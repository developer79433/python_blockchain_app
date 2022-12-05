class Node:
    def __init__(self):
        # the node's copy of blockchain
        self.blockchain = None
        # the address to other participating members of the network
        self.peers = set()
