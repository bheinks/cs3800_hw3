#!/usr/bin/env python3

import socket

from sys import exit
from threading import Thread
from time import sleep

RECV_BUFFER = 4096 

class ChatServer:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.users = {}
        self.client_threads = []

        try:
            self.server_socket.bind((hostname, port))
        except socket.error as e:
            print("Unable to bind: {}".format(e))
            exit()

        self.server_socket.listen(10)

    def listen(self):
        # listen for up to 10 simultaneous clients
        print("Chat server started on {}:{}".format(self.hostname, self.port))

        while True:
            try:
                client_socket, address = self.server_socket.accept()
            except KeyboardInterrupt:
                self.shutdown()
                return 0

            username = client_socket.recv(RECV_BUFFER).decode()

            # duplicate username
            if username in self.users:
                print("User {} already exists".format(username))
                self.send_message(client_socket, "<Username taken, please select another>")
                client_socket.close()
                continue

            self.users[username] = client_socket
             
            try:
                self.client_threads.append(Thread(
                    target = self.listen_to_client,
                    args = (username, client_socket)))

                self.client_threads[-1].start()
            except:
                print("Error creating thread")
                return 1

    def listen_to_client(self, username, client_socket):
        print("Client connected with username " + username)
        self.send_message(
                client_socket,
                "<Welcome, {}! There are {} other user(s) currectly connected>" \
                .format(username, len(self.users) - 1))

        self.broadcast(username, "<{} has connected>".format(username))

        while True:
            try:
                data = client_socket.recv(RECV_BUFFER).decode()

                if data:
                    if data.strip() in ["/exit", "/quit", "/part"]:
                        print("{} command from {}".format(data.strip(), username))

                        self.broadcast(username, "<{} has disonnected>".format(username))
                        self.disconnect(username)

                        return

                    self.broadcast(username, "[{}] {}".format(username, data.strip()))
                else:
                    self.disconnect(username)
                    return
            except:
                self.disconnect(username)
                return

    def send_message(self, sock, message):
        sock.send("{}\n".format(message).encode())

    def broadcast(self, sender, message):
        for username, sock in self.users.items():
            # send the message to everyone except sender
            if username != sender:
                try:
                    self.send_message(sock, message)
                except Exception as e:
                    print("Broken socket connection to {}: {}".format(username, e))
                    self.disconnect(username)

    def disconnect(self, username):
        self.users[username].close()
        del self.users[username]

    def shutdown(self):
        print("Shutting down server in 10 seconds")
        self.broadcast(None, "<Warning: Server shutting down in 10 seconds>")
        sleep(10)

        for username in self.users.keys():
            self.users[username].shutdown(socket.SHUT_RDWR)

        for thread in self.client_threads:
            thread.join()
        
        self.server_socket.close()

if __name__ == "__main__":
    exit(ChatServer('', 9009).listen())
