# Class of Global Variables to be used across files
class G:
    # Ttx: mean interarrival time b/n txns generated by peer
    Ttx = 0
    # Tk: mean mining time of a block
    Tk = 0

    LOW_HASH_POWER = 0.1
    HIGH_HASH_POWER = 1

    # Assuming TRANSACTION_SIZE is a constant
    TRANSACTION_SIZE = 1
    # Assuming MINING_FEE is a constant
    MINING_FEE = 0
    # max allowed size for a block in KB
    max_size = 1024

    # pointer to the genesis block
    global_genesis = None   # Block

    START_TIME = 0.0
    MAX_BLOCK_SIZE = 1000
    DBL_MAX = float('inf')
    INT_MAX = float('inf')

    # a static variable for unique txn id, incremented on every new txn
    txn_counter = 0
    # a static variable for unique peer id, incremented on every new peer
    peer_counter = 0
    # a static variable for unique block id, incremented on every new block
    blk_counter = 0

    # total no of peers in the network
    total_peers = 0
    # List of all peers in the network
    peers = []