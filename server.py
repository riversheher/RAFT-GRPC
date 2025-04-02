from concurrent import futures
import sys
import grpc
import heartbeat_pb2
import heartbeat_pb2_grpc
import bank_pb2_grpc
import log_pb2_grpc
import time
import threading
import logging

HEARTBEAT_INTERVAL = 5  # Heartbeat interval in seconds
ELECTION_TIMEOUT = 10   # Timeout before starting election

from log_pb2 import LogEntry, LogResponse
from bank_pb2 import AccountRequest, AccountResponse, BalanceResponse, DepositRequest, WithdrawRequest, InterestRequest, TransactionResponse, HistoryRequest, HistoryResponse

# configure logging message
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class LogItem:
    def __init__(self, index: int, term: int, command: str):
        self.index = index
        self.term = term
        self.command = command


class BankServer(heartbeat_pb2_grpc.HeartbeatServicer, bank_pb2_grpc.BankServicer, log_pb2_grpc.LoggerServicer):
    # set up a server node
    def __init__(self, logFile: str, backups: list, isPrimary: bool, node_id):
        self.isPrimary = isPrimary
        self.logFile = logFile
        self.backups = backups
        self.log = []
        self.next_index = 0
        self.term = 0     # track the current term in RAFT system
        self.node_id = node_id
        self.voted_for = None
        self.votes_received = 0    # track votes received during an election
        self.heartbeat_received = False      # indicate if a heartbeat received from the leader
        self.lock = threading.Lock()
        self.heartbeat_event = threading.Event()        # synchronizes heartbeat handling
        self.old_primary = None        # stores the previous leader
        self.in_election = False       # indicates if the node is currently in election

        # Bank attributes
        # key: account_id, value: balance
        self.accounts = {}
        # key: account_id, value: list of transactions
        self.transaction_history = {}
        
        if self.isPrimary:
            self.old_primary = node_id
            # start a background thread for sending heartbeats
            threading.Thread(target=self.send_heartbeats, daemon=True).start()
        else:
            # if the node is follower monitor heartbeats
            threading.Thread(target=self.monitor_heartbeat, daemon=True).start()

    def send_heartbeats(self):
        try:
            logging.info("send_heartbeats started")
            while self.isPrimary:
                logging.info(f"Heartbeat sent from primary (term: {self.term})")
                for backup in self.backups:
                    if backup != self.node_id:
                        try:
                            # create a gRPC communication channel to the follower
                            channel = grpc.insecure_channel(f'localhost:{backup}')
                            stub = heartbeat_pb2_grpc.HeartbeatStub(channel)
                            request = heartbeat_pb2.HeartbeatRequest(
                                service_identifier="leader",
                                term=self.term,
                                log_index=self.log[-1].index if self.log else -1,
                                log_term=self.term
                            )
                            response = stub.Heartbeat(request)
                            logging.info(f"Heartbeat response from backup {backup}: {response}")
                        except grpc.RpcError as e:
                            logging.error(f"Failed to send heartbeat to backup {backup}")
                            continue
                time.sleep(HEARTBEAT_INTERVAL)
        except Exception as e:
            logging.error(f"send_heartbeats encountered an error: {e}")

    # updates the leader status
    def update_primary_status(self, new_primary_status):
        with self.lock:
            self.isPrimary = new_primary_status
            if new_primary_status:
                self.heartbeat_event.set()  # Signal heartbeat thread to continue
            else:
                self.heartbeat_event.clear()  # Stop the heartbeat thread

    # detect if the leader is still active
    def monitor_heartbeat(self):
        while not self.isPrimary:
            time.sleep(ELECTION_TIMEOUT)
            if not self.heartbeat_received:
                logging.info(f"No heartbeat received. Starting election for term {self.term}")
                threading.Thread(target=self.start_election, daemon=True).start()
            self.heartbeat_received = False

    # process incoming heartbeats
    def Heartbeat(self, request, context):
        with self.lock:
            if request.term >= self.term:
                self.term = request.term
                self.heartbeat_received = True
        logging.info(f"Heartbeat received from primary (term: {request.term})")
        return heartbeat_pb2.HeartbeatResponse(success=True, term=self.term)

    def start_election(self):
        logging.info("Attempting to acquire lock for election")
        if not self.lock.acquire(blocking=False):
            logging.info("Election already in progress, skipping.")
            return

        try:
            # election initialization
            self.term += 1
            self.voted_for = self.node_id
            self.votes_received = 1  # vote for self
            logging.info(f"Starting election for term {self.term}")

            threads = []

            # Send gRPC vote requests to all backup nodes
            def request_vote_from_backup(backup):
                if backup == self.node_id:
                    return
                try:
                    channel = grpc.insecure_channel(f'localhost:{backup}')
                    stub = heartbeat_pb2_grpc.HeartbeatStub(channel)
                    request = heartbeat_pb2.VoteRequest(
                        term=self.term,
                        candidate_id=self.node_id,
                        last_log_index=self.log[-1].index if self.log else -1,
                        last_log_term=self.term
                    )
                    response = stub.RequestVote(request, timeout=5)
                    if response.vote_granted:
                        self.votes_received += 1
                except grpc.RpcError:
                    pass

            # Each vote request runs in parallel to avoid delays.
            for backup in self.backups:
                thread = threading.Thread(target=request_vote_from_backup, args=(backup,))
                threads.append(thread)
                thread.start()

            # ensure all voting requests have been processed before deciding the election outcome
            for thread in threads:
                thread.join()

            # if the node gets more than half the votes, it becomes primary.
            if self.votes_received > len(self.backups) // 2:
                self.isPrimary = True
                self.old_primary = self.node_id
                self.backups = [b for b in self.backups if b != self.node_id]   # remove leader from backup list

                logging.info(f"Election won! Node {self.node_id} becomes primary for term {self.term}")
                threading.Thread(target=self.send_heartbeats, daemon=True).start()
            else:
                logging.warning(f"Election failed for term {self.term}")

        finally:
            self.lock.release()     # release lock after election

    # schedules a retry for the election after a certain delay
    def schedule_election_retry(self):
        retry_delay = 5
        threading.Timer(retry_delay, self.start_election).start()

    # stop the server and transition its status from "primary" to "not primary."
    def stop_server(self):
        with self.lock:
            self.update_primary_status(False)
        logging.info("Server stopped.")


    def RequestVote(self, request, context):
        with self.lock:
            # if the candidate's term is greater than the current term, update term and grant vote
            if request.term > self.term:
                self.term = request.term
                self.voted_for = request.candidate_id
                return heartbeat_pb2.VoteResponse(term=self.term, vote_granted=True)

            # if the candidate's term is the same as the current term, check voting conditions
            if request.term == self.term:
                # if the node has already voted for someone else, deny the vote
                if self.voted_for and self.voted_for != request.candidate_id:
                    return heartbeat_pb2.VoteResponse(term=self.term, vote_granted=False)

                # check the logs to decide if the node should grant the vote
                last_log_index = self.log[-1].index if self.log else -1
                last_log_term = self.log[-1]['term'] if self.log else 0
                # if the candidate's log is less up-to-date, deny the vote
                if (request.last_log_term < last_log_term) or \
                        (request.last_log_term == last_log_term and request.last_log_index < last_log_index):
                    return heartbeat_pb2.VoteResponse(term=self.term, vote_granted=False)

                # if the candidate's log is sufficiently up-to-date, grant the vote
                self.voted_for = request.candidate_id
                return heartbeat_pb2.VoteResponse(term=self.term, vote_granted=True)

            # if the candidate's term is less than the current term, deny the vote
            return heartbeat_pb2.VoteResponse(term=self.term, vote_granted=False)

    #TODO: Bank methods
    def CreateAccount(self, request, context):
        if request.account_id in self.accounts:
            return AccountResponse(account_id=request.account_id, message="Account already exists.")
        self.accounts[request.account_id] = 0.0
        self.transaction_history[request.account_id] = []
        return AccountResponse(account_id=request.account_id, message="Account created successfully.")

    def GetBalance(self, request, context):
        balance = self.accounts.get(request.account_id)
        if balance is None:
            return BalanceResponse(account_id=request.account_id, balance=0.0, message="Account not found.")
        return BalanceResponse(account_id=request.account_id, balance=balance,
                               message="Balance retrieved successfully.")

    def Deposit(self, request, context):
        if request.account_id not in self.accounts:
            return TransactionResponse(account_id=request.account_id, message="Account not found.", balance=0.0)
        self.accounts[request.account_id] += request.amount
        
        # create a log item for the deposit
        logItem = LogItem(index=self.next_index, term=self.term, command=f"Account {request.account_id} - Deposit: {request.amount}")
        # try to replicate the log
        if not self.TryLog(logItem):
            return TransactionResponse(account_id=request.account_id, message="Deposit failed, try again later", balance=self.accounts[request.account_id])
        
        # Append the transaction to the transaction history
        self.transaction_history[request.account_id].append(
            TransactionResponse(account_id=request.account_id, message=f"Deposit: {request.amount}",
                                balance=self.accounts[request.account_id]))
        
        return TransactionResponse(account_id=request.account_id, message="Deposit successful.",
                                   balance=self.accounts[request.account_id])

    def Withdraw(self, request, context):
        if request.account_id not in self.accounts:
            return TransactionResponse(account_id=request.account_id, message="Account not found.", balance=0.0)
        if self.accounts[request.account_id] < request.amount:
            return TransactionResponse(account_id=request.account_id, message="Insufficient funds.",
                                       balance=self.accounts[request.account_id])
        self.accounts[request.account_id] -= request.amount
        
        #create a log item for the withdrawal
        logItem = LogItem(index=self.next_index, term=self.term, command=f"Account {request.account_id} - Withdraw: {request.amount}")
        # try to replicate the log
        if not self.TryLog(logItem):
            return TransactionResponse(account_id=request.account_id, message="Withdrawal failed, try again later", balance=self.accounts[request.account_id])
        
        # Append the transaction to the transaction history
        self.transaction_history[request.account_id].append(
            TransactionResponse(account_id=request.account_id, message=f"Withdraw: {request.amount}",
                                balance=self.accounts[request.account_id]))
        
        return TransactionResponse(account_id=request.account_id, message="Withdrawal successful.",
                                   balance=self.accounts[request.account_id])

    def CalculateInterest(self, request, context):
        if request.account_id not in self.accounts:
            return TransactionResponse(account_id=request.account_id, message="Account not found.", balance=0.0)
        interest = self.accounts[request.account_id] * request.annual_interest_rate / 100
        self.accounts[request.account_id] += interest
        
        #create a log item for the interest
        logItem = LogItem(index=self.next_index, term=self.term, command=f"Account {request.account_id} - Interest: {interest}")
        if not self.TryLog(logItem):
            return TransactionResponse(account_id=request.account_id, message="Interest calculation failed, try again later", balance=self.accounts[request.account_id])
        
        # Append the transaction to the transaction history
        self.transaction_history[request.account_id].append(
            TransactionResponse(account_id=request.account_id, message=f"Interest Applied: {interest}",
                                balance=self.accounts[request.account_id]))
        
        return TransactionResponse(account_id=request.account_id, message=f"Interest applied: {interest}",
                                   balance=self.accounts[request.account_id])

    def GetHistory(self, request, context):
        if request.account_id not in self.transaction_history:
            return HistoryResponse(account_id=request.account_id, transactions=[])
        return HistoryResponse(account_id=request.account_id, transactions=self.transaction_history[request.account_id])

    #TODO: Log methods
    def WriteLog(self, request, context):
        #Get the log term and index
        log_index = request.index
        log_term = request.term
        
        if (self.isPrimary):
            #return true in this case since the primary should always be able to write to its own log
            #primary will write to its own log in the TryLog method, after majority of backups have replicated the log
            return LogResponse(ack=True, term=self.term)
        
        # If the log index is greater than the next index, return a negative log response
        # The leader should now try sending a lower index until it matches the follower
        # Unsucessful case
        if (log_index > self.next_index):
            return LogResponse(ack=False, term=self.term)
        
        # If the log index is less than the current term, delete the log entry until it matches leader
        # Sucessful case
        elif (log_index < self.next_index):
            del self.log[log_index:]
            self.next_index = log_index
            # Return a positive log response
            return LogResponse(ack=True, term=self.term)           
        
        # If the log index is the same as the next index, append the log entry
        # Sucessful case
        else:
            entry = LogItem(index=log_index, term=log_term, command=request.command)
            self.log.append(entry)
            self.next_index += 1
            self.term = log_term
            # Return a positive log response
            return LogResponse(ack=True, term=self.term)
        

    def TryLog(self, logItem: LogItem) -> bool:
        """This is a wrapper for the log replication process.
        It will send a WriteLog request to all backups, and wait for a majority of them to respond.
        If a majority of them respond, it will return True.
        Otherwise, it will return False
        - When it returns False, the primary should not commit the log entry and should retry.
        - After a retry, if the primary still cannot commit the log entry, it should fail the request.

        Args:
            logItem (LogItem): The log item we want to replicate

    #     Returns:
    #         bool: Is the log item replicated successfully?
    #     """
    
        # create a dictionary for each backup, their next index, and if they have successfully replicated the log
        backup_status = {}
        for backup in self.backups:
            backup_status[backup] = {
                "next_index": self.next_index,
                "success": False
            }
            
        # boolean to keep track of the state of the log replication
        replicated = False
        
        for backup in self.backups:
            try:
                # create a gRPC communication channel to the follower
                channel = grpc.insecure_channel(f'localhost:{backup}')
                stub = log_pb2_grpc.LoggerStub(channel)
                request = LogEntry(
                    index=logItem.index,
                    term=logItem.term,
                    command=logItem.command
                )
                response = stub.WriteLog(request)
                
                # if the log is successfully replicated, update the status
                if response.ack:
                    backup_status[backup]["success"] = True
                else:
                    # if the log is not successfully replicated, update the next index
                    backup_status[backup]["next_index"] = response.index
                    
                    # send logs with the next index to the backup until it catches up
                    while backup_status[backup]["next_index"] < self.next_index:
                        request = LogEntry(
                            index=backup_status[backup]["next_index"],
                            term=self.log[backup_status[backup]["next_index"]].term,
                            command=self.log[backup_status[backup]["next_index"]].command
                        )
                        response = stub.WriteLog(request)
                        if response.ack:
                            backup_status[backup]["next_index"] += 1
                        else:
                            break
                        
                    # if after the while loop the backup has caught up, update the status
                    if backup_status[backup]["next_index"] == self.next_index:
                        backup_status[backup]["success"] = True
                    # if the backup has not caught up, continue to the next backup, and do not update the status to success
                        
            except grpc.RpcError as e:
                # if backup fails for some reason, skip it and continue to the next backup
                logging.error(f"Failed to send log entry to backup {backup}")
                continue
                
            # check if a majority of the backups have successfully replicated the log
            success_count = sum([1 for status in backup_status.values() if status["success"]])
            if success_count > len(self.backups) // 2:
                replicated = True
                
                # Write log to primary's own log
                self.log.append(logItem)
                self.next_index += 1
        
        
        
        
        return replicated


def serve():
    if len(sys.argv) < 3:
        print("Usage: python server.py <port> [primary|backup] <backup1> <backup2> <...>")
        sys.exit(1)
    role = sys.argv[2]
    port = sys.argv[1]

    if role not in ["primary", "backup"]:
        print("Usage: python server.py [primary|backup]")
        sys.exit(1)

    isPrimary = role == "primary"
    backups = sys.argv[3:]

    logFile = f'{port}-log.txt'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    primary = BankServer(logFile, backups, isPrimary, port)

    heartbeat_pb2_grpc.add_HeartbeatServicer_to_server(primary, server)
    bank_pb2_grpc.add_BankServicer_to_server(primary, server)
    log_pb2_grpc.add_LoggerServicer_to_server(primary, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()

    logging.info(f"Server started on port {port}, as {role}")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
