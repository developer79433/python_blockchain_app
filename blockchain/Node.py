from .Blockchain import Blockchain
from .Block import Block


class Node:
    def __init__(self, chain=None, peers=None):
        if chain is None:
            # the node's copy of blockchain
            self.blockchain = Blockchain()
        else:
            self.blockchain = chain
        if peers is None:
            # the address to other participating members of the network
            self.peers = set()
        else:
            self.peers = peers

    @classmethod
    def from_json(cls, node_data):
        blockchain = Blockchain.from_json(node_data['chain'])
        peers = set()
        peers.update(node_data['peers'])
        return cls(chain=blockchain, peers=peers)

    def to_json(self):
        return {
            "length": self.blockchain.length,
            "chain": self.blockchain.to_json(),
            "peers": list(self.peers)
        }
