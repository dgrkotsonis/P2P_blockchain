from peer import Peer
import sys, time

def main(num):
    peer = Peer(self_addr=(f'babylon{num}.thayer.dartmouth.edu', 60810))

    peer.connect()
    while not peer.add_data("Hi"):
        time.sleep(int(4))
    
    while not peer.add_data(f"Peer #babylon{num}"):
        time.sleep(int(4))
    
    while not peer.add_data("I'm"):
        time.sleep(int(4))

    time.sleep(int(10))
    print(peer.get_data())
    time.sleep(int(num))
    peer.disconnect()


if __name__ == "__main__":
    main(sys.argv[1])