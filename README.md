1. Initialize venv:
`virtualenv venv`

`source venv/bin/activate`

2. Install requirements:
`pip install grpcio`
`pip install grpcio-tools`

3. Generate Proto Files:
`./start.sh`


bank.proto provides the protocols related to the bank functionality.

heartbeat.proto provides the protocols related to heartbeats, and for leader election.

log.proto provides the protocols for logging, and reconciliation.

# Usage

To start a server instance, the following command is required:

`python server.py <server_port> <primary|backup> <server_port> <backup1> <backup2> <...>`

An example of this command can be found below:

`python server.py 50051 primary 50051 50052 50053`

This tells the server to start as the primary initially, with servers with port 50051, 50052, and 50053 in its cloud.  It is important to include itself in this list.

A backup can be started with:

`python server.py 50052 backup 50051 50052 50053`

This tells the server to start as the backup in the cloud including servers with port 50051, 50052, and 50053.

Next, start the client with:

`python client.py 50051`

The client will now start pointing to the server 50051 as the primary, and you can follow instructions on how to perform actions on the server.

## Client Actions

The following commands are supported by the client: 

- account <account_id> <account_type>
  - Creates an account
  - Valid account types are 'savings' and 'chequing'
- deposit <account_id> <amount>
  - deposits money to an account
- withdraw <account_id> <amount>
  - withdraws money to an account
- balance <account_id>
  - checks balance of account
- interest <account_id> <annual_interest_rate>
  - calculates and deposits interest to account
- history <account_id>
  - checks transaction history

