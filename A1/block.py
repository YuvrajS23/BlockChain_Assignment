class Block:
    max_size = 0
    counter = 0
    TRANSACTION_SIZE = 1  # Assuming TRANSACTION_SIZE is a constant

    def __init__(self, owner):
        self.owner = owner
        self.parent = None
        self.parent_id = -1
        self.depth = -1
        self.size = 1  # block size with coinbase = 1 KB
        self.id = -1
        self.txns = []

    def set_id(self):
        self.id = Block.counter
        Block.counter += 1

    def add(self, txn):
        self.txns.append(txn)
        self.size += Block.TRANSACTION_SIZE  # size of every txn = 1 KB

    def get_name(self):
        return "Blk" + str(self.id + 1)

    def clone(self):
        ret = Block(self.owner)
        ret.__dict__ = self.__dict__.copy()
        ret.reset_parent()
        ret.next = []
        return ret

    def set_parent(self, b):
        self.parent = b
        # b == None indicates genesis block
        self.parent_id = -2 if b is None else b.id
        self.depth = 0 if b is None else b.depth + 1

    def reset_parent(self):
        self.parent = None
        self.depth = -1


# Example usage:
# owner_ = some_owner_object
# block = Block(owner_)
# block.set_id()
# txn = some_transaction_object
# block.add(txn)
# print(block.get_name())
