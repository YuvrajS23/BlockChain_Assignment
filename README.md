# BlockChain_Assignment
By
- Khushi Gondane (210050056)
- Yuvraj Singh (210050172)
- Shrey Modi (200020135)

### Command for running
> python3 main.py -n 'numpeers' -z0 '%slowpeers' -z1 '%lowhashpeers' -t 'time_limit' -Ttx 'txn_interarrival_time' -Tk 'mining_time' -s 'seed' -txn 'max_txns' -blk 'max_blks' -v -it 'prob_invalid_txns' -ib 'prob_invalid_blks'


### Sample Command
> python3 -n 30 -z0 0.5 -z1 0.3 -t 3000 -Ttx 40 -Tk 40 -s 42 -txn 0 -blk 102 -v -it 0.05 -ib 0.01

### Flags Usage
> - --peers PEERS, -n PEERS -> Number of peers in the network
>  - --slowpeers SLOWPEERS, -z0 SLOWPEERS -> Fraction of slow peers in the network
> - --lowhashpower LOWHASHPOWER, -z1 LOWHASHPOWER -> Fraction of slow peers in the network
> - --time_limit TIME_LIMIT, -t TIME_LIMIT -> Run the simulation up to a time limit (in seconds)
> - --txn_interarrival TXN_INTERARRIVAL, -Ttx TXN_INTERARRIVAL -> Mean of exponential distribution of interarrival time between transactions
> - --mining_time MINING_TIME, -Tk MINING_TIME -> Mean of exponential distribution of time to mine a block
> - --seed SEED, -s SEED -> Seed for random number generator
> - --max_txns MAX_TXNS, -txn MAX_TXNS -> Run simulation till max transactions are generated, 0 indicates infinity
> - --max_blocks MAX_BLOCKS, -blk MAX_BLOCKS -> Run simulation till max blocks are generated, 0 indicates infinity
> - --verbose, -v -> Print output log
> - --invalid_txn_prob INVALID_TXN_PROB, -it INVALID_TXN_PROB -> Probability of generating an invalid transaction
> - --invalid_block_prob INVALID_BLOCK_PROB, -ib INVALID_BLOCK_PROB -> Probability of generating an invalid block

### Packages needed
- python3 version 3.10 or above
- To install, run the following commands in sequence
> sudo apt update && sudo apt upgrade -y
> sudo apt install python3 