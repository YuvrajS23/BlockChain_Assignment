from utils import *

class Transaction:
    def __init__(self, timestamp, sender, receiver, coins):
        # id: unique txn id
        global txn_counter
        self.id = txn_counter # int
        txn_counter += 1
        # coins transferred from sender to receiver
        self.sender = sender    # Peer
        self.receiver = receiver    # Peer
        # amount: no of coins
        self.amount = coins # int
        # timestamp at which txn was created
        self.timestamp = timestamp

    def get_name(self):
        return "Txn" + str(self.id + 1)


# Example usage:
# timestamp_ = 123456789
# sender_ = some_sender_object
# receiver_ = some_receiver_object
# coins_ = 10
# txn = Transaction(timestamp_, sender_, receiver_, coins_)
# print(txn.get_name())
