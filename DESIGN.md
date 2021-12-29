# CS60, Final Project
# George, Gabe, Boxian and Karim

## Blockchain

A single block will be implemented in class `Block`

The blockchain will be implemented as class `Blockchain`

The Blockchain shall contain:
- `length`: number of blocks
- `chain`: a list of blocks
- `difficulty`: mining difficulty, higher is more difficult

A single block shall contain the following fields:

- `index`: index of the block in the chain
- `data`: data/transactions stored in the block
- `prev_hash`: hash of the previous block's header
- `nonce`: number for proof of work

To add a block, a node must compute the appropriate nonce such that
the hash fits the difficulty requirement.

Difficuly shall increase with depth but also adjust for computation power.

In case of a fork, the node shall keep the longer/ more difficult branch and discard the 
unwanted one. In case of a draw, it shall keep the earliest one.

The block chain shall make available the following methods to the p2p app:

- `Blockchain()` returns a new chain w/ genesis block
- `mine_block(data, prev_hash)` returns a new block containing `data` at the endof `chain`
    **prev_hash is required so that the mutex can be released while mining!!!**
- `get_last_hash()` returns hash of last block
- `verify_block(block)` verify if `block` can be added to `chain`
- `verify_chain()` verify entire `chain` itself. Note that if every addition is valid, then the whole chain should be valid.
- `add_block(block)` verify and update the local records according to the new chain.
    **`add_block` does not check if the addition is valid**
- `get_data()` return the data in the chain in a list
- `get_length()` return the length of the chain
- `Blockchain.to_json()` convert chain to json
- `Blockchain.load_json(json)` load chain from json

## P2P

### API

The following functions implemented in `peer` should be exposed to the application:

- `connect()` connects to tracker, get peer list, set up listening threads to exchange data
- `disconnect()` disconnects with tracker, stop all threads
- `get_data()` return a list of the content of current local block chain
- `add_data(data)` **tries** to add a new block containing data; return 1 on success; 0 on retry; -1 on invalid data

If the mining is unsuccessful because another miner was faster, failure should be returned, and it should keep mining after a short wait.

### Peer

The peer can be implemented with the following components:

- `blockchain` a copy of block chain
- `peer_list` a list of peers
- `listening_thread` this runs at all time, should be started when the peer list is retrieved from the tracker
- `mining_thread` this should be started when the user program calls `add_data`, and stops when mining is finished
- `tracking_thread` this runs at all time, which updates the peer list
- `data_crit` that verifies the validity of data
- locks to protect peer_list and chain

### Exchanging messages

Messages should be exchanged from peer to peer and from peer to tracker.

From peer to peer: 

1. Request blockchain. This message indicates the sender want a copy of the blockchain.

2. Send/Broadcast new block/chain. This message contains an updated block/blockchain that the sender has mined.

From peer to tracker:

1. connect

2. disconnect

From tracker to peer:

1. updated peer_list

### Psuedo Code:

#### connect
1. connect with tracker; get peer list 
2. start tracking thread (combine with 1???)
3. start listening thread

#### disconnect
1. announce to tracker
2. disconnect with all peers
3. stop all threads

#### get_data
1. acquire lock
2. use `get_data` provided by the blockchain class

#### add_data
1. start mining in a different thread, using `mine_block` provided by blockchain
2. when done, **check if the local copy has changed by verifying the newly mined block**
3. if all good, add block and broadcast **careful about TOCTTOU** 
4. if the newly mined block is invalid, (what do we do? do we keep mining or return failure?) 

#### tracking thread
1. listen from tracker, when update is received, acquire lock and update local peer_list

#### mining thread
1. just call `mine_block`. Note that the last hash has to be obtained before `mine_block` runs, to 
release the lock on `chain` before mining.

#### listening thread
This is the hard part. I assume you can listen on multiple sockets at the same time in Python, and wake up
if one socket sends stuff.

1. update connection according to `peer_list`
2. listen on all connection
3. if the message is type 1, send your copy
4. if the message is type 2: (I assume we are only broadcasting new blocks)
    - if the new block works using `verify_block`: update local chain
    - if not, send type 1 message to original sender and get entire chain
    - if chain works (using `verify_chain`) and is **longer** than local chain, use new chain
    - else, discard chain
    

### Tracker

To run tracker all you have to do is create a tracker object and then call `tracker_object.start_listening()`. This can be seen in ***tracker.py***, which is the scipt the user has to launch on babylon1 to begin the tracker.

The tracker can be implemented with the following components:

- `peer_list` a list of peers by their address
- `conns` a list of peers by their connection sockets for the trackers use
- `start_listening_thread` this runs all the time and looks for new peers trying to connect to the server
- `handle_conn` this is a thread that deals with each peers communications (sending them updated lists and looking for diconnection requests)
- `conns` and `peer_list` should be protected by locks

### Exchanging messages

Messages should be exchanged from peer to tracker and from tracker to peer.

1. Peer connects and sends `SYN` to tracker along with their address
2. Server responds by sending all peers an updated `peer_list`
3. When peer is disconnecting they send a `FIN` to tracker along with their address
4. Server responds by sending all remaining peers an updated `peer_list`

### Psuedo Code:

#### connect
1. accept peer connection 
2. append their connection socket to the `conns` list
3. start new thread for new user and wait to recieve their `SYN` before adding them to the `peer_list` and then sending all users an updated `peer_list` with the new connection included by calling the `broadcast_peer_list()`.

#### disconnect
1. peers sends a `FIN` to tracker when it wants to disconnect
2. tracker then removes the peer from `conns` and the `peer_list`.
3. tracker then broadcasts the peer list by calling `broadcast_peer_list()` to all of the remaining peers
4. tracker then breaks the loop and closes that peers connection

#### broadcast
1. tracker loops through all the current connections and sends each peer a `peer_list` that has been made into a string using json.

## Demo Application: Distributed Voting

This is the application that leverages everything discussed above barring the Tracker, which is run seperately, but each Peer is run by calling `distributed_voting.py`, which is explained in the README.md. It is a distributed voting application, which allows everyone with a unqiue voter ID to vote for a candidate of their choice. It also allows to see the current state of the vote and protects against users voting more than once with their same voter ID.

How to interact with it once the program is running. It provides the following prompt for the user once all necessary connections have been established and relevant info/data has been recieved: `Enter option ('a' add record, 'd' display tally, 'q' quit):`
1. If user types `a`:
- They are then prompted to `Enter voter id:`
- Then they are prompted to `Enter choice:`
- Then the mining process begins and if the voter ID is unique then their vote will be appended to the blockchain as a new block. Otherwise if their voter ID is not unique they will be alerted: `Invalid/duplicate Vote!`
2. If the user types `d`:
- They will be presented with the current state of the vote
3. If the user types `q`:
- They will complete the exit handshake with the Tracker and then exit.

***distributed_voting.py*** implements the `VotingMachine` class which allows for the user interactions with the voting process and leverages local functions outside the class to make sure the voting occurs properly and accurately.

### Psuedo Code:

#### start voting:
1. the input info is checked to make sure there is not a duplicate peer. This part will call `check_duplicate`, which checks for duplicates: if the length of the array is the same as the length of the set then there’s no duplicate votes
2. user is promted to either vote, display voting tally or quit
3. if they choose to vote, once they vote, they open a mining thread which looks for updates from other peers making it so their vote does not begin to get mined and added to the blockchain until they have the most up to date version. This part of the code will call `self.mining()` and `make_vote()`, which just returns a json of the voter and their choice to be added to the blockchain.
4. if they choose to tally votes the tally of the votes so far in the blockchain will be displayed. This part will call `tally_votes()`, which just tallies up the votes based on the current blockchain and then prints it.
5. if they choose to quit, they will disconnect from the server and then break the loop.

#### mining
1. first the data is addedd to the block chain by calling `add_data(data)` from Peer
2. if the vote is then successfully added based on the return value of `add_data()`, it prints that the vote was added and exits the function
3. if there is another peer trying to add data and their data is being mined already it waits a random amount of time to try again.
4. if the data is invalid or a duplicate the user will be alerted and it exits the function.



