import random
random.seed(60)
# Class for Link
class Link:
    def __init__(self, peer, is_fast):
        # Peer to whom the link is connected
        self.peer = peer
        # 5Mbps = 625KBps
        # 100Mbps = 12500KBps
        # c: link rate 
        self.c = 12500 if (peer.is_fast and is_fast) else 625  # KBps
        # ro chosen from uniform distribution between 10ms and 500ms
        # ro: speed of light propagation delay
        self.ro = random.uniform(0.01, 0.5)

    # returns the delay for a message of size length KB
    def get_delay(self, length):
        # exponential distribution with mean 96kbits/c = 12KB/c , lambda = c/12
        d = random.expovariate(1 / (self.c / 12))
        return self.ro + length / self.c + d

