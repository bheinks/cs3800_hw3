#!/usr/bin/env python3

import sys
import socket
import select

HOST = '' 
RECV_BUFFER = 4096 
PORT = 9009

class ChatServer:
    def __init__(self, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', port))
        self.server_socket.listen(10)

        self.socket_list = [self.server_socket]
    
    def start(self):
        print("Chat server started on {}".format(PORT))

        while True:
            # get the list sockets which are ready to be read through select
            # 4th arg, time_out  = 0 : poll and never block
            ready_to_read, ready_to_write, in_error = \
                   select.select(
                      self.socket_list,
                      [],
                      [],
                      0)
          
            for sock in ready_to_read:
                # a new connection request recieved
                if sock == self.server_socket: 
                    sockfd, addr = self.server_socket.accept()
                    self.socket_list.append(sockfd)

                    print("Client {} connected".format(addr))
                     
                    self.broadcast(sockfd, "[{}] entered our chatting room\n".format(addr))
                 
                # a message from a client, not a new connection
                else:
                    # process data recieved from client, 
                    try:
                        # receiving data from the socket.
                        data = sock.recv(RECV_BUFFER)
                        if data:
                            # there is something in the socket
                            self.broadcast(sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data.decode())
                        else:
                            # remove the socket that's broken    
                            if sock in self.socket_list:
                                self.socket_list.remove(sock)

                            # at this stage, no data means probably the connection has been broken
                            self.broadcast(sock, "Client ({}) is offline\n".format(addr))

                    # exception 
                    except:
                        print("!!! exception !!!")
                        self.broadcast(sock, "Client ({}) is offline\n".format(addr))
                        continue

        self.server_socket.close()

    def broadcast(self, sock, message):
        for socket in self.socket_list:
            # send the message only to peer
            if socket != self.server_socket and socket != sock:
                try :
                    socket.send(message.encode())
                except :
                    # broken socket connection
                    socket.close()
                    # broken socket, remove it
                    if socket in self.socket_list:
                        self.socket_list.remove(socket)

if __name__ == "__main__":
    sys.exit(ChatServer(9009).start())
