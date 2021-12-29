# peer.py - CS 60 Spring 2021
 # Final Project - George McNulty, Karimi Itani, Gabe Kotsonis, Boxian Wang
 # May 25th, 2021
 #
 # This progam creates a malicious class Peer, which is a client side program using TCP that helps implement the p2p aspect
 # of the larger blockchain project. It interacts with the tracker which helps it communicate with the other peers in the network.
 # The malicious peer sends harmful messages and bad chains to disrupt other peers

# import libraries
from socket import *
from threading import Thread, Lock
from blockchain import Blockchain
from block import Block
import time
import json
from hashlib import sha256

class Peer:
    # NEED self_addr (for p2p) and tracker_addr to initialize
    def __init__(self, self_addr=('babylon5.thayer.dartmouth.edu', 60824), 
        tracker_addr=('babylon1.thayer.dartmouth.edu', 60825)):

        # Blockchain1 does not satisfy proof of work
        self.blockchain1 = Blockchain()
        self.blockchain1.add_block(Block(1, 'not valid or malicious stuff here', self.blockchain1.get_last_hash()))
        # Blockchain2 does not have the correct hash chaining
        self.blockchain2 = Blockchain()
        self.blockchain2.add_block(Block(1, 'evil stuff', sha256("nonsense".encode()).hexdigest()))

        # Peer List
        self.peer_list = []
        self.peer_lock = Lock()

        # Threads
        self.tracker_thread = Thread(target=self.listen_from_tracker)
        self.peer_thread = Thread(target=self.harass_peers)

        # Address of the tracker, and address of itself (for p2p)
        self.tracker_addr = tracker_addr
        self.self_addr = self_addr

        # Variable to stop threads
        self.stop = False
        self.stop_lock = Lock()



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
        
    
    def disconnect(self):
        self.peer_thread.join()
        # change stop to true
        self.stop_lock.acquire()
        self.stop = True
        self.stop_lock.release()

        # wait for threads to die
        self.tracker_thread.join()
        

        print("Peer disconencted")

    #################### THREADS ##############################

    # content of tracking thread, listens from tracker and update peer list
    def listen_from_tracker(self):
        # send SYN and my address
        print("Peer connectected to tracker")
        syn_msg = {'type': 'SYN', 'addr': self.self_addr}
        self.tracker_sock.connect(self.tracker_addr)
        self.tracker_sock.send(json.dumps(syn_msg).encode())

        # listen; update peer list; wait for at most 5 seconds
        self.tracker_sock.settimeout(5)
        print("Peer now listening to tracker")
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
        print("Peer disconnected from tracker")
        # close connection
        self.tracker_sock.shutdown(SHUT_RDWR)
        self.tracker_sock.close()

    # broadcast bad chains
    def harass_peers(self):

        # forming message
        msg1 = {'type': 'CHAIN', 'data': self.blockchain1.to_json()}
        msg2 = {'type': 'CHAIN', 'data': self.blockchain1.to_json()}
        # harass peers 3 times
        print("Harassing")
        for i in range(3):
            self.peer_lock.acquire()
            for p in self.peer_list:
                # sending evil messages
                time.sleep(3)
                if p != self.self_addr:
                    self.peer_sock.sendto(json.dumps(msg1).encode(), p)
                    time.sleep(1)
                    self.peer_sock.sendto(json.dumps(msg2).encode(), p)
            self.peer_lock.release()
        
if __name__ == "__main__":
    p = Peer()
    p.connect()
    p.disconnect()
