import argparse
import random
import os
from math import isclose
from enum import Enum
from itertools import cycle
from simulator import *

# Seed for random number generator
seed = 42
random.seed(seed)

# Create ArgumentParser
argparser = argparse.ArgumentParser(description="./blockchain_simulator 1.0")

# Add arguments
argparser.add_argument("--peers", "-n", default=40, type=int, required=True,
                       help="Number of peers in the network")

argparser.add_argument("--edges", "-e", default=150, type=int, required=True,
                       help="Number of edges in the peer network")

argparser.add_argument("--slowpeers", "-z", default=0.4, type=float, required=True,
                       help="Fraction of slow peers in the network")

argparser.add_argument("--time_limit", "-t", default=float('inf'), type=float, required=True,
                       help="Run the simulation up to a time limit (in seconds)")

argparser.add_argument("--txn_interarrival", "-Ttx", default=40, type=float, required=True,
                       help="Mean of exponential distribution of interarrival time between transactions")

argparser.add_argument("--mining_time", "-Tk", default=1000.0, type=float, required=True,
                       help="Mean of exponential distribution of time to mine a block")

argparser.add_argument("--seed", "-s", default=seed, type=int, required=True,
                       help="Seed for random number generator")

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

argparser.add_argument("--attacker_connection", "-zeta", default=0.5, type=float,
                       help="Fraction of honest nodes adversary is connected to")

argparser.add_argument("--alpha", "-a", default=0.35, type=float,
                       help="Fraction of hash power belonging to attacker")

argparser.add_argument("--adversary_type", "-adv", default="none", type=str,
                       choices=["none", "selfish", "stubborn"],
                       help="Type of adversary, choose from (none, selfish, stubborn)")

# Parse arguments
args = argparser.parse_args()

# Extract arguments
n = args.peers
edges = args.edges
z = args.slowpeers
t = args.time_limit
Ttx = args.txn_interarrival
Tk = args.mining_time
seed = args.seed
max_txns = args.max_txns
max_blocks = args.max_blocks
verbose = args.verbose
invalid_txn_prob = args.invalid_txn_prob
invalid_block_prob = args.invalid_block_prob
zeta = args.attacker_connection
alpha = args.alpha
adv = args.adversary_type

# Set random seed
random.seed(seed)

# Create Simulator instance and run simulation
simulator = Simulator(n, z, Ttx, Tk, edges, verbose, invalid_txn_prob, invalid_block_prob, zeta, adv, alpha)
simulator.run(t, max_txns, max_blocks)
