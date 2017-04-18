#!/usr/bin/env python3

import sys
import socket
import select
import threading
 
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
         
        print("Connected to {}. You can start sending messages".format(hostname))
        self.server_socket.send(self.username.encode())

        self.listen_thread = threading.Thread(target = self.listen)
        self.listen_thread.start()

    def listen(self):
        listening = True

        while listening:
            data = self.server_socket.recv(4096).decode()

            if not data:
                print("Disconnected from chat server")
                listening = False
            else:
                #print data
                sys.stdout.write(data)
                sys.stdout.write('> ')
                sys.stdout.flush()     

        sys.exit()
    
    def start(self):
        while True:
            sys.stdout.write('> ')
            sys.stdout.flush() 
            msg = sys.stdin.readline()
            self.server_socket.send(msg.encode())
            
            if msg.strip() in ["/quit", "/part", "/exit"]:
                self.listen_thread.join()
                return

if __name__ == "__main__":
    hostname, port = input("Hostname: ").split(':')
    username = input("Username: ")
    sys.exit(ChatClient(hostname, int(port), username).start())
