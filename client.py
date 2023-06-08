# Before sending each question, wait 1-5 secs. This will help test multipole clients.
import socket
import sys
import select
import time
import random

class Client:
        def __init__(self):
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                port = 12345
                if(len(sys.argv) > 1 and sys.argv[1].isnumeric()):
                    port = int(sys.argv[1])
                self.server_address = ('localhost', port)
                self.connections = [self.client]
                self.guessL = 1
                self.guessR = 100
                self.greater = True
                self.equal = False
                self.prev = "Yes"
        
        def run(self):
                # Connect the socket to the port where the server is listening
                print(f'Connecting to {self.server_address[0]} port {self.server_address[1]}')
                self.client.connect(self.server_address)
                while True:
                    # Get the list sockets which are readable
                    readable_connections, _, _ = select.select(self.connections, [], [], 1)
                    #print(readable_connections)
                    # print(self.client)
                    if(not len(readable_connections)):
                            readable_connections.append(sys.stdin)
                    for c in readable_connections:
                            #print("For")
                            #incoming message from remote server
                            if c == self.client:
                                data = c.recv(4096).decode()
                                print(data)
                                if str(data) == "End" or str(data) == "You win":
                                        return
                                elif str(data) == "Yes" and self.greater:
                                        self.guessR = int((self.guessL + self.guessR)/2) - 1
                                elif str(data) == "Yes" and not self.greater:
                                        self.guessL = int((self.guessL + self.guessR)/2) + 1
                                elif str(data) == "No" and self.greater and self.prev == "Yes":
                                        self.greater = False
                                elif str(data) == "No" and not self.greater and self.prev == "Yes":
                                        self.greater = True
                                else:
                                        self.equal = True
                                self.prev = str(data)
                            elif c == sys.stdin:
                                if self.equal:
                                        msg = "= "
                                elif self.greater:
                                        msg = "> "
                                else:
                                        msg = "< "
                                msg += str(int((self.guessL + self.guessR)/2));
                                print(msg)
                                time.sleep(random.randint(1,5))
                                self.client.send(str(msg).encode())

if __name__ == '__main__':
        user = Client()
        user.run()