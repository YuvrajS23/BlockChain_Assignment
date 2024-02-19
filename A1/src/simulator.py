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

# Class Simulator simulates the running of the blockchain network among peers
class Simulator:
    # Initializing values at the start of simulation
    def __init__(self, n_, z0_, z1_, Ttx_, Tk_, verbose_, invalid_txn_prob_, invalid_block_prob_):
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
        G.global_genesis = Block(None)
        G.global_genesis.setParent(None)
        G.total_peers = self.n
        G.Ttx = self.Ttx
        G.Tk = self.Tk
        # Event queue
        self.events = set()
        self.current_event = None

    # Returns the name of the simulator with all the input parameters
    def getName(self):
        return f"Simulator-{self.n}-{self.z0}-{self.Ttx}-{self.Tk}-{self.z1}-{self.verbose}-{self.invalid_txn_prob}-{self.invalid_block_prob}"

    # Resets a dirpath i.e clears it
    def reset(self, dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)
        os.makedirs(dir_path)

    # Generate self.n new peers and initialize the properly with appropriate link speeds and hash powers
    def get_new_peers(self):

        G.peers = [Peer() for _ in range(self.n)]
        # print(G.peers[5].id)

        for i in range(self.slow_peers):
            G.peers[i].is_fast = False
        for i in range(self.slow_peers, self.n):
            G.peers[i].is_fast = True



        random.shuffle(G.peers)
        # print([G.peers[k].is_fast for k in range(self.n)])
        for i in range(self.lowhashpower):
            G.peers[i].hash_power = G.LOW_HASH_POWER
        for i in range(self.lowhashpower, self.n):
            G.peers[i].hash_power = G.HIGH_HASH_POWER

        normalization_factor = sum(p.hash_power for p in G.peers)
        for p in G.peers:
            p.initialize_block_mining_distribution(p.hash_power / normalization_factor)

    # Forms a random connected graph between peers and writes the edges in a file
    # Uses the generate_random_graph function of graph_generator
    def form_random_network(self, os):
        edge_list = generate_random_graph(G.total_peers)
        # print(edge_list)
        for edge in edge_list:
            node1 = edge[0]
            node2 = edge[1]
            # print(node1, node2)
            os.write(f"{node1} {node2}\n")
            G.peers[node1].add_edge(G.peers[node2])

    # Starts txn and blk mining for every peer
    def init_events(self):
        for peer in G.peers:
            peer.schedule_next_transaction(self)
            peer.schedule_next_block(self)

    # Adds an event to the event queue
    def add_event(self, event):
        event.timestamp += self.current_timestamp
        self.events.add(event)

    # Deletes an event from the event queue
    def delete_event(self, event):
        assert event is not None
        self.events.remove(event)
        del event

    # Runs the simulation
    def run(self, end_time_, max_txns_, max_blocks_):
        # Generate peers
        self.get_new_peers()

        # Form graph
        self.reset("output")
        filename = "output/peer_network_edgelist.txt"
        with open(filename, 'w') as outfile:
            self.form_random_network(outfile)

        # Initialize events
        self.init_events()
        self.has_simulation_ended = False

        # Initializing the break conditions for simulation
        max_txns = G.INT_MAX if max_txns_ <= 0 else max_txns_
        max_blocks = G.INT_MAX if max_blocks_ <= 0 else max_blocks_
        end_time = G.DBL_MAX if end_time_ <= 0 else end_time_
        # Simulation
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

        # Exporting blockchain at the end of simulations
        self.reset("output/termination_blockchains")
        for p in G.peers:
            filename = f"output/termination_blockchains/{p.getName()}.txt"
            with open(filename, 'w') as outfile:
                p.export_blockchain(outfile)

        # Runs the non generate type events
        self.complete_non_generate_events()

        # Export block arrival times in file
        self.reset("output/block_arrivals")
        for p in G.peers:
            filename = f"output/block_arrivals/{p.getName()}.txt"
            with open(filename, 'w') as outfile:
                p.export_arrival_times(outfile)

        # Exporting peer stats
        self.reset("output/peer_stats")
        for p in G.peers:
            filename = f"output/peer_stats/{p.getName()}.txt"
            with open(filename, 'w') as outfile:
                p.export_stats(self, outfile)

        # Num txns and blks generated
        print("Total Transactions:", G.txn_counter)
        print("Total Blocks:", G.blk_counter)

    # Runs the non generate type events only
    def complete_non_generate_events(self):
        self.has_simulation_ended = True

        for p in G.peers:
            p.next_mining_event = None
            p.next_mining_block = None
        # Run
        while self.events:
            self.current_event = min(self.events, key=lambda x: x.timestamp)
            self.current_timestamp = self.current_event.timestamp

            if not self.current_event.is_generate_type_event:
                self.current_event.run(self)

            self.delete_event(self.current_event)
        # Exports final blockchain
        self.reset("output/final_blockchains")
        for p in G.peers:
            filename = f"output/final_blockchains/{p.getName()}.txt"
            with open(filename, 'w') as outfile:
                p.export_blockchain(outfile)

    # Logs the stuff occurring while simulation
    # Used for debugging mostly
    def log(self, s):
        if not self.verbose:
            return
        print(f"Time {self.current_timestamp:.5f}: {s}")
