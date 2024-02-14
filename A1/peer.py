from typing import List
import io
import random
from collections import deque
from transaction import Transaction
from block import Block
from blockchain import Blockchain
from event import *
from link import *
from utils import *

class Peer:
    # list of peers adjacent to this peer
    adj = []
    # all transaction ids received so far
    recv_pool = set()
    # chain_blocks: blocks in the blockchain, free_blocks: blocks not yet in blockchain
    chain_blocks = {}
    free_blocks = {}
    # map from free_block_parents ids to pointer to free blocks 
    free_block_parents = {}
    # transactions not yet mined
    txn_pool = set()
    # blocks which are invalid
    rejected_blocks = set()
    received_blocks = set()
    # stores arrival times for each block
    block_arrival_times = []

    def __init__(self):
        # unique id for every block
        self.id = G.peer_counter
        G.peer_counter += 1
        # balances[i] stores current balance for peer with id i
        # initialize balances of all peers with 0
        self.balances = [0] * G.total_peers
        # print(self.id)
        assert G.Ttx > 0
        assert G.Tk > 0
        # no of peers connected to this
        self.degree = 0
        self.is_fast = False
        # avg of expo dist = 1/lambda
        # distributions to sample txn interarrival time and block mining time
        self.txn_interarrival_time = random.expovariate(1.0 / G.Ttx)
        # uniform distribution to select a peer
        self.unif_dist_peer = random.randint(0, G.total_peers - 1)
        # uniform distribution to select a real no between 0 and 1
        self.unif_rand_real = random.uniform(0, 1)

        self.blockchain = Blockchain()
        # add genesis block in chain_blocks
        self.chain_blocks[self.blockchain.current_block.id] = self.blockchain.current_block

        self.block_arrival_times.append((self.blockchain.genesis, 0))

        # create hash power distribution: 50% with low hash power (0.1) 
        # and remaining 50% with high hash power (0.5)
        # fraction of the entire hash power
        self.hash_power = G.LOW_HASH_POWER if self.unif_rand_real < 0.5 else G.HIGH_HASH_POWER

    # update hash power to normalized value and initialize block mining distribution
    def initialize_block_mining_distribution(self, hash_power):
        self.hash_power = hash_power
        # more hash power: less G.Tk
        self.block_mining_time = random.expovariate(hash_power / G.Tk)

    # returns the name of this peer
    def get_name(self):
        return f"Peer{self.id + 1}"

    # returns the degree for this peer
    def get_degree(self):
        return self.degree

    # creates a link between peer a and peer b
    def add_edge(self, b):   # Peer self, Peer b, ostream os
        # write undirected edge to file
        print(f"Edge between peers: {self.id + 1} {b.id + 1}\n")

        # increase the degree
        self.degree += 1
        b.degree += 1

        # add b in self's adj list
        ab = Link(b, self.is_fast)
        self.adj.append(ab)

        # add self in b's adj list
        ba = Link(self, b.is_fast)
        b.adj.append(ba)

    # ================== TRANSACTION =============================

    def schedule_next_transaction(self, sim):
        interArrivalTime = self.txn_interarrival_time
        ev = GenerateTransaction(interArrivalTime, self)
        sim.add_event(ev)

    def generate_transaction(self, sim):
        generate_invalid = random.uniform(0, 1) < sim.invalid_txn_prob
        coins = -1
        cur_balance = self.balances[self.id]

        if generate_invalid:
            coins = cur_balance + random.randint(1, 100)
        elif cur_balance == 0:
            coins = 0
        else:
            coins = random.randint(1, cur_balance)

        txn = None
        if coins > 0:
            # todo: check if uniform distribution is correct for sampling receiver & no of coins
            receiver = random.randint(0, G.total_peers - 1)
            while receiver == self.id:
                receiver = random.randint(0, G.total_peers - 1)

            txn = Transaction(sim.current_timestamp, self, G.peers[receiver], coins)

            # todo: add transaction in transaction/recv pool
            self.recv_pool.add(txn.id)
            self.txn_pool.add(txn)

            # forward the transaction to peers
            ev = ForwardTransaction(0, self, self, txn)
            sim.add_event(ev)

        # generate new transaction
        self.schedule_next_transaction(sim)
        return txn

    def forward_transaction(self, sim, source, txn):
        # send transaction to peers
        for link in self.adj:
            if link.peer.id == source.id:
                continue  # source already has the txn, loop-less forwarding
            delay = link.get_delay(G.TRANSACTION_SIZE)
            ev = ReceiveTransaction(delay, self, link.peer, txn)
            sim.add_event(ev)

    def receive_transaction(self, sim, sender, txn):
        # if already received the transaction then ignore
        if txn.id in self.recv_pool:
            return

        self.recv_pool.add(txn.id)
        self.txn_pool.add(txn)

        # forward the txn to other peers
        ev = ForwardTransaction(0, self, sender, txn)
        sim.add_event(ev)

    def validate_txn(self, txn, custom_balances):
        balance = custom_balances[txn.sender.id]
        return balance >= txn.amount

    # ================== BLOCK =============================

    def validate_block(self, block, custom_balances):
        if block.size > G.max_size:
            return False
        balances_copy = custom_balances[:]
        for txn in block.txns:
            if not self.validate_txn(txn, balances_copy):
                return False
            balances_copy[txn.sender.id] -= txn.amount
            balances_copy[txn.receiver.id] += txn.amount
        return True

    # generate new block: equivalent of mining a block and add corresponding event
    def generate_new_block(self, sim):
        generate_invalid = random.uniform(0, 1) < sim.invalid_block_prob
        block = Block(self)
        block.set_parent(self.blockchain.current_block)
        is_invalid = False
        balances_copy = self.balances[:]
        if generate_invalid:
            for txn in self.txn_pool:
                if block.size + G.TRANSACTION_SIZE > G.max_size:
                    if not is_invalid:
                        block.add(txn)
                        is_invalid = True
                    break
                if not self.validate_txn(txn, balances_copy):
                    is_invalid = True
                balances_copy[txn.sender.id] -= txn.amount
                balances_copy[txn.receiver.id] += txn.amount
                block.add(txn)
            return block
        for txn in self.txn_pool:
            if block.size + G.TRANSACTION_SIZE > G.max_size:
                break
            if self.validate_txn(txn, balances_copy):
                block.add(txn)
                balances_copy[txn.sender.id] -= txn.amount
                balances_copy[txn.receiver.id] += txn.amount
        return block

    def schedule_next_block(self, sim):
        self.next_mining_block = self.generate_new_block(sim)
        miningTime = random.expovariate(self.hash_power / G.Tk)
        self.next_mining_event = BroadcastMinedBlock(miningTime, self)
        sim.add_event(self.next_mining_event)

    def broadcast_mined_block(self, sim):
        block = self.next_mining_block
        block.set_id()

        assert self.blockchain.current_block.id == block.parent.id
        is_valid = self.validate_block(block, self.balances)

        # do not add an invalid block, only transmit it to other peers
        validity = "INVALID"
        if is_valid:
            self.add_block(block, True)
            validity = "VALID"
        sim.log(f"{self.get_name()} mines and broadcasts {validity} block {block.get_name()}")
        self.block_arrival_times.append((block, sim.current_timestamp))

        ev = ForwardBlock(0, self, self, block.clone())
        sim.add_event(ev)

        self.schedule_next_block(sim)

    def forward_block(self, sim, source, block):
        # send block to peers
        # this block is a copy, memory needs to be freed
        for link in self.adj:
            if link.peer.id == source.id:
                continue  # source already has the block, loop-less forwarding
            new_block = block.clone()
            delay = link.get_delay(new_block.size)
            ev = ReceiveBlock(delay, self, link.peer, new_block)
            sim.add_event(ev)
        del block

    # add block to the blockchain and update balances
    def add_block(self, block, update_balances):
        self.blockchain.add(block)
        self.chain_blocks[block.id] = block
        if update_balances:
            for txn in block.txns:
                self.balances[txn.sender.id] -= txn.amount
                self.balances[txn.receiver.id] += txn.amount
                if txn in self.txn_pool:
                    self.txn_pool.remove(txn)
            self.balances[block.owner.id] += G.MINING_FEE
            self.blockchain.current_block = block

    def delete_invalid_free_blocks(self, block, sim):
        it = block.id in self.free_block_parents.keys()
        
        # add block to rejected_blocks
        self.rejected_blocks.add(block.id)
        sim.log(f"{self.get_name()} REJECTS block {block.get_name()}")
        
        if not it:
            return

        # recursive call to delete child blocks
        for child in self.free_block_parents[block.id]:
            assert child.parent is None
            child.set_parent(block)
            del self.free_blocks[child.id]
            self.delete_invalid_free_blocks(child, sim)
        del self.free_block_parents[block.id]

    def free_blocks_dfs(self, block, cur_balances, blocks_to_add, deepest_block, sim):
        if not self.validate_block(block, cur_balances):
            self.delete_invalid_free_blocks(block, sim)
            return

        blocks_to_add.add(block)
        if deepest_block is None or block.depth > deepest_block.depth:
            deepest_block = block

        it = block.id in self.free_block_parents.keys()
        if not it:
            return

        # update balance array
        for txn in block.txns:
            cur_balances[txn.sender.id] -= txn.amount
            cur_balances[txn.receiver.id] += txn.amount
        cur_balances[block.owner.id] += G.MINING_FEE

        # recursive call to child blocks
        for child in self.free_block_parents[block.id]:
            assert child.parent is None
            child.set_parent(block)
            del self.free_blocks[child.id]
            self.free_blocks_dfs(child, cur_balances, blocks_to_add, deepest_block, sim)
        del self.free_block_parents[block.id]

        # reset balance array
        for txn in block.txns:
            cur_balances[txn.sender.id] += txn.amount
            cur_balances[txn.receiver.id] -= txn.amount
        cur_balances[block.owner.id] -= G.MINING_FEE

    def receive_block(self, sim, sender, block):
        chain_it = block.id in self.chain_blocks.keys()
        free_it = block.id in self.free_blocks.keys()
        reject_it = block.id in self.rejected_blocks

        # already received this block
        if not chain_it or free_it is not None or not reject_it:
            return

        # block arrival times
        self.block_arrival_times.append((block, sim.current_timestamp))
        
        # forward every received block regardless of validity
        ev = ForwardBlock(0, self, sender, block.clone())
        sim.add_event(ev)
        
        chain_it = block.parent_id in self.chain_blocks.keys()

        # block parent not in our blockchain
        if not chain_it:
            self.free_blocks[block.id] = block
            self.free_block_parents[block.parent_id].append(block)
            return

        block.set_parent(self.chain_blocks[block.parent_id])

        current_block = self.blockchain.current_block  # last block in the blockchain
        branch_block = block.parent  # add the new block as a child of branch block

        # balances to update in case longest chain changes
        current_balance_change = [0] * G.total_peers
        # txns to add to the txn pool in case longest chain changes
        txns_to_add = []
        # find lca
        while current_block.depth > branch_block.depth:
            current_block = Blockchain.backward(current_block, current_balance_change, txns_to_add)

        # balances to update in case longest chain changes
        branch_balance_change = [0] * G.total_peers
        # txns to remove from the txn pool in case longest chain changes
        txns_to_remove = []
        while branch_block.depth > current_block.depth:
            branch_block = Blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        while branch_block.id != current_block.id:
            current_block = Blockchain.backward(current_block, current_balance_change, txns_to_add)
            branch_block = Blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        # current_balance_change = balances just before block insertion point
        for i in range(G.total_peers):
            current_balance_change[i] += self.balances[i] - branch_balance_change[i]

        blocks_to_add = set()
        deepest_block = None

        self.free_blocks_dfs(block, current_balance_change, blocks_to_add, deepest_block, sim)

        # block is invalid
        if deepest_block is None:
            return

        # now block gets added to blockchain
        # balances will be updated only if branch was changed
        if deepest_block.depth > self.blockchain.current_block.depth:

            # change peer state to just before block insertion
            self.balances = current_balance_change
            self.txn_pool.extend(txns_to_add)
            self.txn_pool = [item for item in self.txn_pool if item not in txns_to_remove]

            order = [deepest_block]
            while order[-1] != block:
                order.append(order[-1].parent)

            while order:
                b = order.pop()
                self.add_block(b, True)
                blocks_to_add.discard(b)

            for b in blocks_to_add:
                self.add_block(b, False)

            if self.next_mining_event is not None:
                sim.delete_event(self.next_mining_event)
                del self.next_mining_block
                self.schedule_next_block(sim)
        else:
            for b in blocks_to_add:
                self.add_block(b, False)

    # output the edges in blockchain in os and update deepest_block
    def traverse_blockchain(self, b, os, deepest_block, total_blocks):
        # for canonicalization
        b.next.sort(key=lambda a: a.id)
        if b.depth > deepest_block.depth or (b.depth == deepest_block.depth and b.id < deepest_block.id):
            deepest_block = b

        # genesis id is -2
        if b.parent_id >= -1:
            total_blocks[b.owner.id] += 1

        for c in b.next:
            os.write(f"{b.id + 1} {c.id + 1}\n")
            self.traverse_blockchain(c, os, deepest_block, total_blocks)

    # output the arrival times of blocks to os
    def export_arrival_times(self, os):
        self.block_arrival_times.sort(key=lambda p: p[0].id)

        os.write(f"{self.get_name()}\n")
        for p in self.block_arrival_times:
            b, timestamp = p
            os.write(f"{b.get_name()}, {b.depth}, {timestamp:.5f}, {('NO_PARENT' if b.parent is None else b.parent.get_name())}\n")
        os.write("\n")

    # output the blockchain to a stream
    def export_blockchain(self, os):
        total_blocks = [0] * G.total_peers
        deepest_block = self.blockchain.genesis
        self.traverse_blockchain(self.blockchain.genesis, os, deepest_block, total_blocks)

    # output the final statistics to a file
    def export_stats(self, sim, os):
        fake = io.StringIO()
        deepest_block = self.blockchain.genesis
        total_blocks = [0] * G.total_peers
        self.traverse_blockchain(self.blockchain.genesis, fake, deepest_block, total_blocks)

        blocks_in_chain = [0] * G.total_peers
        while deepest_block.id != self.blockchain.genesis.id:
            blocks_in_chain[deepest_block.owner.id] += 1
            deepest_block = deepest_block.parent

        os.write("id,chain_blocks,generated_blocks,is_fast,hash_power\n")
        for i in range(G.total_peers):
            os.write(f"{i + 1},{blocks_in_chain[i]},{total_blocks[i]},{int(self.is_fast)},{self.hash_power}\n")

