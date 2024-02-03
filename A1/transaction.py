class Transaction:
    counter = 0

    def __init__(self, timestamp, sender, receiver, coins):
        self.id = Transaction.counter
        Transaction.counter += 1
        self.sender = sender
        self.receiver = receiver
        self.amount = coins
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
