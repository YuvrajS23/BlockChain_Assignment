from utils import *

# Class of transactions
class Transaction:
    def __init__(self, time, s, r, c):
        # id: unique txn id
        self.id = G.txn_counter # int
        G.txn_counter += 1
        # coins transferred from sender to receiver
        self.sender = s    # Peer
        self.receiver = r    # Peer
        # amount: no of coins
        self.amount = c # int
        # timestamp at which txn was created
        self.timestamp = time

    # Return the id of the transaction as a string
    def getName(self):
        return "Txn" + str(self.id + 1)