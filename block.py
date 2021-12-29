# block.py
# Final Project - Gabe Kotsonis, Boxian Wang, George McNulty, Karimi Itani
# implementation of a class for a single block in the blockchain
# NOTE: The structure of this code is partially borrowed from https://www.activestate.com/blog/how-to-build-a-blockchain-in-python/

from hashlib import sha256
import json
import math

class Block:

    def __init__(self, index, data, prev_hash, nonce=0):

        # private instance variables
        self._index = index
        self._nonce = nonce
        self._data = data
        self._prev_hash = prev_hash
        

    # compute hash value of this block
    def compute_hash(self):

        # get json string containing info in this block (sort keys to make sure
        # this is repeatable)
        block_info = json.dumps(vars(self), sort_keys=True)
        
        # get and return hash of this string using sha256 function (put it into hex form)
        res = sha256(block_info.encode()).hexdigest()
        return res

    # getters and setters
    def get_index(self):
        return self._index
    
    def get_data(self):
        return self._data

    def get_prev_hash(self):
        return self._prev_hash

    def get_nonce(self):
        return self._nonce

    def inc_nonce(self):
        self._nonce += 1

    def get_diff(self):
        return 3 + math.floor(self._index ** (1. / 3))

    # convert to and from json
    def to_json(self):
        return json.dumps(vars(self), sort_keys=True)

    @staticmethod
    def load_json(json_string):
        def decoder(d):
            return Block(d['_index'], d['_data'], d['_prev_hash'], d['_nonce'])
        return json.loads(json_string, object_hook=decoder)
    
