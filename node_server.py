import os
import sys
import signal
import atexit
import json
import time
import logging

from flask import Flask, request
import requests

from blockchain import Block, Node


logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
chain_file_name = os.environ.get('DATA_FILE')
if chain_file_name is None:
    data = None
else:
    with open(chain_file_name, 'r') as chain_file:
        raw_data = chain_file.read()
        if raw_data is None or len(raw_data) == 0:
            data = None
        else:
            data = json.loads(raw_data)

if data is None:
    node = Node()
else:
    node = Node.from_json(data)


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    global node
    return json.dumps(node.to_json())


def save_chain():
    if chain_file_name is not None:
        with open(chain_file_name, 'w') as chain_file:
            chain_file.write(get_chain())


def exit_from_signal(signum, stack_frame):
    sys.exit(0)


atexit.register(save_chain)
signal.signal(signal.SIGTERM, exit_from_signal)
signal.signal(signal.SIGINT, exit_from_signal)


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    global node
    tx_data = request.get_json()
    required_fields = ["author", "content"]

    for field in required_fields:
        if not tx_data.get(field):
            return "Invalid transaction data", 404

    tx_data["timestamp"] = time.time()

    node.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    global node
    new_block_idx = node.mine_unconfirmed_transactions()
    if new_block_idx == 0:
        return "No transactions to mine"
    else:
        return "Block #{} is mined.".format(new_block_idx)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    global node
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    # Add the node to the peer list
    node.add_peer(node_address)

    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global node
        # update chain and the peers
        node = Node.from_json(response.json())
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block.from_json(block_data)

    proof = block_data['hash']
    try:
        global node
        node.add_block(block, proof)
    except:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    global node
    return json.dumps(node.blockchain.unconfirmed_transactions)


# Uncomment this line if you want to specify the port number in the code
#app.run(debug=True, port=8000)
