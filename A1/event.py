from typing import Optional

class Event:
    def __init__(self, timestamp):
        self.timestamp = timestamp
        self.is_generate_type_event = False  # default value false

    def __lt__(self, other):
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        else:
            # two different events with the same timestamp should not be considered as equal
            return id(self) < id(other)

    def run(self, sim):
        assert False


class GenerateTransaction(Event):
    def __init__(self, timestamp, payed_by):
        super().__init__(timestamp)
        self.payed_by = payed_by
        self.is_generate_type_event = True

    def run(self, sim):
        txn = self.payed_by.generate_transaction(sim)
        if txn is not None:
            # sim.log(f"{self.payed_by.get_name()} generates and emits transaction {txn.get_name()}")
            pass


class ForwardTransaction(Event):
    def __init__(self, timestamp, peer, source, txn):
        super().__init__(timestamp)
        self.peer = peer
        self.source = source
        self.txn = txn

    def run(self, sim):
        # if self.peer.id != self.source.id:
        #     sim.log(f"{self.peer.get_name()} forwards transaction {self.txn.get_name()} received from {self.source.get_name()}")
        self.peer.forward_transaction(sim, self.source, self.txn)


class ReceiveTransaction(Event):
    def __init__(self, timestamp, sender, receiver, txn):
        super().__init__(timestamp)
        self.sender = sender
        self.receiver = receiver
        self.txn = txn

    def run(self, sim):
        # sim.log(f"{self.receiver.get_name()} receives transaction {self.txn.get_name()} from {self.sender.get_name()}")
        self.receiver.receive_transaction(sim, self.sender, self.txn)


class BroadcastMinedBlock(Event):
    def __init__(self, timestamp, owner):
        super().__init__(timestamp)
        self.owner = owner
        self.is_generate_type_event = True

    def run(self, sim):
        self.owner.broadcast_mined_block(sim)


class ForwardBlock(Event):
    def __init__(self, timestamp, peer, source, block):
        super().__init__(timestamp)
        self.peer = peer
        self.source = source
        self.block = block

    def run(self, sim):
        # if self.peer.id != self.source.id:
        #     sim.log(f"{self.peer.get_name()} forwards block {self.block.get_name()} received from {self.source.get_name()}")
        self.peer.forward_block(sim, self.source, self.block)


class ReceiveBlock(Event):
    def __init__(self, timestamp, sender, receiver, block):
        super().__init__(timestamp)
        self.sender = sender
        self.receiver = receiver
        self.block = block

    def run(self, sim):
        # sim.log(f"{self.receiver.get_name()} receives block {self.block.get_name()} from {self.sender.get_name()}")
        self.receiver.receive_block(sim, self.sender, self.block)
