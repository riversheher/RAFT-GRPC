from concurrent import futures
import logging
import grpc
import sys

import bank_pb2
from bank_pb2 import AccountRequest, DepositRequest, WithdrawRequest, InterestRequest, HistoryRequest
from bank_pb2_grpc import BankStub

from client_pb2_grpc import ClientStub, ClientServicer, add_ClientServicer_to_server
from client_pb2 import UpdatePrimaryRequest, UpdatePrimaryResponse

def create_account(stub: BankStub, account_id: str, account_type: str) -> str:
    request = AccountRequest(account_id=account_id, account_type=account_type)
    response = stub.CreateAccount(request)
    return response.message

def deposit(stub: BankStub, account_id: str, amount: float) -> str:
    request = bank_pb2.DepositRequest(account_id=account_id, amount=amount)
    response = stub.Deposit(request)
    return f"{response.message} New Balance: {response.balance}"


def withdraw(stub: BankStub, account_id: str, amount: float) -> str:
    request = bank_pb2.WithdrawRequest(account_id=account_id, amount=amount)
    response = stub.Withdraw(request)
    return f"{response.message} New Balance: {response.balance}"


def balance(stub: BankStub, account_id: str) -> str:
    request = bank_pb2.AccountRequest(account_id=account_id)
    response = stub.GetBalance(request)
    return response.balance

def calculate_interest(stub: BankStub, account_id: str, annual_interest_rate: float) -> str:
    request = bank_pb2.InterestRequest(account_id=account_id, annual_interest_rate=annual_interest_rate)
    response = stub.CalculateInterest(request)
    return f"{response.message} New Balance: {response.balance}"


def get_history(stub: BankStub, account_id: str) -> str:
    request = bank_pb2.HistoryRequest(account_id=account_id)
    response = stub.GetHistory(request)
    
    history = []
    transaction_num = 0
    for transaction in response.transactions:
        transaction_num += 1
        history.append(f"Account: {transaction.account_id} - Transaction#: {transaction_num} - {transaction.message} - end balance: {transaction.balance}")
        
    return "\n".join(history)
        
        
class ClientServer(ClientServicer):
    def __init__(self, primary_port: str):
        self.primary = primary_port
        
    def UpdatePrimary(self, request, context):
        self.primary = request.port
        return UpdatePrimaryResponse(ack=True)

def run(command: str, server: ClientServer):
    user_input = command.split()
    if len(user_input) == 0:
        print("Invalid command")
        return
        
    channel = grpc.insecure_channel(f'localhost:{server.primary}')
    stub = BankStub(channel)
    
    match user_input[0]:
        case "account":
            if len(user_input) != 3:
                print("Usage: account <account_id> <account_type>\n")
                return
            account_id = user_input[1]
            account_type = user_input[2]
            print(create_account(stub, account_id, account_type))
        case "deposit":
            if len(user_input) != 3:
                print("Usage: deposit <account_id> <amount> \n")
                return
            account_id = user_input[1]
            amount = float(user_input[2])
            print(deposit(stub, account_id, amount))
        case "withdraw":
            if len(user_input) != 3:
                print("Usage: withdraw <account_id> <amount> \n")
                return
            account_id = user_input[1]
            amount = float(user_input[2])
            print(withdraw(stub, account_id, amount))
        case "balance":
            if len(user_input) != 2:
                print("Usage: balance <account_id> \n")
                return
            account_id = user_input[1]
            print(balance(stub, account_id))
        case "interest":
            if len(user_input) != 3:
                print("Usage: interest <account_id> <annual_interest_rate> \n")
                return
            account_id = user_input[1]
            annual_interest_rate = float(user_input[2])
            print(calculate_interest(stub, account_id, annual_interest_rate))
        case "history":
            if len(user_input) != 2:
                print("Usage: history <account_id> \n")
                return
            account_id = user_input[1]
            print(get_history(stub, account_id))
        case _:
            print("Invalid command")
            print("Commands: account, deposit, withdraw, balance, interest, history")
            print('''
              Usage:
                account <account_id> <account_type>
                deposit <account_id> <amount>
                withdraw <account_id> <amount>
                balance <account_id>
                interest <account_id> <annual_interest_rate>
                history <account_id>
              ''')
            sys.exit(1)
    
    
def serve():
    if len(sys.argv) != 2:
        print("Usage: python client.py <primary_port>")
        sys.exit(1)  
    
    primary_port = sys.argv[1]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    client_server = ClientServer(primary_port)
    add_ClientServicer_to_server(client_server, server)
    server.add_insecure_port('[::]:50050')
    server.start()
    
    logging.info("Client server started on port 50050 with primary port: " + primary_port)
    
    while True:
        print('''
              Welcome to the CS4459 ATM! Please enter a command:
                Create a new account: 
                    account <account_id> <account_type>
                
                Deposit to your account: 
                    deposit <account_id> <amount>
                
                Withdraw from your account: 
                    withdraw <account_id> <amount>
                
                Get your account balance:
                    balance <account_id>
                    
                Apply interest to your account:
                    interest <account_id> <annual_interest_rate>
                    
                Get your transaction history:
                    history <account_id>
              ''')
        command = input("Enter command: ")
        run(command, client_server)
        pass
    
if __name__ == '__main__':
    serve()