#!/usr/bin/env python3

import sys
import socket
import select
import threading

HOST = '' 
RECV_BUFFER = 4096 

class ChatServer:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.users = {}

        try:
            self.server_socket.bind((hostname, port))
        except socket.error:
            print("Bind failed: {}".socket.error)
            sys.exit()

        self.server_socket.listen(10)

    def listen(self):
        # listen for up to 10 simultaneous clients
        print("Chat server started on {}".format(self.port))

        while True:
            client_socket, address = self.server_socket.accept()
            username = client_socket.recv(RECV_BUFFER).decode()
            self.users[username] = client_socket

            threading.Thread(
                    target = self.listen_to_client,
                    args = (username, client_socket)
                ).start()

    def listen_to_client(self, username, client_socket):
        print("Client connected with username " + username)

        while True:
            try:
                data = client_socket.recv(RECV_BUFFER)

                if data:
                    self.broadcast(username, data)
                else:
                    raise error('Client disconnected')
            except:
                client_socket.close()
                return False

    def broadcast(self, username, message):
        for user, socket in self.users.items():
            # send the message only to peer
            if user != username:
                try:
                    socket.send(message)
                except Exception as e:
                    # broken socket connection
                    socket.close()
                    print("broken socket")
                    print(e)
                    # broken socket, remove it
                    #if socket in self.socket_list:
                    #    self.socket_list.remove(socket)

if __name__ == "__main__":
    sys.exit(ChatServer('', 9009).listen())
