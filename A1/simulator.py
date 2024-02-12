from collections import deque
import random
import math
import os
import shutil
from typing import List, Set, Tuple
from peer import *
from transaction import *
from block import *
from blockchain import *
from event import *
from utils import *


class Simulator:
    def __init__(self, n_, z_, Ttx_, Tk_, edges_, verbose_, invalid_txn_prob_, invalid_block_prob_, zeta_, adversary_, alpha_):
        self.n = n_
        self.z = min(1.0, max(z_, 0.0))
        self.slow_peers = int(self.z * self.n)
        self.Ttx = Ttx_
        self.Tk = Tk_
        self.edges = edges_
        self.current_timestamp = START_TIME
        self.invalid_txn_prob = invalid_txn_prob_
        self.invalid_block_prob = invalid_block_prob_
        self.verbose = verbose_
        self.has_simulation_ended = False
        self.zeta = zeta_
        self.adversary = adversary_
        self.alpha = alpha_
        global max_size, global_genesis, total_peers, Ttx, Tk
        max_size = MAX_BLOCK_SIZE
        global_genesis = Block(None)
        global_genesis.set_parent(None)
        total_peers = self.n
        Ttx = self.Ttx
        Tk = self.Tk
        self.events = set()
        self.current_event = None

    def get_name(self):
        return f"Simulator-{self.n}-{self.z}-{self.Ttx}-{self.Tk}-{self.edges}-{self.verbose}-{self.invalid_txn_prob}-{self.invalid_block_prob}-{self.zeta}-{self.adversary}-{self.alpha}"

    def reset(self, dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path)

    def get_new_peers(self):
        global peers
        if self.adversary != "none":
            self.n -= 1

        peers = [Peer() for _ in range(self.n)]

        for i in range(self.slow_peers):
            peers[i].is_fast = False
        for i in range(self.slow_peers, self.n):
            peers[i].is_fast = True

        random.shuffle(peers)

        # if self.adversary != "none":
        #     self.n += 1
        #     if self.adversary == "selfish":
        #         peers.append(SelfishAttacker())
        #     else:
        #         peers.append(StubbornAttacker())
        #     peers[-1].is_fast = True
        #     honest_power = 0.0
        #     for i in range(self.n - 1):
        #         honest_power += peers[i].hash_power
        #     peers[-1].hash_power = (honest_power * self.alpha) / (1 - self.alpha)
        global peer_counter
        for i in range(self.n):
            peers[i].id = peer_counter
            peer_counter += 1

        normalization_factor = sum(p.hash_power / self.n for p in peers)
        for p in peers:
            p.initialize_block_mining_distribution(p.hash_power / normalization_factor)

    def form_random_network(self, os):
        assert self.edges >= self.n - 1
        global peers
        n = len(peers)

        if self.adversary != "none":
            n -= 1

        assert n >= 2

        node_1 = random.randint(0, n - 1)
        node_2 = random.randint(0, n - 1)
        while node_2 == node_1:
            node_2 = random.randint(0, n - 1)

        if node_1 > node_2:
            node_1, node_2 = node_2, node_1

        s = set(range(n))
        t = {node_1, node_2}

        Peer.add_edge(peers[node_1], peers[node_2], os)
        self.edges -= 1

        degrees = [0] * n
        degrees[node_1] += 1
        degrees[node_2] += 1

        edges_log = {(node_1, node_2)}

        while s:
            next_node = random.randint(0, n - 1)
            if next_node not in t:
                disc = random.choices(range(n), weights=degrees, k=1)[0]
                while disc == next_node:
                    disc = random.choices(range(n), weights=degrees, k=1)[0]

                s.remove(next_node)
                t.add(next_node)

                if next_node > disc:
                    next_node, disc = disc, next_node

                Peer.add_edge(peers[next_node], peers[disc], os)
                self.edges -= 1
                degrees[next_node] += 1
                degrees[disc] += 1

        edges_set = set()
        while self.edges > 0:
            a = random.randint(0, n - 1)
            disc = random.choices(range(n), weights=degrees, k=1)[0]
            while disc == a:
                disc = random.choices(range(n), weights=degrees, k=1)[0]

            if a > disc:
                a, disc = disc, a

            if (a, disc) not in edges_set:
                Peer.add_edge(peers[a], peers[disc], os)
                self.edges -= 1
                degrees[a] += 1
                degrees[disc] += 1
                edges_set.add((a, disc))

        if self.adversary != "none":
            self.edges = int(self.zeta * n)
            n += 1
            while self.edges > 0:
                a = random.randint(0, n - 1)
                b = n - 1

                if (a, b) not in edges_set:
                    Peer.add_edge(peers[a], peers[b], os)
                    self.edges -= 1
                    degrees[a] += 1
                    degrees[b] += 1

    def init_events(self):
        global peers
        for peer in peers:
            peer.schedule_next_transaction(self)
            peer.schedule_next_block(self)

    def add_event(self, event):
        event.timestamp += self.current_timestamp
        self.events.add(event)

    def delete_event(self, event):
        assert event is not None
        self.events.remove(event)
        del event

    def run(self, end_time_, max_txns_, max_blocks_):
        self.get_new_peers()

        self.reset("output")
        filename = "output/peer_network_edgelist.txt"
        with open(filename, 'w') as outfile:
            self.form_random_network(outfile)

        self.init_events()
        self.has_simulation_ended = False

        max_txns = INT_MAX if max_txns_ <= 0 else max_txns_
        max_blocks = INT_MAX if max_blocks_ <= 0 else max_blocks_
        end_time = DBL_MAX if end_time_ <= 0 else end_time_
        global txn_counter, blk_counter
        while self.events:
            self.current_event = min(self.events, key=lambda x: x.timestamp)
            self.current_timestamp = self.current_event.timestamp

            if self.current_event.timestamp > end_time:
                break
            if txn_counter >= max_txns:
                break
            if blk_counter >= max_blocks:
                break

            self.current_event.run(self)

            self.delete_event(self.current_event)
        global peers

        self.reset("output/termination_blockchains")
        for p in peers:
            filename = f"output/termination_blockchains/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_blockchain(outfile)

        self.complete_non_generate_events()

        self.reset("output/block_arrivals")
        for p in peers:
            filename = f"output/block_arrivals/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_arrival_times(outfile)

        self.reset("output/peer_stats")
        for p in peers:
            filename = f"output/peer_stats/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_stats(self, outfile)

        print("Total Transactions:", txn_counter)
        print("Total Blocks:", blk_counter)

    def complete_non_generate_events(self):
        self.has_simulation_ended = True
        global peers

        for p in peers:
            p.next_mining_event = None
            p.next_mining_block = None

        while self.events:
            self.current_event = min(self.events, key=lambda x: x.timestamp)
            self.current_timestamp = self.current_event.timestamp

            if not self.current_event.is_generate_type_event:
                self.current_event.run(self)

            self.delete_event(self.current_event)

        self.reset("output/final_blockchains")
        for p in peers:
            filename = f"output/final_blockchains/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_blockchain(outfile)

    def log(self, os, s):
        if not self.verbose:
            return
        os.write(f"Time {self.current_timestamp:.5f}: {s}\n")
