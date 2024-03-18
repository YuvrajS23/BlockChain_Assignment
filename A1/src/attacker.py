from utils import *
from peer import *

class SelfishAttacker(Peer):
    def __init__(self):
        super().__init__()
        self.state_0_prime = False

    def generate_new_block(self, sim):
        block = Block(self)
        block.set_parent(self.blockchain.current_block)
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

        assert self.blockchain.current_block.id == block.parent.id
        is_valid = self.validate_block(block, self.balances)

        validity = "INVALID"
        if is_valid:
            self.add_block(block, True)
            validity = "VALID"
        sim.log("Attacker mines " + validity + " block " + block.getName())
        self.block_arrival_times.append((block, sim.current_timestamp))

        if self.state_0_prime:
            ev = ForwardBlock(0, self, self, block.clone())
            sim.add_event(ev)
            self.state_0_prime = False

        self.schedule_next_block(sim)

    def receive_block(self, sim, sender, block):
        chain_it, free_it, reject_it = self.chain_blocks.find(block.id), self.free_blocks.find(block.id), self.rejected_blocks.find(block.id)

        if chain_it is not None or free_it is not None or reject_it is not None:
            return

        self.block_arrival_times.append((block, sim.current_timestamp))

        chain_it = self.chain_blocks.find(block.parent_id)

        if chain_it is None:
            self.free_blocks[block.id] = block
            self.free_block_parents[block.parent_id].append(block)
            return

        block.set_parent(chain_it.second)

        current_block = self.blockchain.current_block
        branch_block = block.parent

        current_balance_change = [0] * G.total_peers
        txns_to_add = []
        while current_block.depth > branch_block.depth:
            current_block, current_balance_change, txns_to_add = Blockchain.backward(current_block, current_balance_change, txns_to_add)

        branch_balance_change = [0] * G.total_peers
        txns_to_remove = []
        while branch_block.depth > current_block.depth:
            branch_block, branch_balance_change, txns_to_remove = Blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        while branch_block.id != current_block.id:
            current_block, branch_block = Blockchain.backward(current_block, current_balance_change, txns_to_add), Blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        for i in range(G.total_peers):
            current_balance_change[i] += balances[i] - branch_balance_change[i]

        blocks_to_add = set()
        deepest_block = None

        self.free_blocks_dfs(block, current_balance_change, blocks_to_add, deepest_block, sim)

        if deepest_block is None:
            return

        if deepest_block.depth == self.blockchain.current_block.depth:
            private_block = self.blockchain.current_block
            while private_block.depth >= block.depth:
                sim.log("Attacker broadcasts block " + private_block.get_name())
                ev = ForwardBlock(0, self, self, private_block.clone())
                sim.add_event(ev)
                private_block = private_block.parent

            for b in blocks_to_add:
                self.add_block(b, False)
        elif deepest_block.depth + 1 == self.blockchain.current_block.depth:
            private_block = self.blockchain.current_block
            while private_block.depth >= block.depth:
                if private_block.depth <= deepest_block.depth:
                    sim.log("Attacker broadcasts block " + private_block.get_name())
                    ev = ForwardBlock(0, self, self, private_block.clone())
                    sim.add_event(ev)
                private_block = private_block.parent

            for b in blocks_to_add:
                self.add_block(b, False)
        elif deepest_block.depth < self.blockchain.current_block.depth:
            private_block = self.blockchain.current_block
            while private_block.depth >= block.depth:
                if private_block.depth <= deepest_block.depth:
                    sim.log("Attacker broadcasts block " + private_block.get_name())
                    ev = ForwardBlock(0, self, self, private_block.clone())
                    sim.add_event(ev)
                private_block = private_block.parent

            for b in blocks_to_add:
                self.add_block(b, False)
        else:
            balances = current_balance_change.copy()
            for txn in txns_to_add:
                self.txn_pool.add(txn)
            for txn in txns_to_remove:
                self.txn_pool.remove(txn)

            order = []
            order.append(deepest_block)
            while order[-1] != block:
                order.append(order[-1].parent)

            while order:
                b = order.pop()
                self.add_block(b, True)
                blocks_to_add.remove(b)

            for b in blocks_to_add:
                self.add_block(b, False)

            if self.next_mining_event is not None:
                sim.delete_event(self.next_mining_event)
                del self.next_mining_block
                self.schedule_next_block(sim)