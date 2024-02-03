class Blockchain:
    global_genesis = None
    MINING_FEE = 0  # Assuming MINING_FEE is a constant

    def __init__(self):
        # initialize every blockchain with a copy of genesis block
        self.genesis = Blockchain.global_genesis.clone()
        self.current_block = self.genesis

    def add(self, block):
        assert block.parent is not None
        block.parent.next.append(block)

    def backward(self, b, balances, txns):
        # used when the longest branch changes to some other branch
        # equivalent to rolling back the addition of block b
        for txn in b.txns:
            balances[txn.sender.id] += txn.amount
            balances[txn.receiver.id] -= txn.amount
            txns.append(txn)
        balances[b.owner.id] -= Blockchain.MINING_FEE
        return b.parent


# Example usage:
# blockchain = Blockchain()
# block = some_block_object
# blockchain.add(block)
# balances = [0, 0, 0]  # Assuming there are 3 peers
# txns = []
# new_block = blockchain.backward(block, balances, txns)
