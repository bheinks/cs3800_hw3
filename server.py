#!/usr/bin/env python3

###################################################
# 
#  Brett Heinkel (bhbn8), Michael Proemsey (mkpv3b)
#  CS3800, Section 1B, Assignement 3
#  Group Chat Server - server.py
#
#  Usage: ./server.py
#
###################################################

import socket
import threading

from sys import exit
from time import sleep

RECV_BUFFER = 4096 

class ChatServer:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

        # initialize server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # keep track of connected users and threads
        self.users = {}
        self.client_threads = []

        try:
            # attempt to bind server to address:port
            self.server_socket.bind((hostname, port))

            # accept connections from a maximum of 10 clients
            self.server_socket.listen(10)
        except OSError as e:
            print("Unable to bind: {}".format(e))
            exit(1)

    # accept new connection and spin up threads for each new client
    def listen(self):
        print("Chat server started on {}:{}".format(self.hostname, self.port))

        while True:
            try:
                client_socket, address = self.server_socket.accept()
            except OSError as e:
                print("Error accepting client connection: {}".format(e))
                continue
            # catch ctrl+c and initiate shutdown
            except KeyboardInterrupt:
                self.shutdown()
                return 0

            # first message from client is username
            username = client_socket.recv(RECV_BUFFER).decode().strip()

            # if a client connects with a username that is already in use
            if username in self.users:
                print("User {} already exists".format(username))
                self.send_message(client_socket, "<Username taken, please select another>")
                client_socket.close()
                continue

            # otherwise, add them to the users table
            self.users[username] = client_socket
             
            try:
                self.client_threads.append(threading.Thread(
                    target = self.listen_to_client,
                    args = (username, client_socket)))

                self.client_threads[-1].start()
            except (RuntimeError, threading.ThreadError) as e:
                print("Error creating thread: {}".format(e))
                return 1

    # manage connection to client and receive incoming messages
    def listen_to_client(self, username, client_socket):
        print("Client connected with username " + username)
        self.send_message(
                client_socket,
                "<Welcome, {}! There are {} other user(s) currectly connected>" \
                .format(username, len(self.users) - 1))

        self.broadcast("<{} has connected>".format(username), username)

        while True:
            try:
                data = client_socket.recv(RECV_BUFFER).decode()

                if data:
                    # if message from user is an exit command, close socket to client
                    if data.strip() in ["/exit", "/quit", "/part"]:
                        print("{} command from {}".format(data.strip(), username))

                        self.send_message(client_socket, "<Goodbye!>")
                        self.disconnect(username)
                        self.broadcast("<{} has disonnected>".format(username))

                        return

                    message = "[{}] {}".format(username, data.strip())
                    print(message)

                    # send message to all users but sender
                    self.broadcast(message, username)
                # socket has probably been closed
                else:
                    self.disconnect(username)
                    return
            except:
                self.disconnect(username)
                return

    def send_message(self, sock, message):
        sock.send("{}\n".format(message).encode())

    # broadcast message to all clients (except sender)
    def broadcast(self, message, sender = ""):
        for username, sock in self.users.items():
            # send the message to everyone except sender
            if username != sender:
                try:
                    self.send_message(sock, message)
                except Exception as e:
                    print("Broken socket connection to {}: {}".format(username, e))
                    self.disconnect(username)

    # disconnect user and remove from user table
    def disconnect(self, username):
        self.users[username].close()
        del self.users[username]

    # shut down the server
    def shutdown(self):
        print("Shutting down server in 10 seconds")
        self.broadcast("<Warning: Server shutting down in 10 seconds>")
        sleep(10)

        # disallow sending and receiving for all client sockets
        for username in self.users.keys():
            self.users[username].shutdown(socket.SHUT_RDWR)

        # close all client threads
        for thread in self.client_threads:
            thread.join()
        
        self.server_socket.close()

if __name__ == "__main__":
    # start server on localhost:9009
    exit(ChatServer('', 9009).listen())
