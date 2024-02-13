from utils import *
class Blockchain:
    def __init__(self):
        # initialize every blockchain with a copy of genesis block
        # pointer to genesis block in this blockchain
        self.genesis = G.global_genesis.clone()
        # pointer to the last block in the blockchain
        self.current_block = self.genesis

    # add block to the children of its parent block in the blockchain
    def add(self, block):
        assert block.parent is not None
        block.parent.next.append(block)

    # returns the parent while updating the balances array and storing the transactions
    def backward(self, b, balances, txns):  # Block, list, list
        # used when the longest branch changes to some other branch
        # equivalent to rolling back the addition of block b
        global MINING_FEE
        for txn in b.txns:
            balances[txn.sender.id] += txn.amount
            balances[txn.receiver.id] -= txn.amount
            txns.append(txn)
        balances[b.owner.id] -= MINING_FEE
        return b.parent


# Example usage:
# blockchain = Blockchain()
# block = some_block_object
# blockchain.add(block)
# balances = [0, 0, 0]  # Assuming there are 3 peers
# txns = []
# new_block = blockchain.backward(block, balances, txns)
