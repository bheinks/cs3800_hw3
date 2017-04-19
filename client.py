#!/usr/bin/env python3

import sys
import socket

from threading import Thread
from select import select
 
class ChatClient:
    def __init__(self, hostname, port, username):
        self.username = username
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.settimeout(None)
         
        # connect to remote host
        try:
            self.server_socket.connect((hostname, port))
        except:
            print("Unable to connect")
            sys.exit()
         
        # send username to server
        self.server_socket.send(self.username.encode())

        self.listen_thread = Thread(target = self.listen)
        self.listen_thread.start()

    def listen(self):
        while True:
            data = self.server_socket.recv(4096).decode()

            if not data:
                print("Disconnected from chat server")
                self.reading = False
                break
            else:
                # print data
                sys.stdout.write(data)
                sys.stdout.write('> ')
                sys.stdout.flush()     
    
    def start(self):
        self.reading = True

        sys.stdout.write('> ')
        sys.stdout.flush() 

        while self.reading:
            ready_to_read, ready_to_write, error = select([sys.stdin], [], [], 1)

            if ready_to_read:
                sys.stdout.write('> ')
                sys.stdout.flush() 

                try:
                    msg = sys.stdin.readline()
                except KeyboardInterrupt:
                    print("\nPlease type /exit, /quit or /part to exit the chatroom")
                    continue

                self.server_socket.send(msg.encode())
                
                if msg.strip() in ["/quit", "/part", "/exit"]:
                    self.listen_thread.join()
                    return

if __name__ == "__main__":
    hostname, port = input("Hostname: ").split(':')
    username = input("Username: ")
    sys.exit(ChatClient(hostname, int(port), username).start())
