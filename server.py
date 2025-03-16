from concurrent import futures
import sys

import grpc
import heartbeat_pb2_grpc
import bank_pb2_grpc
import log_pb2_grpc

from heartbeat_pb2 import HeartbeatResponse, HeartbeatRequest, VoteRequest, VoteResponse
from log_pb2 import LogEntry, LogResponse, IndexRequest, IndexResponse
from bank_pb2 import AccountRequest, AccountResponse, BalanceResponse, DepositRequest, WithdrawRequest, InterestRequest, TransactionResponse, HistoryRequest, HistoryResponse

class LogItem:
    def __init__(self, index: int, term: int, command: str):
        self.index = index
        self.term = term
        self.command = command

class BankServer(heartbeat_pb2_grpc.HeartbeatServicer, bank_pb2_grpc.BankServicer, log_pb2_grpc.LoggerServicer):
    """Notes:
    Log replication is done by sending log entries to all backups, and waiting for a majority of them to respond with an ack.
    The primary will then commit the log entry, and send a response to the client.
    
    The primary will also send a heartbeat to all backups.
    When a backup receives a heartbeat, it will not respond.
    If a backup does not receive a heartbeat within a certain time, it will start an election.
    The backup will send a RequestVote to all other servers, and wait for a majority of them to respond.
    If the backup receives a majority of votes, it will become the primary.
    - Review RAFT election algorithms for more details on how election works by comparing log indexes.
    
    """
    
    
    def __init__(self, logFile: str, backups: list, isPrimary: bool):
        self.isPrimary = isPrimary
        self.logFile = logFile
        self.backups = backups
        self.log = []
        
    # Bank methods
    def CreateAccount(self, request, context):
        #TODO: Implement CreateAccount
        return super().CreateAccount(request, context)
    
    def GetBalance(self, request, context):
        #TODO: Implement GetBalance
        return super().GetBalance(request, context)
    
    def Deposit(self, request, context):
        #TODO: Implement Deposit
        return super().Deposit(request, context)
    
    def Withdraw(self, request, context):
        #TODO: Implement Withdraw
        return super().Withdraw(request, context)
    
    def CalculateInterest(self, request, context):
        #TODO: Implement CalculateInterest
        return super().CalculateInterest(request, context)
    
    def GetHistory(self, request, context):
        #TODO: Implement GetHistory
        return super().GetHistory(request, context)
    
    # Heartbeat/Election methods
    def Heartbeat(self, request, context):
        #TODO: Implement Heartbeat
        return super().Heartbeat(request, context)
    
    def RequestVote(self, request, context):
        #TODO: Implement RequestVote
        return super().RequestVote(request, context)
    
    # Log methods
    def WriteLog(self, request, context):
        #TODO: Implement WriteLog - with log replication
        return super().WriteLog(request, context)
    
    def RetrieveIndex(self, request, context):
        #TODO: Implement RetrieveIndex - get next index for log replication
        return super().RetrieveIndex(request, context)
    
    def TryLog(self, logItem: LogItem) -> bool:
        """This is a wrapper for the log replication process.
        It will send a WriteLog request to all backups, and wait for a majority of them to respond.
        If a majority of them respond, it will return True.
        Otherwise, it will return False
        - When it returns False, the primary should not commit the log entry and should retry.
        - After a retry, if the primary still cannot commit the log entry, it should fail the request.

        Args:
            logItem (LogItem): The log item we want to replicate

        Returns:
            bool: Is the log item replicated successfully?
        """
        
    
    
def serve():
    # Command line configs
    if len(sys.argv) < 3:
        print("Usage: python server.py <port> [primary|backup] <backup1> <backup2> <...>")
        sys.exit(1)
    role = sys.argv[2]
    if role not in ["primary", "backup"]:
        print("Usage: python server.py [primary|backup]")
        sys.exit(1)
    else:
        isPrimary = role == "primary"
        
    backups = []
    if len(sys.argv) > 3:
        backups = sys.argv[2:]
        
    port = sys.argv[1]
    
    
    # Server configuration
    logFile = f'{port}-log.txt'
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    primary = BankServer(logFile, backups, isPrimary)
    
    # GRPC server setup
    heartbeat_pb2_grpc.add_HeartbeatServicer_to_server(primary, server)
    bank_pb2_grpc.add_BankServicer_to_server(primary, server)
    log_pb2_grpc.add_LoggerServicer_to_server(primary, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    # Server Loop
    print(f"Server started on port {port}, as primary")
    server.wait_for_termination()
    
if __name__ == '__main__':
    serve()