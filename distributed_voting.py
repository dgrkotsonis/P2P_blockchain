# distributed_voting.py
# Final Project - Gabe Kotsonis, Boxian Wang, George McNulty, Karimi Itani
# June 3, 2021
#
# This program implements our distributed voting application, which, by utilizing our
# blockchain, allows peers to vote and view tallies from the vote.


import json, time, random
from sys import argv
from threading import Thread
from peer import Peer

# check that a new vote has not already been made
def check_duplicate(new_vote, all_votes):
    all_votes_list = [json.loads(i) for i in all_votes]
    if new_vote is not None:
        all_votes_list.append(json.loads(new_vote))
    voters = [i['voter'] for i in all_votes_list]
    return len(voters) == len(set(voters))

# create syntax for a specific vote
def make_vote(voter, choice):
    return json.dumps({'voter': voter, 'choice': choice})

# return a dict of 'choice: votes'; assume no duplicates
def tally_votes(votes):
    all_votes_list = [json.loads(i) for i in votes]
    res = {}
    for vote in all_votes_list:
        if vote['choice'] in res:
            res[vote['choice']]  += 1
        else:
            res[vote['choice']] = 1
    return res

# voting machine class, provides distributed voting functionality
class VotingMachine:
    def __init__(self, self_addr=('babylon1.thayer.dartmouth.edu', 60806), 
        tracker_addr=('babylon1.thayer.dartmouth.edu', 60825)):
        self.node = Peer(self_addr=self_addr, tracker_addr=tracker_addr, data_crit=check_duplicate)
        self.is_mining = False

    def start(self):
        self.node.connect()

        # prompt user for input, whether they want to vote, view the tally, or quit. Handle accordingly
        while True:
            op = str(input("Enter option ('a' add record, 'd' display tally, 'q' quit): "))
            if op == 'a':
                if self.is_mining:
                    print("Please wait for current mining to finish...")
                else:
                    voter = str(input("Enter voter id: "))
                    choice = str(input("Enter choice: "))
                    Thread(target=self.mining, args = (make_vote(voter, choice), )).start()
                    print("Mining started, please wait...")
            elif op == 'd':
                print(tally_votes(self.node.get_data()))
            elif op == 'q':
                print("Quitting...")
                self.node.disconnect()
                break
            else:
                print("Invalid option!")

    # mine to add to the blockchain  
    def mining(self, data):
        self.is_mining = True
        while True:
            res = self.node.add_data(data)
            if res == 1: 
                print("Vote is successfully added.\n")
                break
            elif res == 0:
                print("While mining, blockchain is changed. Retrying...\n")
                time.sleep(random.randint(0, 100) / 100.0 * 2.0)
            elif res == -1:
                print("Invalid/duplicate Vote!\n")
                break
        self.is_mining = False

if __name__ == "__main__":
    VotingMachine(self_addr=(argv[1], int(argv[2]))).start()

