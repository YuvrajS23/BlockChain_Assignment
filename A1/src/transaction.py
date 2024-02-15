from utils import *

class Transaction:
    def __init__(self, timestamp, sender, receiver, coins):
        # id: unique txn id
        self.id = G.txn_counter # int
        G.txn_counter += 1
        # coins transferred from sender to receiver
        self.sender = sender    # Peer
        self.receiver = receiver    # Peer
        # amount: no of coins
        self.amount = coins # int
        # timestamp at which txn was created
        self.timestamp = timestamp

    # Return the id of the transaction as a string
    def get_name(self):
        return "Txn" + str(self.id + 1)