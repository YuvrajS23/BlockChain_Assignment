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
from graph_generator import *


class Simulator:
    def __init__(self, n_, z0_, z1_, Ttx_, Tk_, verbose_, invalid_txn_prob_, invalid_block_prob_, zeta_, adversary_, alpha_):
        self.n = n_
        self.z0 = min(1.0, max(z0_, 0.0))
        self.slow_peers = int(self.z0 * self.n)
        self.z1 = min(1.0, max(z1_, 0.0))
        self.lowhashpower = int(self.z1 * self.n)
        self.Ttx = Ttx_
        self.Tk = Tk_
        self.current_timestamp = G.START_TIME
        self.invalid_txn_prob = invalid_txn_prob_
        self.invalid_block_prob = invalid_block_prob_
        self.verbose = verbose_
        self.has_simulation_ended = False
        self.zeta = zeta_
        self.adversary = adversary_
        self.alpha = alpha_
        G.global_genesis = Block(None)
        G.global_genesis.set_parent(None)
        G.total_peers = self.n
        G.Ttx = self.Ttx
        G.Tk = self.Tk
        self.events = set()
        self.current_event = None

    def get_name(self):
        return f"Simulator-{self.n}-{self.z}-{self.Ttx}-{self.Tk}-{self.edges}-{self.verbose}-{self.invalid_txn_prob}-{self.invalid_block_prob}-{self.zeta}-{self.adversary}-{self.alpha}"

    def reset(self, dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path)

    def get_new_peers(self):
        if self.adversary != "none":
            self.n -= 1

        G.peers = [Peer() for _ in range(self.n)]
        # print(G.peers[5].id)

        for i in range(self.slow_peers):
            G.peers[i].is_fast = False
        for i in range(self.slow_peers, self.n):
            G.peers[i].is_fast = True

        for i in range(self.lowhashpower):
            G.peers[i].hash_power = G.LOW_HASH_POWER
        for i in range(self.lowhashpower, self.n):
            G.peers[i].hash_power = G.HIGH_HASH_POWER

        random.shuffle(G.peers)

        # if self.adversary != "none":
        #     self.n += 1
        #     if self.adversary == "selfish":
        #         G.peers.append(SelfishAttacker())
        #     else:
        #         G.peers.append(StubbornAttacker())
        #     G.peers[-1].is_fast = True
        #     honest_power = 0.0
        #     for i in range(self.n - 1):
        #         honest_power += G.peers[i].hash_power
        #     G.peers[-1].hash_power = (honest_power * self.alpha) / (1 - self.alpha)
        # for i in range(self.n):
        #     G.peers[i].id = G.peer_counter
        #     G.peer_counter += 1

        normalization_factor = sum(p.hash_power / self.n for p in G.peers)
        for p in G.peers:
            p.initialize_block_mining_distribution(p.hash_power / normalization_factor)

    def form_random_network(self, os):
        self.get_new_peers()
        edge_list = generate_random_graph(G.total_peers)
        print(edge_list)
        os.write(f"{len(edge_list)}\n")
        for edge in edge_list:
            node1 = edge[0]
            node2 = edge[1]
            print(node1, node2)
            os.write(f"{node1} , {node2}\n")
            G.peers[node1].add_edge(G.peers[node2])
            G.peers[node2].add_edge(G.peers[node1])

    def init_events(self):
        for peer in G.peers:
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

        max_txns = G.INT_MAX if max_txns_ <= 0 else max_txns_
        max_blocks = G.INT_MAX if max_blocks_ <= 0 else max_blocks_
        end_time = G.DBL_MAX if end_time_ <= 0 else end_time_
        while self.events:
            self.current_event = min(self.events, key=lambda x: x.timestamp)
            self.current_timestamp = self.current_event.timestamp

            if self.current_event.timestamp > end_time:
                break
            if G.txn_counter >= max_txns:
                break
            if G.blk_counter >= max_blocks:
                break
            self.current_event.run(self)

            self.delete_event(self.current_event)

        self.reset("output/termination_blockchains")
        for p in G.peers:
            filename = f"output/termination_blockchains/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_blockchain(outfile)

        self.complete_non_generate_events()

        self.reset("output/block_arrivals")
        for p in G.peers:
            filename = f"output/block_arrivals/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_arrival_times(outfile)

        self.reset("output/peer_stats")
        for p in G.peers:
            filename = f"output/peer_stats/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_stats(self, outfile)

        print("Total Transactions:", G.txn_counter)
        print("Total Blocks:", G.blk_counter)

    def complete_non_generate_events(self):
        self.has_simulation_ended = True

        for p in G.peers:
            p.next_mining_event = None
            p.next_mining_block = None

        while self.events:
            self.current_event = min(self.events, key=lambda x: x.timestamp)
            self.current_timestamp = self.current_event.timestamp

            if not self.current_event.is_generate_type_event:
                self.current_event.run(self)

            self.delete_event(self.current_event)

        self.reset("output/final_blockchains")
        for p in G.peers:
            filename = f"output/final_blockchains/{p.get_name()}.txt"
            with open(filename, 'w') as outfile:
                p.export_blockchain(outfile)

    def log(self, s):
        if not self.verbose:
            return
        print(f"Time {self.current_timestamp:.5f}: {s}")
