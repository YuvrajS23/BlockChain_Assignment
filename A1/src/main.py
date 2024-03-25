import argparse
import random
from simulator import *

# Seed for random number generator
# seed = 42
# random.seed(seed)

# Create ArgumentParser
argparser = argparse.ArgumentParser(description="BlockChain Simulator")

# Add arguments
argparser.add_argument("--peers", "-n", default=40, type=int, required=True,
                       help="Number of peers in the network")

argparser.add_argument("--slowpeers", "-z0", default=0.4, type=float, required=True,
                       help="Fraction of slow peers in the network")

argparser.add_argument("--lowhashpower", "-z1", default=0.4, type=float, required=True,
                       help="Fraction of low hash power peers in the network")

argparser.add_argument("--time_limit", "-t", default=float('inf'), type=float, required=True,
                       help="Run the simulation up to a time limit (in seconds)")

argparser.add_argument("--txn_interarrival", "-Ttx", default=40, type=float, required=True,
                       help="Mean of exponential distribution of interarrival time between transactions")

argparser.add_argument("--mining_time", "-Tk", default=1000.0, type=float, required=True,
                       help="Mean of exponential distribution of time to mine a block")

argparser.add_argument("--max_txns", "-txn", default=0, type=int, required=True,
                       help="Run simulation till max transactions are generated, 0 indicates infinity")

argparser.add_argument("--max_blocks", "-blk", default=100, type=int, required=True,
                       help="Run simulation till max blocks are generated, 0 indicates infinity")

argparser.add_argument("--verbose", "-v", action="store_true",
                       help="Print output log")

argparser.add_argument("--invalid_txn_prob", "-it", default=0.05, type=float, required=True,
                       help="Probability of generating an invalid transaction")

argparser.add_argument("--invalid_block_prob", "-ib", default=0.05, type=float, required=True,
                       help="Probability of generating an invalid block")

argparser.add_argument("--alpha1", "-a1", default=0.30, type=float, required=True,
                       help="Fraction of hash power belonging to attacker 1")

argparser.add_argument("--alpha2", "-a2", default=0.30, type=float, required=True,
                       help="Fraction of hash power belonging to attacker 2")

# Parse arguments
args = argparser.parse_args()

# Extract arguments
n = args.peers
z0 = args.slowpeers
z1 = args.lowhashpower
t = args.time_limit
Ttx = args.txn_interarrival
Tk = args.mining_time
max_txns = args.max_txns
max_blocks = args.max_blocks
verbose = args.verbose
invalid_txn_prob = args.invalid_txn_prob
invalid_block_prob = args.invalid_block_prob
alpha1 = args.alpha1
alpha2 = args.alpha2


# Create Simulator instance and run simulation
simulator = Simulator(n, z0, z1, Ttx, Tk, verbose, invalid_txn_prob, invalid_block_prob, alpha1, alpha2)
simulator.run(t, max_txns, max_blocks)
