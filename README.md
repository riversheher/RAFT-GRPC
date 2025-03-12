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