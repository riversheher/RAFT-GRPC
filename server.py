from concurrent import futures
import sys

import grpc
import heartbeat_pb2_grpc
import bank_pb2_grpc
import log_pb2_grpc

from heartbeat_pb2 import HeartbeatResponse, HeartbeatRequest, VoteRequest, VoteResponse
from log_pb2 import LogEntry, LogResponse, IndexRequest, IndexResponse
from bank_pb2 import AccountRequest, AccountResponse, BalanceResponse, DepositRequest, WithdrawRequest, InterestRequest, TransactionResponse, HistoryRequest, HistoryResponse

class BankServer(heartbeat_pb2_grpc.HeartbeatServicer, bank_pb2_grpc.BankServicer, log_pb2_grpc.LoggerServicer):
    
    def __init__(self, logFile: str, backups: list, isPrimary: bool):
        self.isPrimary = isPrimary
        self.logFile = logFile
        self.backups = backups
        self.log = []
        
def serve():
    # Command line configs
    if len(sys.argv) < 2:
        print("Usage: python server.py [primary|backup] <backup1> <backup2> <...>")
        sys.exit(1)
    role = sys.argv[1]
    if role not in ["primary", "backup"]:
        print("Usage: python server.py [primary|backup]")
        sys.exit(1)
    else:
        isPrimary = role == "primary"
        
    backups = []
    if len(sys.argv) > 2:
        backups = sys.argv[2:]
    
    
    # Server configuration
    port = "50051"
    logFile = "50051-log.txt"
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