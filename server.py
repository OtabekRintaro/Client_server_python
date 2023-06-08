# Before sending each question, wait 1-5 secs. This will help test multipole clients.
import socket
import sys
import select
import queue
import random

class Server:
    def __init__(self, address='localhost', port=12345):
        self.timeout = 0
        if(len(sys.argv) > 1 and sys.argv[1].isnumeric()):
            port = int(sys.argv[1])
        self.server_address = (address, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        self.server.bind(self.server_address)
        self.server.listen()
        self.connections = [self.server]
        self.messages = queue.Queue()
        self.number = random.randint(1, 100)
        self.end = False

    def deal_with_socket_error(self, client, error):
        print(f'ERROR: {error}')
        self.connections.remove(client)

    def add_client(self):
        client, _ = self.server.accept()
        self.connections.append(client)

    def deal_with_messages(self, messages, writeable_connections):
        while True:
            try:
                client, inp = messages.get_nowait()
                if client in writeable_connections:
                    if not self.end:
                        data = inp.split(' ')
                        op = data[0]
                        num = data[1]
                        if op == ">":
                            if(int(num) > int(self.number)):
                                client.sendall("Yes".encode())
                            else:
                                client.sendall("No".encode())
                        elif op == "<":
                            if(int(num) < int(self.number)):
                                client.sendall("Yes".encode())
                            else:
                                client.sendall("No".encode())
                        elif op == "=":
                            if(int(num) == int(self.number)):
                                client.sendall("You win".encode())
                                self.end = True
                                self.connections.remove(client)
                            else:
                                client.sendall("You lose".encode())
                    else:
                        client.sendall("End".encode())
                        self.connections.remove(client)
                if len(self.connections) == 1:
                    self.end = False
                    self.number = random.randint(1,100)
                    print(self.number)
                    

            except queue.Empty:
                break

    def run(self):
        print(self.number)
        while self.connections:
            readable_connections, writeable_connections, _ = select.select(self.connections, self.connections, [], self.timeout)
            # print(readable_connections)
            for c in readable_connections:
                if c is self.server:
                    self.add_client()
                else:
                    try:
                        message = c.recv(4096).decode()
                        self.messages.put((c, message))
                    except socket.error as e:
                        self.deal_with_socket_error(c, e)
            self.deal_with_messages(self.messages, writeable_connections)

if __name__=='__main__':
    server = Server()
    server.run()