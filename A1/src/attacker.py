from utils import *
from peer import *

class SelfishAttacker(Peer):
    def __init__(self):
        super().__init__()
        self.state_0_prime = False
        self.privateChain = []

    def generate_new_block(self, sim):
        block = Block(self)
        if len(self.privateChain) <= 0:
            block.setParent(self.blockchain.current_block)
        else:
            block.setParent(self.privateChain[-1])
        balances_copy = self.balances.copy()
        for txn in self.txn_pool:
            if block.size + G.TRANSACTION_SIZE > G.max_size:
                break
            if self.validate_txn(txn, balances_copy):
                block.add(txn)
                balances_copy[txn.sender.id] -= txn.amount
                balances_copy[txn.receiver.id] += txn.amount
        return block

    def broadcast_mined_block(self, sim):
        block = self.next_mining_block
        block.setID()

        assert self.blockchain.current_block.id == block.parent.id or self.privateChain[-1].id == block.parent.id
        is_valid = self.validate_block(block, self.balances)
        attnum = str(self.id + 3 - G.total_peers)

        validity = "INVALID"
        if is_valid:
            self.privateChain.append(block)
            # Update Balances
            for txn in block.txns:
                self.balances[txn.sender.id] -= txn.amount
                self.balances[txn.receiver.id] += txn.amount
                if txn in self.txn_pool:
                    self.txn_pool.remove(txn)
            self.balances[block.owner.id] += G.MINING_FEE
            validity = "VALID"
        sim.log("Attacker" + attnum + " mines " + validity + " block " + block.getName())
        self.block_arrival_times.append((block, sim.current_timestamp))

        if self.state_0_prime:
            ev = ForwardBlock(0, self, self, block.clone())
            sim.add_event(ev)
            self.state_0_prime = False

        self.schedule_next_block(sim)

    def receive_block(self, sim, sender, block):
        chain_it = block.id in self.chain_blocks.keys()
        free_it = block.id in self.free_blocks.keys()
        reject_it = block.id in self.rejected_blocks
        if chain_it or free_it or reject_it:
            return
        attnum = str(self.id + 3 - G.total_peers)
        self.block_arrival_times.append((block, sim.current_timestamp))

        chain_it = block.parent_id in self.chain_blocks.keys()

        if not chain_it:
            self.free_blocks[block.id] = block
            if block.parent_id in self.free_block_parents.keys():
                self.free_block_parents[block.parent_id].append(block)
            else:
                self.free_block_parents[block.parent_id] = [block]
            return

        block.setParent(self.chain_blocks[block.parent_id])

        current_block = self.blockchain.current_block
        branch_block = block.parent

        current_balance_change = [0] * G.total_peers
        txns_to_add = []
        while current_block.depth > branch_block.depth:
            current_block = self.blockchain.backward(current_block, current_balance_change, txns_to_add)

        branch_balance_change = [0] * G.total_peers
        txns_to_remove = []
        while branch_block.depth > current_block.depth:
            branch_block = self.blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        while branch_block.id != current_block.id:
            current_block = self.blockchain.backward(current_block, current_balance_change, txns_to_add)
            branch_block = self.blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        for i in range(G.total_peers):
            current_balance_change[i] += self.balances[i] - branch_balance_change[i]

        blocks_to_add = set()
        deepest_block = None

        deepest_block = self.free_blocks_dfs(block, current_balance_change, blocks_to_add, deepest_block, sim)

        if deepest_block is None:
            return
        # if deepest_block.depth == self.blockchain.current_block.depth:
        #     private_block = self.blockchain.current_block
        #     print("Pvt Block Depth before adding", private_block.depth)
        #     while private_block.depth >= block.depth:
        #         print("Going from state 1 to 0")
        #         sim.log("Attacker" + attnum + " broadcasts block " + private_block.getName())
        #         ev = ForwardBlock(0, self, self, private_block.clone())
        #         sim.add_event(ev)
        #         private_block = private_block.parent
        #     self.state_0_prime = True
        #     for b in blocks_to_add:
        #         self.add_block(b, False)
        #     print("Pvt Block Depth after adding", private_block.depth)
        # elif deepest_block.depth + 1 == self.blockchain.current_block.depth:
        #     private_block = self.blockchain.current_block
        #     print("Pvt Block Depth before adding", private_block.depth)
        #     while private_block.depth >= block.depth:
        #         if private_block.depth <= deepest_block.depth:
        #             print("Going from state 2 to 0")
        #             sim.log("Attacker" + attnum + " broadcasts block " + private_block.getName())
        #             ev = ForwardBlock(0, self, self, private_block.clone())
        #             sim.add_event(ev)
        #         private_block = private_block.parent

        #     for b in blocks_to_add:
        #         self.add_block(b, False)
        #     print("Pvt Block Depth after adding", private_block.depth)
        # elif deepest_block.depth < self.blockchain.current_block.depth:
        #     private_block = self.blockchain.current_block
        #     print("Pvt Block Depth before adding", private_block.depth)
        #     while private_block.depth >= block.depth:
        #         if private_block.depth <= deepest_block.depth:
        #             print("Going from state 0 to 0")
        #             sim.log("Attacker" + attnum + " broadcasts block " + private_block.getName())
        #             ev = ForwardBlock(0, self, self, private_block.clone())
        #             sim.add_event(ev)
        #         private_block = private_block.parent

        #     for b in blocks_to_add:
        #         self.add_block(b, False)
        #     print("Pvt Block Depth after adding", private_block.depth)
        # else:
        #     balances = current_balance_change.copy()
        #     for txn in txns_to_add:
        #         self.txn_pool.add(txn)
        #     for txn in txns_to_remove:
        #         self.txn_pool.remove(txn)

        #     order = []
        #     order.append(deepest_block)
        #     while order[-1] != block:
        #         order.append(order[-1].parent)

        #     while order:
        #         b = order.pop()
        #         self.add_block(b, True)
        #         blocks_to_add.remove(b)

        #     for b in blocks_to_add:
        #         self.add_block(b, False)

        #     if self.next_mining_event is not None:
        #         sim.delete_event(self.next_mining_event)
        #         del self.next_mining_block
        #         self.schedule_next_block(sim)

        if deepest_block.depth > self.blockchain.current_block.depth:

            # change peer state to just before block insertion
            self.balances = current_balance_change
            self.txn_pool = self.txn_pool.union(set(txns_to_add))
            self.txn_pool = set([item for item in self.txn_pool if item not in txns_to_remove])

            order = [deepest_block]
            while order[-1] != block:
                order.append(order[-1].parent)

            while order:
                b = order.pop()
                # print("Heyaa got you")
                # print(f"Adding id {block.id + 1} with parent {block.parent_id} in peer {self.id + 1}'s blockchain")
                self.add_block(b, True)
                blocks_to_add.discard(b)

            for b in blocks_to_add:
                # print(f"Adding id {block.id + 1} with parent {block.parent_id} in peer {self.id + 1}'s blockchain")
                self.add_block(b, False)

            if self.next_mining_event is not None:
                sim.delete_event(self.next_mining_event)
                del self.next_mining_block
                self.schedule_next_block(sim)
        else:
            for b in blocks_to_add:
                # print(f"Adding id {block.id + 1} with parent {block.parent_id} in peer {self.id + 1}'s blockchain")
                self.add_block(b, False)

        if len(self.privateChain) > 0:
            if self.privateChain[-1].depth < self.blockchain.current_block.depth:
                self.privateChain = []
            elif self.privateChain[-1].depth == self.blockchain.current_block.depth:
                while self.privateChain:
                    b = self.privateChain[0]
                    del self.privateChain[0]
                    self.add_block(b, True)
                    sim.log("Attacker" + attnum + " broadcasts block " + b.getName())
                    ev = ForwardBlock(0, self, self, b.clone())
                    sim.add_event(ev)
                self.state_0_prime = True
            elif self.privateChain[-1].depth == self.blockchain.current_block.depth + 1:
                while self.privateChain:
                    b = self.privateChain[0]
                    del self.privateChain[0]
                    self.add_block(b, True)
                    sim.log("Attacker" + attnum + " broadcasts block " + b.getName())
                    ev = ForwardBlock(0, self, self, b.clone())
                    sim.add_event(ev)
            elif self.privateChain[-1].depth >= self.blockchain.current_block.depth + 2:
                while self.privateChain[0].depth <= self.blockchain.current_block.depth:
                    b = self.privateChain[0]
                    del self.privateChain[0]
                    self.add_block(b, True)
                    sim.log("Attacker" + attnum + " broadcasts block " + b.getName())
                    ev = ForwardBlock(0, self, self, b.clone())
                    sim.add_event(ev)