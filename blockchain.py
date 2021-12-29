# blockchain.py
# Final Project - Gabe Kotsonis, Boxian Wang, George McNulty, Karimi Itani
# implementation of a class for the entire blockchain
# NOTE: The structure of this code is partially borrowed from https://www.activestate.com/blog/how-to-build-a-blockchain-in-python/

import time
import json
from block import Block


class Blockchain:

    def __init__(self, init=True, chain=[], length=0):
        
        if init:
            # initialize empty chain and pending transactions as private variables
            self._chain = []

            # start with 0 blocks
            self._length = 0

            # create block object for this initial block
            initial_block = Block(0, "", "0")
            
            # add this block to the chain
            self.add_block(initial_block)
        else:
             # initialize empty chain and pending transactions as private variables
            self._chain = chain 

            # start with 0 blocks
            self._length = length

    def get_length(self):
        return self._length
    
    def get_data(self):
        return [i.get_data() for i in self._chain][1:]
    
    # add a new block to the chain, no verification is performed
    def add_block(self, block):

        # append to chain
        self._chain.append(block)

        # adjust length
        self._length += 1

    # return a mined block based on the previous hash
    @staticmethod
    def mine_block(data, prev_hash, index):

        new_block = Block(index, data, prev_hash)
        # get the hash of this block
        hash = new_block.compute_hash()

        # re-compute hash with new nonce until we get a hash that starts with
        # "difficulty" number of zeroes
        while not hash.startswith('0' * new_block.get_diff()):

            # increment the nonce, recompute hash
            new_block.inc_nonce()
            hash = new_block.compute_hash()
        
        # set the value of the proof to this final computed hash
        time.sleep(5) # wait here to create a feeling of hard work... use this to test fork
        return new_block

    # return the hash of the last block in the chain
    def get_last_hash(self):
        return self._chain[-1].compute_hash()

    # check if a proof is valid
    def verify_block(self, block):
        # check the proof and hash
        return (block.compute_hash().startswith('0' * block.get_diff())) and (self.get_last_hash() == block.get_prev_hash())
    
    # verifies the whole chain
    def verify_chain(self):
        for i in range(1, self._length):
            block = self._chain[i]
            if (not block.compute_hash().startswith('0' * block.get_diff())): return False # satisfies proof of work
            if (block.get_prev_hash() != self._chain[i - 1].compute_hash()): return False # check hash chaining
        return True
    
    # to and from json
    def to_json(self):
        return json.dumps(vars(self), sort_keys=True, default=Block.to_json)
    
    @staticmethod
    def load_json(json_string):
        chain_dict = json.loads(json_string)
        block_decoder = lambda d: Block(d['_index'], d['_data'], d['_prev_hash'], d['_nonce'])
        chain = [block_decoder(json.loads(i)) for i in chain_dict['_chain']]
        length = chain_dict['_length']
        return Blockchain(init=False, chain=chain, length=length)

