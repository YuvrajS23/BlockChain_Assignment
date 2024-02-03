import random
from typing import Union

class Link:
    def __init__(self, peer, is_fast):
        self.peer = peer
        # 5Mbps = 625KBps
        # 100Mbps = 12500KBps
        self.c = 12500 if (peer.is_fast and is_fast) else 625  # KBps
        # exponential distribution with mean 96kbits/c = 12KB/c , lambda = c/12
        self.exp = random.expovariate(1 / (self.c / 12))
        # ro chosen from uniform distribution between 10ms and 500ms
        self.ro = random.uniform(0.01, 0.5)

    def get_delay(self, length):
        d = self.exp
        return self.ro + length / self.c + d

# Example usage:
# peer = some_peer_object
# is_fast_link = True  # or False
# link = Link(peer, is_fast_link)
# message_length = 1024  # in KB
# delay = link.get_delay(message_length)
