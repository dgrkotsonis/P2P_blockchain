# CS60 Spring 2021
# Project Title: Distributed Voting Using Peer-to-Peer Blockchain

## Code Structure

Our code is split among a number of files 

### Main Files

The basic functionality for our project is implemented in 5 main files: block.py, blockchain.py, peer.py, tracker.py, and distributed_voting.py

#### block.py

Our block.py file contains implementation of the Block class. The Block class contains the functionality of a single block in the blockchain

#### blockchain.py

Blockchain.py implements the Blockchain class, which draws on the functionality of the Block class. The blockchain class maintains the functionality of the entire blockchain, providing the ability to create a new chain, mine new blocks, add blocks to the chain, and validate specific blocks as well as the entire blockchain.

#### peer.py

Our peer.py file contains the implementation of the Peer class. The Peer class is a client side program using UDP to implement the peer-to-peer functionality of the larger project. The Peer class runs multiple threads, and interacts with the tracker via a TCP connection, to consitently receive and update the list of peer addresses locally. By utilizing the functionality of the blockchain, the peer.py file is able to mine blocks, add them to the chain, and receive new blocks in the chain from other peers.

#### tracker.py

Our tracker.py file contains the implementation of the Tracker class, which is a server-side program that helps facilitate communication between peers by tracking peer updates and fowarding these updates to other peers in the network.

#### distributed_voting.py

Our distributed_voting.py file contains the implementation of our demo application: distributed voting (if that wasn't already clear!). In addition to containing a VotingMachine class that prompts peers for input to interact with the voting mechanism, it provides methods to tally up votes from peers and checks that no duplicate votes are added to the blockchain.

### Test Files

In addition to our five main files, our project directory contains a few files used to test the functionality of our project: test_peer.py, test_tracker.py, and malicious_peer.py.

#### test_peer.py

Our test_peer.py file simply contains a main function that creates a new peer, connects to the network, then adds data to the blockchain, and waits to receive new updates to the blockchain by other users, before printing the full blockchain and disconnecting.

#### test_tracker.py

Like our test_peer.py file, our test_tracker.py file simply contains a main function that calls the methods provided by our Tracker class. It creates a new tracker object, and then begins listening for new connections, and handles them appropriately.

**THE ABOVE TWO FILES ARE USED FOR INTERNAL TESTING ON THE P2P BLOCKCHAIN ONLY AND IS NOT MEANT TO BE TESTS FOR THE APPLICATION**

**TO TEST THE APPLICATION YOU MUST USE `distributed_voting.py` and `malicious_peer.py`**

#### malicious_peer.py

Our malicious_peer.py file is used mainly to demonstrate how our blockchain handles disruptions and invalid blocks. This file provides the a Peer class very similar to in peer.py, except it has a method called "harrass_peers" which sends a number of invalid messages and bad chains that force other peers in the network to demonstrate how these disruptions are handled.

## Code Usage and Compilation

launch tracker by running tracker in b1 ```python3 tracker.py```, then in other terminals run peers in different servers by calling ```python3 distributed_voting.py [server they are on] [port number for the connection, which in our case is 60806]```

For example `python3 distributed_voting.py babylon3.thayer.dartmouth.edu 60844`.

After that, individual peers will be prompted about what they want to do, and then can vote or view the tally by interacting with the text interface. 
Some intervening messages (starting with two asterisks) shall be displayed, but they are for the internals of the blockchain and can be safely ignored. The tally of votes shall be displayed as a dict.

Each individual peer must be run on a different server than the next. (Preferably not on the tracker server)

To run a peer that continuously sends malicious attacks to the other peers, run ```python3 malicious_peer.py```. NOTE: This peer will be run on babylon5 and cannot have any other peers running on that server as well. It also must be run when there are other peers already on the network to demonstrate its use.

### WHEN RUNNING TRACKER, TEST TRACKER IS DEFAULT TO BE RUN ON BABYLON1. TO CHANGE IT YOU WILL HAVE TO CHANGE THE SERVER_ADDR PARAMETER WHICH WE DIDN'T BOTHER WITH

## Extra Features and Notes

**Extra Feature: This implementation of blockchain increases difficulty as as function of the length of the blockchain, using `difficulty = floor(3 + length^(1/3))`.**

It also adds 5 extra seconds in mining purely for the sake of demonstration and can be removed to make it run faster
