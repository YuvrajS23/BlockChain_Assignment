from typing import Optional

class Event:
    def __init__(self, timestamp):
        # timestamp at which event occured/will occur
        self.timestamp = timestamp
        # bool to indicate if the event generates a new txn/block such events are ignored after simulation end time
        self.is_generate_type_event = False  # default value false

    # compare based on timestamp
    def __lt__(self, other):    # other: Event
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        else:
            # two different events with the same timestamp should not be considered as equal
            return id(self) < id(other)

    # execute the event, definition in derived classes
    def run(self, sim):
        assert False


class GenerateTransaction(Event):
    def __init__(self, timestamp, payed_by):
        super().__init__(timestamp)
        self.payed_by = payed_by    # Peer
        self.is_generate_type_event = True

    def run(self, sim): # Simulator : sim
        txn = self.payed_by.generate_transaction(sim)   # generate_transaction func in Peer class
        # if txn is not None:
            # sim.log(f"{self.payed_by.get_name()} generates and emits transaction {txn.get_name()}")
            # pass


class ForwardTransaction(Event):
    def __init__(self, timestamp, peer, source, txn):
        super().__init__(timestamp)
        self.peer = peer    # peer who'll forward the transaction
        self.source = source    # peer who sent the transaction (won't forward to this peer)
        self.txn = txn      # transaction

    def run(self, sim):
        # if self.peer.id != self.source.id:
        #     sim.log(f"{self.peer.get_name()} forwards transaction {self.txn.get_name()} received from {self.source.get_name()}")
        self.peer.forward_transaction(sim, self.source, self.txn)   # forward_transaction func in Peer class


class ReceiveTransaction(Event):
    def __init__(self, timestamp, sender, receiver, txn):
        super().__init__(timestamp)
        self.sender = sender
        self.receiver = receiver    # peer who receives the transaction
        self.txn = txn  # transaction

    def run(self, sim):
        # sim.log(f"{self.receiver.get_name()} receives transaction {self.txn.get_name()} from {self.sender.get_name()}")
        self.receiver.receive_transaction(sim, self.sender, self.txn)   # receive_transaction func in Peer class


class BroadcastMinedBlock(Event):
    def __init__(self, timestamp, owner):
        super().__init__(timestamp)
        self.owner = owner  # Owner Peer
        self.is_generate_type_event = True

    def run(self, sim):
        self.owner.broadcast_mined_block(sim)    # broadcast_mined_block func in Peer class


class ForwardBlock(Event):
    def __init__(self, timestamp, peer, source, block):
        super().__init__(timestamp)
        self.peer = peer    # peer who'll forward the block
        self.source = source    # peer who sent the block (won't forward to this peer)
        self.block = block  # block

    def run(self, sim):
        # if self.peer.id != self.source.id:
        #     sim.log(f"{self.peer.get_name()} forwards block {self.block.get_name()} received from {self.source.get_name()}")
        self.peer.forward_block(sim, self.source, self.block)    # forward_block func in Peer class


class ReceiveBlock(Event):
    def __init__(self, timestamp, sender, receiver, block):
        super().__init__(timestamp)
        self.sender = sender
        self.receiver = receiver    # peer who receives the block
        self.block = block  # block

    def run(self, sim):
        # sim.log(f"{self.receiver.get_name()} receives block {self.block.get_name()} from {self.sender.get_name()}")
        self.receiver.receive_block(sim, self.sender, self.block)    # receive_block func in Peer class
