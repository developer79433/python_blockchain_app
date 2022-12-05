import requests
import json

from .Blockchain import Blockchain


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

    def add_peer(self, peer_address):
        self.peers.add(peer_address)

    def add_block(self, block, proof):
        self.blockchain.add_block(block, proof)

    def consensus(self):
        """
        Our naive consnsus algorithm. If a longer valid chain is
        found, our chain is replaced with it.
        """
        longest_chain = None
        current_len = self.blockchain.length

        for peer in self.peers:
            response = requests.get('{}chain'.format(peer))
            length = response.json()['length']
            chain = response.json()['chain']
            if length > current_len and Blockchain.check_chain_validity(chain):
                current_len = length
                longest_chain = chain

        if longest_chain:
            self.blockchain = longest_chain
            return True

        return False

    def add_new_transaction(self, tx_data):
        return self.blockchain.add_new_transaction(tx_data)

    def announce_new_block(self, block):
        """
        A function to announce to the network once a block has been mined.
        Other blocks can simply verify the proof of work and add it to their
        respective chains.
        """
        for peer in self.peers:
            url = "{}add_block".format(peer)
            headers = {'Content-Type': "application/json"}
            requests.post(url,
                        data=json.dumps(block.to_json(), sort_keys=True),
                        headers=headers)

    def mine_unconfirmed_transactions(self):
        result = self.blockchain.mine()
        if result:
            # Making sure we have the longest chain before announcing to the network
            chain_length = self.blockchain.length
            self.consensus()
            if chain_length == self.blockchain.length:
                # announce the recently mined block to the network
                self.announce_new_block(self.blockchain.last_block)
            return self.blockchain.last_block.index
        else:
            return 0
