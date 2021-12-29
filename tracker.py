# tracker.py - CS 60 Spring 2021
 # Final Project - Gabe Kotsonis, Boxian Wang, George McNulty, Karimi Itani
 # May 25th, 2021
 #
 # This progam creates the class Tracker, which is a server side program using UDP that helps implement the p2p aspect
 # of the larger blockchain project. It essentially tracks the peers updates and forwards these updates to other peers.

# import libraries
from socket import *

from threading import Thread, Lock
import json


class Tracker:
    # need to know my listening address
    def __init__(self, tracker_addr=('babylon1.thayer.dartmouth.edu', 60825)):
        # peer list (p2p port for each node)
        self.peer_list = []
        self.peer_lock = Lock()

        # broadcast list
        self.conns = []
        self.broadcast_lock = Lock()

        # listening socket
        self.listen_sock = socket(AF_INET, SOCK_STREAM)
        self.listen_sock.bind(tracker_addr)

    # handle new connections
    def start_listening(self):
        self.listen_sock.listen()
        print("Tracker Started")

        while True:
            # get new connection
            conn, addr = self.listen_sock.accept()
            print("New connection accepted")

            # add that socket to conns
            self.broadcast_lock.acquire()
            self.conns.append(conn)
            self.broadcast_lock.release()

            # kick off new thread to handle that connection
            handle_thread = Thread(target=self.handle_conn, args=(conn,))
            handle_thread.start()
    
    # thread to handle a connection
    def handle_conn(self, conn):
        while True:
            # receive message
            msg = json.loads(conn.recv(1500).decode())
            # new connection

            if msg['type'] == 'SYN':
                print("Received SYN from peer")
                # add to peer list
                self.peer_lock.acquire()
                self.peer_list.append(msg['addr'])
                self.peer_lock.release()

                # broadcast update
                self.broadcast_peer_list()

            # stop connection
            elif msg['type'] == 'FIN':
                print("Received FIN from peer")
                # remove peer from peer list 
                self.peer_lock.acquire()
                self.peer_list.remove(msg['addr'])
                self.peer_lock.release()

                # remove connecton from broadcast list
                self.broadcast_lock.acquire()
                self.conns.remove(conn)
                self.broadcast_lock.release()

                # broadcast update
                self.broadcast_peer_list()
                break

        # clean up
        conn.shutdown(SHUT_RDWR)
        conn.close()
        
    
    def broadcast_peer_list(self):
        # codify peer list
        self.peer_lock.acquire()
        peer_list = json.dumps(self.peer_list).encode()
        self.peer_lock.release()

        # broadcast it
        self.broadcast_lock.acquire()
        for conn in self.conns:
            conn.send(peer_list)
        self.broadcast_lock.release()

if __name__ == "__main__":
    Tracker().start_listening()