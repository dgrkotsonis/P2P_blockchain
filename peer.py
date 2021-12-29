# peer.py - CS 60 Spring 2021
 # Final Project - George McNulty, Karimi Itani, Boxian Wang, Gabe Kotsonis
 # May 25th, 2021
 #
 # This progam creates the class Peer, which is a client side program using UDP that helps implement the p2p aspect
 # of the larger blockchain project. It interacts with the tracker which helps it communicate with the other peers in the network.

# import libraries
from socket import *
from threading import Thread, Lock
from blockchain import Blockchain
from block import Block
import time
import json

class Peer:
    # NEED self_addr (for p2p) and tracker_addr to initialize
    def __init__(self, self_addr=('babylon1.thayer.dartmouth.edu', 60806), 
        tracker_addr=('babylon1.thayer.dartmouth.edu', 60825), data_crit=lambda new_data, all_data: True):
        # Blockchain, start with genesis
        self.blockchain = Blockchain()
        self.chain_lock = Lock()

        # Peer List
        self.peer_list = []
        self.peer_lock = Lock()

        # Threads
        self.tracker_thread = Thread(target=self.listen_from_tracker)
        self.peer_thread = Thread(target=self.listen_from_peers)

        # Address of the tracker, and address of itself (for p2p)
        self.tracker_addr = tracker_addr
        self.self_addr = self_addr

        # Variable to stop threads
        self.stop = False
        self.stop_lock = Lock()

        # Function for controlling data addition
        self.data_crit = data_crit


    ################### EXPOSED API #######################

    def connect(self):
        # start tracking thread
        self.tracker_sock = socket(AF_INET, SOCK_STREAM)
        self.tracker_thread.start()

        time.sleep(0.5) # sleep to make sure thread got peer list before doing p2p

        # start listening thread
        self.peer_sock = socket(AF_INET, SOCK_DGRAM)
        self.peer_sock.bind(self.self_addr)
        self.peer_thread.start()
        print("**Peer listening for messages**")
        
    
    def disconnect(self):
        # change stop to true
        self.stop_lock.acquire()
        self.stop = True
        self.stop_lock.release()

        # wait for threads to die
        self.tracker_thread.join()
        self.peer_thread.join()

        print("**Peer disconencted**")

    def get_data(self):
        # get lock
        self.chain_lock.acquire()

        # return list
        res = self.blockchain.get_data()

        # release lock
        self.chain_lock.release()

        return res


    def add_data(self, data):
        # get lock, get hash, length
        self.chain_lock.acquire()
        prev_hash = self.blockchain.get_last_hash()
        length = self.blockchain.get_length()
        all_data = self.blockchain.get_data() # exclude the genesis block!
        # release lock
        self.chain_lock.release()
        if not self.data_crit(data, all_data): return -1
        # start mining
        res = []
        self.mining_thread = Thread(target=self.mine, args=(data, prev_hash, length, res))
        self.mining_thread.start()
        print("**Mining block**")

        # wait for finish and retrieve resulting block
        self.mining_thread.join()
        new_block = res[0]

        # get lock
        self.chain_lock.acquire()

        # check validity
        if self.blockchain.verify_block(new_block):
            print("**Block Verified, broadcasting...**")
            # publicize new block
            self.blockchain.add_block(new_block)
            self.chain_lock.release()
            self.broadcast_block(new_block)
            return 1

        else:
            print("Verify failed; chain changed during mining")
            # return failure
            self.chain_lock.release()
            return 0

    #################### THREADS ##############################

    # content of tracking thread, listens from tracker and update peer list
    def listen_from_tracker(self):
        # send SYN and my address
        print("**Peer connectected to tracker**")
        syn_msg = {'type': 'SYN', 'addr': self.self_addr}
        self.tracker_sock.connect(self.tracker_addr)
        self.tracker_sock.send(json.dumps(syn_msg).encode())

        # listen; update peer list; wait for at most 5 seconds
        self.tracker_sock.settimeout(5)
        print("**Peer now listening to tracker**")
        while True:
            try:
                track_msg = json.loads(self.tracker_sock.recv(1500).decode())
                self.peer_lock.acquire()
                self.peer_list = [tuple (i) for i in track_msg] # acquire lock and update peer list
                self.peer_lock.release()

            except timeout:  # check if we disconnected
                self.stop_lock.acquire()
                stop = self.stop
                self.stop_lock.release()
                if stop: 
                    break

        # send FIN
        fin_msg = {'type': 'FIN', 'addr': self.self_addr}
        self.tracker_sock.send(json.dumps(fin_msg).encode())
        print("**Peer disconnected from tracker**")
        # close connection
        self.tracker_sock.shutdown(SHUT_RDWR)
        self.tracker_sock.close()

    
    def listen_from_peers(self):
        # First request a copy of blockchain, start by finding a peer (if any)
        valid_peer = None
        self.peer_lock.acquire()

        for p in self.peer_list:
            if p != self.self_addr: 
                valid_peer = p

        self.peer_lock.release()

        # ask it for blockchain
        if valid_peer is not None:
            self.send_req(valid_peer)
        
        # Then start handling messages; wait for at most 5 seconds
        self.peer_sock.settimeout(5)
        while True:

            try:
                packet, addr = self.peer_sock.recvfrom(65536)
                peer_msg = json.loads(packet.decode())

                # if got a block
                if peer_msg['type'] == 'BLOCK':
                    print("**Received a block from peer " + addr[0] + "**")
                    new_block = Block.load_json(peer_msg['data'])
                    self.chain_lock.acquire()

                    # accept, or request entire chain, based on verification
                    if self.blockchain.verify_block(new_block) and self.data_crit(new_block.get_data(), self.blockchain.get_data()):
                        self.blockchain.add_block(new_block)
                        self.chain_lock.release()
                        print("**New block accepted**")

                    else:
                        self.chain_lock.release()
                        print("**New block does not match; sending request for whole chain**")
                        self.send_req(addr)

                # if got a chain
                elif peer_msg['type'] == 'CHAIN':
                    print("**Received a chain from peer " + addr[0] + "**")
                    new_chain = Blockchain.load_json(peer_msg['data'])
                    self.chain_lock.acquire()

                    # accept if new chain is longer and valid
                    if new_chain.verify_chain() and self.data_crit(None, new_chain.get_data()) and new_chain.get_length() > self.blockchain.get_length():
                        print("**New chain accepted**")
                        self.blockchain = new_chain
                    else:
                        print("**New chain rejected**")

                    self.chain_lock.release()

                # if got a request
                elif peer_msg['type'] == 'REQ':
                    print("**Received a request from peer " + addr[0] + "**")
                    self.send_blockchain(addr)

            except timeout:
                # check for stoppage
                self.stop_lock.acquire()
                stop = self.stop
                self.stop_lock.release()
                if stop: 
                    break

        # clean up
        self.peer_sock.close()
    
    # mining thread, simply invoke Blockchain.mineblock
    def mine(self, data, prev_hash, length, res):
        new_block = Blockchain.mine_block(data, prev_hash, length)
        res.append(new_block)
    
    ############### SENDING TO TRACKER & PEERS #############


    # broadcast block to all peers except self
    def broadcast_block(self, new_block):
        self.peer_lock.acquire()

        # forming block message
        block_msg = {'type': 'BLOCK', 'data': new_block.to_json()}
        for p in self.peer_list:
            # sending block message
            if p != self.self_addr:
                self.peer_sock.sendto(json.dumps(block_msg).encode(), p)

        print("**Block sent to all peers**")
        self.peer_lock.release()


    # send entire chain to one peer
    def send_blockchain(self, peer):
        self.chain_lock.acquire()


        # forming chain message
        chain_msg = {'type': 'CHAIN', 'data': self.blockchain.to_json()}
        self.chain_lock.release()

        # send it 
        print("**Blockchain sent to peer " + peer[0] + "**")
        self.peer_sock.sendto(json.dumps(chain_msg).encode(), peer)
        

    # send a request and retrieve block chain from a peer
    def send_req(self, peer):
        # forming request
        req_msg = {'type': 'REQ'}

        # send it
        print("**Request sent to peer " + peer[0] + "**")
        self.peer_sock.sendto(json.dumps(req_msg).encode(), peer)
