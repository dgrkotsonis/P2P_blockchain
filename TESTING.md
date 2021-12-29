# CS60, Final Project
# George, Gabe, Boxian and Karim

## Testing

We set out to test the following functionalities:

1. That the Tracker maintains a constantly updating list of peers
2. That it works with 3+ users
3. That the Peers are always made aware of changes in the P2P network by the Tracker
4. That each peer can maintain a copy of the most up-to-date blockchain
5. That the blocks can be broadcast to all peers by a peer
6. That the blocks can be verified and added to the local blockchain
7. That our program is immune to forks
8. That our blockchain is immune to invailid transactions and modifications to blocks.
9. That the no voters with the same voter ID can add a vote to the blockchain


### Tests

***NOTE***: Refer to the flow of the Tracker, Peer 1, Peer 2 and Peer 3 at the bottom to see how they all interact. I test all of the functionalities in this flow to demonstrate that the program works! Messages starting with 2 asterisks are internal prints that demonstrate the flow of the blockchain.

1. To test this we added a print statement on the Tracker that prints an updated list everytime a Peer joins or leaves the server. It worked as it should have. Once this test was complete we added print statements on the Tracker that still remain, which signifies when a new Peer has joined by printing "New connection accepted" followed by "Received SYN from peer" and when a peer leaves the trackers prints "Received FIN from peer." When running our program you will see these print statements work precisely as they should. You can see this by looking at the Tracker output in tandem with how the Peers join and leave.

2. We tested the program with 3 users: The Tracker was run on Babylon1, then the peers on Babylon2-4. All functionalities worked as they should. You will see this works when you test. Below you can see that three peers are present in the flows.

3. We included print statments that print out the address of each user when they joined or left the server to prove this funcationality worked. However, this is largely unnecessary because the fact that all the funcitonalities of the blockchain updates worked suggests that the Peers were always in possession of updated lists.

4. We print out the blockchain everytime an update is made. During your testing you might see something like: "Received a block from peer 129.170.65.171" followed by a print out of the new chain in the form of a list. After many many tests, we are certain this works properly. You can see this in the flows below!

5. The fact that each Peer is recieveing the blocks and printing them each time suggests that the broadcasting through p2p works! This is evident in the flows below!

6. Our print statments are strategically placed to display that all the blocks can be verified and added to the local blockchain. You will see that this functionallity works when you run our program. Everytime one user adds to the chain the others will print it out after it has been verrified: See below.

7. To make our program immune from forks we implmented a functionality in Peer that returns 0 when `add_data()` is called if there has been a change to a block that not every user has to let the local script know that they cannot yet add to the blockchain. The distributing_voting script will then know to wait for a random short period of time before trying again to add the data. This test hard to demonstrate here, but if you attempt to add to the blockchain from two different peers at the same or similar times, you will see that both will be added, one after the other.

8. To test this Boxian constructed a script called ***malicious_peer.py*** that pretends to be a Peer and connects to the Tracker and P2P network, but then attempts to continuoulsy add unacceptable data to the blockchain. It sends two types of bad data: the first does not statisfy proof of work and the second does not have the correct hash chaining. The other peers respond well by printing first: "Received a chain from peer 129.170.65.173," followed by: "New chain rejected." Then when the chain is printed after this you will see that the bad data has not been added. In terms of making sure there are no modifications made the blockchain, while we do not explicitly test for this, it is clear that to modify prior data malicious peers would have to modify the whole chain that follows, which is possible only if the malicious peer has more than 51% of the total computation power. We execute malicious peer below after Peer 3 leaves and you can see how Peer 1 and 2 react to it in the flows.

9. This is prevented in the ***distributed_voter.py*** script and when you attmempt to add a vote with a voter ID that has already been used the code will output the following: "Invalid/duplicate Vote!". You can see Peer 3 attempt to use a voter ID that has already been used by Peer 1 and it fails!.


#### Tracker

***NOTE***: the parts in parentheses were not actually printed out. I just added them for clarity.

```
f00321f@babylon1:~/project-boxian-james-karim-george$ python3 test_tracker.py
Tracker Started
New connection accepted
Received SYN from peer (Babylon3 — Peer 1)
New connection accepted
Received SYN from peer (Baylon2 — Peer 2)
New connection accepted
Received SYN from peer (Babylon4 — Peer 3)
Received FIN from peer (Babylon4 — Peer 3)
New connection accepted
Received SYN from peer (Babylon5 - Malicious Peer)
Received FIN from peer (Babylon2 - Peer 2)
Received FIN from peer (Babylon3 — Peer 1)
```

#### Peer 1 (Bablyon3)

```
f00321f@babylon3:~/project-boxian-james-karim-george$ python3 distributed_voting.py babylon3.thayer.dartmouth.edu 60806
**Peer connectected to tracker**
**Peer now listening to tracker**
**Peer listening for messages**
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a request from peer 129.170.65.171**
**Blockchain sent to peer 129.170.65.171**
d
{}
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a block from peer 129.170.65.171**
**New block accepted**
d
{'Obama': 1}
Enter option ('a' add record, 'd' display tally, 'q' quit): a
Enter voter id: Karim
Enter choice: McCain
Mining started, please wait...
Enter option ('a' add record, 'd' display tally, 'q' quit): Mining block
**Block Verified, broadcasting...**
**Block sent to all peers**
Vote is successfully added.

**Received a block from peer 129.170.65.173**
**New block accepted**
d
{'Obama': 2, 'McCain': 1}
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a chain from peer 129.170.65.174**
**New chain rejected**
**Received a chain from peer 129.170.65.174**
**New chain rejected**
**Received a chain from peer 129.170.65.174**
**New chain rejected**
**Received a chain from peer 129.170.65.174**
**New chain rejected**
q
Quitting...
**Peer disconnected from tracker**
**Peer disconencted**
```

#### Peer 2 (Babylon2)

```
f00321f@babylon2:~/project-boxian-james-karim-george$ python3 distributed_voting.py babylon2.thayer.dartmouth.edu 60806
**Peer connectected to tracker**
**Peer now listening to tracker**
**Request sent to peer babylon3.thayer.dartmouth.edu**
**Peer listening for messages**
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a chain from peer 129.170.65.172**
**New chain rejected**
**Received a request from peer 129.170.65.173**
**Blockchain sent to peer 129.170.65.173**
d
{}
Enter option ('a' add record, 'd' display tally, 'q' quit): a 
Enter voter id: george
Enter choice: Obama
Mining started, please wait...
Enter option ('a' add record, 'd' display tally, 'q' quit): Mining block
**Block Verified, broadcasting...**
**Block sent to all peers**
Vote is successfully added.

**Received a block from peer 129.170.65.172**
**New block accepted**
**Received a block from peer 129.170.65.173**
**New block accepted**
d
{'Obama': 2, 'McCain': 1}
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a chain from peer 129.170.65.174**
**New chain rejected**
**Received a chain from peer 129.170.65.174**
**New chain rejected**
**Received a chain from peer 129.170.65.174**
**New chain rejected**
**Received a chain from peer 129.170.65.174**
**New chain rejected**
q
Quitting...
**Peer disconnected from tracker**
**Peer disconencted**
```

#### Peer 3 (Babylon4)

```
f00321f@babylon4:~/project-boxian-james-karim-george$ python3 distributed_voting.py babylon4.thayer.dartmouth.edu 60806
**Peer connectected to tracker**
**Peer now listening to tracker**
**Request sent to peer babylon2.thayer.dartmouth.edu**
**Peer listening for messages**
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a chain from peer 129.170.65.171**
[]
**New chain rejected**
d
{}
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a block from peer 129.170.65.171**
**New block accepted**
d
{'Obama': 1}
Enter option ('a' add record, 'd' display tally, 'q' quit): **Received a block from peer 129.170.65.172**
**New block accepted**
a
Enter voter id: Karim
Enter choice: Obama
Mining started, please wait...
Invalid/duplicate Vote!

Enter option ('a' add record, 'd' display tally, 'q' quit): a
Enter voter id: Gabe
Enter choice: Obama
Mining started, please wait...
Enter option ('a' add record, 'd' display tally, 'q' quit): Mining block
**Block Verified, broadcasting...**
**Block sent to all peers**
Vote is successfully added.

d
{'Obama': 2, 'McCain': 1}
Enter option ('a' add record, 'd' display tally, 'q' quit): q
**Quitting...**
**Peer disconnected from tracker**
**Peer disconencted**
```

#### Malicious Peer (Babylon5)

```
f00321f@babylon5:~/project-boxian-james-karim-george$ python3 malicious_peer.py
Peer connectected to tracker
Peer now listening to tracker
Harassing
```
