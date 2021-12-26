import socket
import sys
from struct import pack
import threading
from connectionThread import ConnectionThread
from connection import GameConnection

BROADCAST_PORT =13117
BROADCAST_ADDR = ''
SERVER_PORT = 32201
HOST = 'localhost'
HOST_IP = ''
NUM_OF_CONNECTIONS = 2
TIMEOUT = 10
RECEIVE_NAME_TIMEOUT = 10
connections_arr = [] # Array of Connection objects.
server_wakeup_str = lambda host_addr : "Server started, listening on IP address {}".format(host_addr)

def printMessage(str):
    print(str)

def create_math_question():
    NotImplemented

def receiveName(gameConnection):
    gameConnection.setTimeOut(RECEIVE_NAME_TIMEOUT)
    name = gameConnection.socket.recv() # Receiving the name of the player. 
    gameConnection.setName(name)

def setPlayerName(gameCon):
    setNameThread = threading.Thread(target=receiveName(gameCon))
    setNameThread.run()


""" Creating the welcoming TCP socket and listening on the selected port"""
welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcoming_socket.bind((HOST, SERVER_PORT))
printMessage(server_wakeup_str(host_addr=HOST_IP))
welcoming_socket.listen(1)

math_q, math_a = create_math_question()

# Starting to accept connections of clients and adding them to the connected clients array.
for i in range(NUM_OF_CONNECTIONS):
    connectionSocket, addr = welcoming_socket.accept()
    connectionSocket.settimeout(TIMEOUT) # setting the determined timeout
    GC = GameConnection(connectionSocket, math_q, math_a)
    setPlayerName(GC) # Setting the name of the player
    connections_arr.append(GC)



