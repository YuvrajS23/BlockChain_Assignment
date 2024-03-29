from utils import *
# Class for block
class Block:
    def __init__(self, owner):
        self.owner = owner  # peer who mined this block
        self.parent = None  # pointer to parent block
        self.parent_id = -1 # id of parent block
        self.depth = -1     # depth: block_num
        self.size = 1  # block size with coinbase = 1 KB
        self.id = -1    # id: BlkID
        self.next = []  # list of children blocks
        self.txns = []  # txns in this block

    # set id for this block and increment static counter
    def setID(self):
        self.id = G.blk_counter
        G.blk_counter += 1

    # add txn in this block
    def add(self, txn):
        self.txns.append(txn)
        self.size += G.TRANSACTION_SIZE  # size of every txn = 1 KB

    # return name of current block
    def getName(self):
        return "Blk" + str(self.id + 1)

    # return a copy of this block
    def clone(self):
        ret = Block(self.owner)
        ret.size = self.size
        ret.id = self.id
        ret.txns = self.txns[:]
        ret.parent_id = self.parent_id
        ret.resetParent()
        ret.next = []
        return ret

    # set parent of this block to b
    def setParent(self, b):
        self.parent = b
        # b == None indicates genesis block
        self.parent_id = -2 if b is None else b.id
        self.depth = 0 if b is None else b.depth + 1

    # set parent pointer to None
    def resetParent(self):
        self.parent = None
        self.depth = -1

