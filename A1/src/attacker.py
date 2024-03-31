from utils import *
from peer import *

# Class for SelfishAttacker which is inherited from the Peer Class
class SelfishAttacker(Peer):
    def __init__(self):
        # Initializing the parent Peer class
        super().__init__()
        # State_0_prime indicates the state 0' where the attacker and honest miners would compete for generating the next block
        self.state_0_prime = False
        # Attacker mines and expands this private Chain
        self.privateChain = []

    # generate new block: equivalent of mining a block and add corresponding event
    def generate_new_block(self, sim):
        block = Block(self)
        # If there is no private Chain
        if len(self.privateChain) <= 0:
            # then mine on the last block of the main chain (longest chain)
            block.setParent(self.blockchain.current_block)
        else:
            # else mine on the private Chain
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

    # Broadcasts the mined block
    def broadcast_mined_block(self, sim):
        # Block to broadcast
        block = self.next_mining_block
        block.setID()
        # If there is no private Chain and the longest chain of the blockchain changes
        if len(self.privateChain) <= 0:
            if self.blockchain.current_block.id != block.parent.id:
                # then Mine another block 
                self.schedule_next_block(sim)
                return
        # Mined block must be mined on the last block of private Chain or the last block of longest Chain
        assert self.blockchain.current_block.id == block.parent.id or self.privateChain[-1].id == block.parent.id
        is_valid = self.validate_block(block, self.balances)
        # Gets the Attacker number
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
        # Printing the attacker's mining log
        sim.log("Attacker" + attnum + " mines " + validity + " block " + block.getName())
        # Adding it to block arrival times of attacker
        self.block_arrival_times.append((block, sim.current_timestamp))

        # If competing for generating blocks
        if self.state_0_prime:
            # then forward this generated block as soon as possible
            ev = ForwardBlock(0, self, self, block.clone())
            sim.add_event(ev)
            self.state_0_prime = False

        # In any case, schedule mining of next block
        self.schedule_next_block(sim)

    # receives a blocks and handles it accordingly
    def receive_block(self, sim, sender, block):
        chain_it = block.id in self.chain_blocks.keys()
        free_it = block.id in self.free_blocks.keys()
        reject_it = block.id in self.rejected_blocks
        # already received this block
        if chain_it or free_it or reject_it:
            return
        # Gets the Attacker number
        attnum = str(self.id + 3 - G.total_peers)
        # print("Received Block", block.id+1, "for attacker",attnum)
        # block arrival times
        self.block_arrival_times.append((block, sim.current_timestamp))

        chain_it = block.parent_id in self.chain_blocks.keys()

        # block parent not in our blockchain
        if not chain_it:
            self.free_blocks[block.id] = block
            if block.parent_id in self.free_block_parents.keys():
                self.free_block_parents[block.parent_id].append(block)
            else:
                self.free_block_parents[block.parent_id] = [block]
            return

        block.setParent(self.chain_blocks[block.parent_id])

        current_block = self.blockchain.current_block   # last block in the blockchain
        branch_block = block.parent # add the new block as a child of branch block

        # balances to update in case longest chain changes
        current_balance_change = [0] * G.total_peers
        # txns to add to the txn pool in case longest chain changes
        txns_to_add = []
        # find lca
        while current_block.depth > branch_block.depth:
            current_block = self.blockchain.backward(current_block, current_balance_change, txns_to_add)

        # balances to update in case longest chain changes
        branch_balance_change = [0] * G.total_peers
        # txns to remove from the txn pool in case longest chain changes
        txns_to_remove = []
        while branch_block.depth > current_block.depth:
            branch_block = self.blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        while branch_block.id != current_block.id:
            current_block = self.blockchain.backward(current_block, current_balance_change, txns_to_add)
            branch_block = self.blockchain.backward(branch_block, branch_balance_change, txns_to_remove)

        # current_balance_change = balances just before block insertion point
        for i in range(G.total_peers):
            current_balance_change[i] += self.balances[i] - branch_balance_change[i]

        blocks_to_add = set()
        deepest_block = None

        deepest_block = self.free_blocks_dfs(block, current_balance_change, blocks_to_add, deepest_block, sim)

        if deepest_block is None:
            return

        # balances will be updated only if branch was changed
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
                # Add the block to blockchain and make it the longest chain
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

        # After receiving the block from an honest node
        # If there are some blocks mined in the private Chain
        if len(self.privateChain) > 0:
            # If Pvt Chain depth < longest chain depth
            if self.privateChain[-1].depth < self.blockchain.current_block.depth:
                # Nullify the private Chain and start a new attack
                self.privateChain = []
            # If Pvt Chain depth == longest chain depth
            elif self.privateChain[-1].depth == self.blockchain.current_block.depth:
                # Forward all the blocks of the private Chain and empty the chain
                while self.privateChain:
                    b = self.privateChain[0]
                    del self.privateChain[0]
                    self.add_block(b, True)
                    sim.log("Attacker" + attnum + " broadcasts block " + b.getName())
                    ev = ForwardBlock(0, self, self, b.clone())
                    sim.add_event(ev)
                # Enter state 0'
                self.state_0_prime = True
            # If Pvt Chain depth == longest chain depth + 1
            elif self.privateChain[-1].depth == self.blockchain.current_block.depth + 1:
                # Forward all the blocks of the private Chain and empty the chain
                while self.privateChain:
                    b = self.privateChain[0]
                    del self.privateChain[0]
                    self.add_block(b, True)
                    sim.log("Attacker" + attnum + " broadcasts block " + b.getName())
                    ev = ForwardBlock(0, self, self, b.clone())
                    sim.add_event(ev)
            # If Pvt Chain depth > longest chain depth
            elif self.privateChain[-1].depth >= self.blockchain.current_block.depth + 2:
                # Broadcast Private Blocks up until the current longest chain's depth
                while self.privateChain[0].depth <= self.blockchain.current_block.depth:
                    b = self.privateChain[0]
                    del self.privateChain[0]
                    self.add_block(b, True)
                    sim.log("Attacker" + attnum + " broadcasts block " + b.getName())
                    ev = ForwardBlock(0, self, self, b.clone())
                    sim.add_event(ev)