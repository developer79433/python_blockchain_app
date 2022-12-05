from .Blockchain import Blockchain
from .Block import Block


class Node:
    def __init__(self, json_data=None):
        if json_data is None:
            # the node's copy of blockchain
            self.blockchain = Blockchain()
            # the address to other participating members of the network
            self.peers = set()
        else:
            self.blockchain = Blockchain.create_chain_from_dump(json_data['chain'])
            self.peers = set()
            self.peers.update(json_data['peers'])