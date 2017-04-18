#!/usr/bin/env python3

import sys
import socket
import select
 
class ChatClient:
    def __init__(self, hostname, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.settimeout(2)
         
        # connect to remote host
        try :
            self.server_socket.connect((hostname, port))
        except :
            print('Unable to connect')
            sys.exit()
         
        print('Connected to remote host. You can start sending messages')
        sys.stdout.write('[Me] ')
        sys.stdout.flush()

    def start(self):
        while True:
            socket_list = [sys.stdin, self.server_socket]
             
            # Get the list sockets which are readable
            ready_to_read, ready_to_write, in_error = \
                   select.select(
                      socket_list,
                      [],
                      [])
             
            for sock in ready_to_read:             
                if sock == self.server_socket:
                    # incoming message from remote server
                    data = sock.recv(4096)

                    if not data:
                        print('\nDisconnected from chat server')
                        sys.exit()
                    else :
                        #print data
                        sys.stdout.write(data.decode())
                        sys.stdout.write('[Me] ')
                        sys.stdout.flush()     
                else:
                    # user entered a message
                    msg = sys.stdin.readline()
                    self.server_socket.send(msg.encode())
                    sys.stdout.write('[Me] ')
                    sys.stdout.flush() 
            
if __name__ == "__main__":
    _, hostname, port = sys.argv
    sys.exit(ChatClient(hostname, int(port)).start())
