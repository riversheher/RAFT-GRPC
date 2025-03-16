import grpc
import sys

from bank_pb2 import AccountRequest, DepositRequest, WithdrawRequest, InterestRequest, HistoryRequest
from bank_pb2_grpc import BankStub

def create_account(stub: BankStub, account_id: str, account_type: str) -> str:
    request = AccountRequest(account_id=account_id, account_type=account_type)
    response = stub.CreateAccount(request)
    return response.message

def deposit(stub: BankStub, account_id: str, amount: float) -> str:
    return "not implemented"

def withdraw(stub: BankStub, account_id: str, amount: float) -> str:
    return "not implemented"

def balance(stub: BankStub, account_id: str) -> str:
    return "not implemented"

def calculate_interest(stub: BankStub, account_id: str, annual_interest_rate: float) -> str:
    return "not implemented"

def get_history(stub: BankStub, account_id: str) -> str:
    return "not implemented"

def run():
    if len(sys.argv) < 2:
        print("Usage: python client.py <command>")
        print("Commands: account, deposit, withdraw, balance, interest, history")
        print('''
              Usage:
                python client.py account <account_id> <account_type>
                python client.py deposit <account_id> <amount>
                python client.py withdraw <account_id> <amount>
                python client.py balance <account_id>
                python client.py interest <account_id> <annual_interest_rate>
                python client.py history <account_id>
              ''')
        sys.exit(1)
        
    channel = grpc.insecure_channel('localhost:50051')
    stub = BankStub(channel)
    
    match sys.argv[1]:
        case "account":
            if len(sys.argv) != 4:
                print("Usage: python client.py account <account_id> <account_type>")
                sys.exit(1)
            account_id = sys.argv[2]
            account_type = sys.argv[3]
            print(create_account(stub, account_id, account_type))
        case "deposit":
            if len(sys.argv) != 4:
                print("Usage: python client.py deposit <account_id> <amount>")
                sys.exit(1)
            account_id = sys.argv[2]
            amount = float(sys.argv[3])
            print(deposit(stub, account_id, amount))
        case "withdraw":
            if len(sys.argv) != 4:
                print("Usage: python client.py withdraw <account_id> <amount>")
                sys.exit(1)
            account_id = sys.argv[2]
            amount = float(sys.argv[3])
            print(withdraw(stub, account_id, amount))
        case "balance":
            if len(sys.argv) != 3:
                print("Usage: python client.py balance <account_id>")
                sys.exit(1)
            account_id = sys.argv[2]
            print(balance(stub, account_id))
        case "interest":
            if len(sys.argv) != 4:
                print("Usage: python client.py interest <account_id> <annual_interest_rate>")
                sys.exit(1)
            account_id = sys.argv[2]
            annual_interest_rate = float(sys.argv[3])
            print(calculate_interest(stub, account_id, annual_interest_rate))
        case "history":
            if len(sys.argv) != 3:
                print("Usage: python client.py history <account_id>")
                sys.exit(1)
            account_id = sys.argv[2]
            print(get_history(stub, account_id))
        case _:
            print("Invalid command")
            print("Usage: python client.py <command>")
            print("Commands: account, deposit, withdraw, balance, interest, history")
            print('''
              Usage:
                python client.py account <account_id> <account_type>
                python client.py deposit <account_id> <amount>
                python client.py withdraw <account_id> <amount>
                python client.py balance <account_id>
                python client.py interest <account_id> <annual_interest_rate>
                python client.py history <account_id>
              ''')
            sys.exit(1)
    