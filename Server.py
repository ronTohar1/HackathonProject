import socket
import sys
from struct import pack
import scapy

BROADCAST_PORT =13117
BROADCAST_ADDR = ''
SERVER_PORT = 32201
HOST = 'localhost'
NUM_OF_CONNECTIONS = 2
TIMEOUT = 10
connections_arr = []

server_wakeup_str = lambda host_addr : "Server started, listening on IP address {}".format(host_addr)

def printMessage(str):
    print(str)

""" Creating the welcoming TCP socket and listening on the selected port"""
welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcoming_socket.bind((HOST, SERVER_PORT))
printMessage(server_wakeup_str(host_addr=Host))
welcoming_socket.listen(1)

# Starting to accept connections of clients and adding them to the connected clients array.
for i in range(NUM_OF_CONNECTIONS):
    connectionSocket, addr = welcoming_socket.accept()
    connections_arr.append((connectionSocket, addr))

client_message = connectionSocket.recv(1024)
message_to_client=
connectionSocket.send(message_to_client)
connectionSocket.close()
