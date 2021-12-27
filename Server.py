import socket
import sys
from struct import pack
import threading
from connectionThread import ConnectionThread
from Player import Player
import numpy as np

BROADCAST_PORT =13117
BROADCAST_ADDR = ''
SERVER_PORT = 32201
HOST_IP = '127.0.0.1'
NUM_OF_CONNECTIONS = 2
TIMEOUT = 10
RECEIVE_NAME_TIMEOUT = 10

playerNameThreads = []
connections_arr = [] # Array of Connection Threads.
server_wakeup_str = lambda host_addr : "Server started, listening on IP address {}".format(host_addr)

def printMessage(str):
    print(str)

""" Creating a math question as a string, and returns it and the 
    answer to the question as (question, ans) tuple """
def create_math_question():
    first = np.random.uniform(0,4)
    second = np.random.uniform(0,5)
    question = "How much is {} + {}".format(first, second)
    answer  = first + second
    return (question, answer)

""" Requesting the name of the player from the client, waiting up to a certain timeout """
def receivPlayereName(player, receiveNameTimeout):
    player.receiveName(player,receiveNameTimeout)

""" Creating a thread that requests the name of the player from the client,
    and waiting until a certain timeout """
def setPlayerName(player):
    setNameThread = threading.Thread(target=receivPlayereName, args=(player, RECEIVE_NAME_TIMEOUT))
    setNameThread.run()
    playerNameThreads.append(setNameThread)


""" Creating the welcoming TCP socket and listening on the selected port"""
welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcoming_socket.bind((HOST_IP, SERVER_PORT))
printMessage(server_wakeup_str(host_addr=HOST_IP))
welcoming_socket.listen(1)

math_q, math_a = create_math_question()

# Starting to accept connections of clients and adding them to the connected clients array.
for i in range(NUM_OF_CONNECTIONS):
    connectionSocket, addr = welcoming_socket.accept()
    connectionSocket.settimeout(TIMEOUT) # setting the determined timeout
    player = Player(connectionSocket, math_q, math_a)
    setPlayerName(player) # Setting the name of the player using a different thread.
    conThread = ConnectionThread(player)
    connections_arr.append(conThread)



