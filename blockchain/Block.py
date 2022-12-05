import json
from hashlib import sha256


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    @classmethod
    def from_json(cls, block_data):
        return cls(block_data["index"],
            block_data["transactions"],
            block_data["timestamp"],
            block_data["previous_hash"],
            block_data["nonce"]
        )

    def to_json(self):
        return self.__dict__
