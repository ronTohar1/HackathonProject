import socket
import sys
from struct import pack
import threading
import time
from numpy.core.defchararray import startswith
from numpy.core.fromnumeric import trace
from connectionThread import ConnectionThread
from Player import Player
import numpy as np
import queue

BROADCAST_PORT =13117
BROADCAST_ADDR = ''
SERVER_PORT = 32201
HOST_IP = '127.0.0.1'

NUM_OF_PLAYERS = 2
ANSWER_TIMEOUT = 10
RECEIVE_NAME_TIMEOUT = 5
TIME_AFTER_LAST_JOINED = 10

teamNumberCounter = 1
defaultTeamName = lambda num :  "Team Number {}".format(num)

we_have_a_winner = False

players = [] # Player objects that play in the game.
playerNameThreads = [] # Threads that request the name from the players.
connections_arr = [] # Array of Connection Threads (game members).

server_wakeup_str = lambda host_addr : "Server started, listening on IP address {}".format(host_addr)

class PlayerNameException(Exception):
    def __init__(self, player):
        self.player = player

def printMessage(str):
    print(str)

"""broadcast the invitation message"""
"""Receives a message string and sends it as a broadcast"""
def broadcast_message(message):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    server.sendto( pack('c',message), ('<broadcast>', BROADCAST_PORT))
    server.close()

""" Creating a math question as a string, and returns it and the 
    answer to the question as (question, ans) tuple """
def create_math_question():
    first = np.random.randint(0, 4)
    second = np.random.randint(0, 5)
    question = "How much is {} + {}".format(first, second)
    answer  = first + second
    return question, answer

""" Requesting the name of the player from the client, waiting up to a certain timeout """
def receivePlayereName(player, receiveNameTimeout, names_q, defaultTeamNum):
    player.receiveName(player,receiveNameTimeout, names_q, defaultTeamNum)

""" Creating a thread that requests the name of the player from the client,
    and waiting until a certain timeout, and returns the thread that sets the name """
def setPlayerName(player, defaultName):
    names_q = queue.Queue(NUM_OF_PLAYERS)
    setNameThread = threading.Thread(target=receivePlayereName, args=(player, RECEIVE_NAME_TIMEOUT, names_q, defaultName))
    setNameThread.start()
    playerNameThreads.append(setNameThread)
    return setNameThread

""" Adding a connection thread for a given player thus adding it to the members of the game"""
def addConnectionThread(player):
    conThread = ConnectionThread(player)
    connections_arr.append(conThread)

""" Creating the welcoming TCP socket and listening on the selected port"""
def startServer(host_ip, server_port):
    we_have_a_winner = False
    welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcoming_socket.bind(('', server_port))
    question, answer = create_math_question()
    printMessage(server_wakeup_str(host_addr=host_ip))
    broadcast_message(server_wakeup_str(host_addr=host_ip))
    welcoming_socket.listen(1)
    connectPlayers(welcoming_socket, NUM_OF_PLAYERS) # accepting new players
    startGame(question, answer, players, connections_arr)


""" Connecting the players to the server """
""" Recieves -> welcome socket that is listening to new connection requests,
                math question and answer,
                number of allowed players."""
""" Method requests the name of the player from the client and adds the client to the game members """
def connectPlayers(welcome_socket , num_of_players):
    # Starting to accept connections of clients and adding them to the connected clients array.
    for i in range(num_of_players):
        connectionSocket, addr = welcome_socket.accept()
        connectionSocket.setblocking(True) # making sure the socket is blocking.
        player = Player(connectionSocket)
        players.append(player) # adding the player to the players list

    for player in players:
        defaultName = defaultTeamName(teamNumberCounter)
        player_name_thread = setPlayerName(player, defaultName)
        teamNumberCounter = teamNumberCounter + 1
    

def handleNoNameSent(player):
    "NANA BANANA"

def checkPlayersNames(players):
    for player in players:
        if not player.isNameValid():
            raise PlayerNameException(player)

def createWelcomeString(question, players):
    welcome_str = "Welcome to Quick Maths!\n"
    for i in range(len(players)):
        welcome_str = welcome_str + "Player {}: {}\n".format(i, players[i].getName())
    welcome_str = welcome_str + "== \n Please answer as fast as you can :\n{}".format(question)

def addConnectionThreads(players, welcomeMsg, timeout):
    for player in players:
        addConnectionThread(player, welcomeMsg, timeout)
"""Returns true if finished properly or false otherwise -> meaning not
all participants are connected properly ??????????????????????????????"""
def startGame(math_q, math_a, players, connectionThreads):

    try:
        checkPlayersNames(players)
    except PlayerNameException as e:
        # return False???
        handleNoNameSent(e.player)

    # need to sleep for 10 seconds after all clients joined
    conThreads_thread = threading.Thread(target=addConnectionThreads, args=(players))
    conThreads_thread.start()
    time.sleep(RECEIVE_NAME_TIMEOUT)
    conThreads_thread.join
    

    # We start the game after knowing all players are connected and have names
    # send message to all players : 'All players connected, starting in 10 seconds....'
    welcome_str = createWelcomeString(math_q, players)
    for player in players:
        # The timeout is not really relevant as we will not wait for it. 
        # Therefore, we put the answer timeout that is already the max time out.
        t = threading.Thread(target=player.sendMessage, args=(welcome_str, ANSWER_TIMEOUT))
        t.start()

    # GAME STARTING!!!!!




    
    







