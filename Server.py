import socket
import sys
from struct import pack
import threading
import time
from connectionThread import ConnectionThread
from Player import Player
import queue
import numpy as np

class Server():

    BROADCAST_PORT = 13117
    BROADCAST_ADDR = ''
    HOST_IP = '127.0.0.1'

    ANSWER_TIMEOUT = 10
    RECEIVE_NAME_TIMEOUT = 10
    TIME_AFTER_LAST_JOINED = 10

    MAGIC_COOKIE = bytearray([0xab , 0xcd, 0xdc, 0xba])
    MSG_TYPE = bytearray([0x02])

    # initiating the server object. expacting a lock object to be received!.
    def __init__(self, lock, port, num_of_players=2):
        self.lock = lock

        # Server related variables
        self.port = port # Server port
        self.welcome_socket = None # TCP 'welcome' socket

        # Players related variables
        self.team_number_counter = 1 # used for default team numbers
        self.player = [] # Player objects that play in the game.
        self.connection_threads = [] # Array of Connection Threads (game members).

        # Game variables
        self.num_of_players = num_of_players
        self.isGameFinished = False
        self.question = ""
        self.answer = 0
    
        # Informative strings for the server.
        self.server_wakeup_str = lambda host_addr : "Server started, listening on IP address {}".format(host_addr)
        self.get_finish_str = lambda ans : "Game Over!\n the correct answer was {}\n\n".format(ans)
        self.get_congrats_str = lambda p_won: "Congratulations to the WINNER: {}".format(p_won)
        self.draw_str = "Good game everyone! it's a draw"
        self.get_lose_str = lambda p_loss: "Congratulations to the LOSER : {}".format(p_loss)
        
    def getLoseStr(self, PlayerName):
        return self.get_finish_str(self.answer) + self. get_lose_str(PlayerName)
    def getWinStr(self, PlayerName):
        return self.get_finish_str(self.answer) + self.getWinStr(PlayerName)
    def getDrawStr(self):
        return self.get_finish_str(self.answer) + self.draw_str

    """broadcast the invitation message"""
    """Receives a message string and sends it as a broadcast"""
    def broadcast_message(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        formatted_msg = pack('ssh',Server.MAGIC_COOKIE, Server.MSG_TYPE, self.port)
        broadcast_socket.sendto( formatted_msg , ('<broadcast>', Server.BROADCAST_PORT))
        broadcast_socket.close()

    """ Creating a math question as a string, and returns it and the 
        answer to the question as (question, ans) tuple """
    def create_math_question(self):
        first = np.random.randint(0, 4)
        second = np.random.randint(0, 5)
        question = "How much is {} + {}".format(first, second)
        answer  = first + second
        return question, answer

    def getDefaultTeamName(self):
        teamName = "Team Number {}".format(self.team_number_counter)
        self.team_number_counter += 1
        return teamName
   
    """ Creating a thread that requests the name of the player from the client,
        and waiting until a certain timeout, and returns the thread that sets the name """
    def setPlayerName(self, player : Player, defaultName):
        target_func = Player.receiveName
        target_args = (player, Server.RECEIVE_NAME_TIMEOUT, defaultName)
        setNameThread = threading.Thread(target=target_func , args=target_args)
        setNameThread.start()
        return setNameThread

    """ Creating the welcoming TCP socket and listening on the selected port"""
    def startServer(self, host_ip, server_port):
        while True:
            self.resetServer() # Making sure server is ready for new game.

            # Starting TCP 'welcome' socket for the server
            self.welcoming_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.welcoming_socket.bind(('', server_port))
            self.welcoming_socket.listen(1)
            
            print(self.server_wakeup_str(host_addr=host_ip)) # Printing that started listening
            self.question, self.answer = self.create_math_question() # Setting math question and ans

            # Sending broadcast and starting to connect players.
            self.broadcast_message(self.server_wakeup_str(host_addr=host_ip)) 
            self.connectPlayers() # accepting new players
            self.startGame() # After all players joined -> starting the game.


    """ Connecting the players to the server """
    """ Recieves -> welcome socket that is listening to new connection requests,
                    math question and answer,
                    number of allowed players."""
    """ Method requests the name of the player from the client and adds the client to the game members """
    def connectPlayers(self):
        # Starting to accept connections of clients and adding them to the connected clients array.
        for i in range(self.num_of_players):
            connectionSocket, addr = self.welcome_socket.accept()
            connectionSocket.setblocking(True) # making sure the socket is blocking.
            player = Player(connectionSocket)
            self.players.append(player) # adding the player to the players list

        for player in self.players:
            defaultName = self.getDefaultTeamName()
            self.setPlayerName(player, defaultName)
        
    """ Creating the string that will be sent to all players when the game begins"""
    def createWelcomeString(self):
        welcome_str = "Welcome to Quick Maths!\n"
        for i in range(len(self.players)):
            welcome_str = welcome_str + "Player {}: {}\n".format(i, self.players[i].getName())
        welcome_str = welcome_str + "== \n Please answer as fast as you can :\n{}".format(self.question)

    """ Saving connection threads, where each thread manages the game flow of a player """
    def addConnectionThreads(self, welcomeMsg):
        for player in self.players:
            conThread = ConnectionThread(player, welcomeMsg, self.answer, Server.ANSWER_TIMEOUT)
            self.connection_threads.append(conThread)

    """ This method is being called when the game is finished by one of the threads """
    # num = 0 is loss, num = 1 is win, other num is draw
    def finishGame(self, num, player : Player=None):
        self.lock.acquire()
        if not self.isGameFinished :
            self.isGameFinished = True
            if num == ConnectionThread.LOSS_INDEX:
                self.SendPlayersAndFinish(self.getLoseStr(player.getName()))
            elif num == ConnectionThread.WIN_INDEX:
                self.SendPlayersAndFinish(self.getWinStr(player.getName()))
            else:
                self.SendPlayersAndFinish(self.getDrawStr(player.getName))
        self.lock.release()

    """ This method makes sure that the game is no longer than the determined max time """
    def gameTimeout(self):
        time.sleep(Server.ANSWER_TIMEOUT) # waiting 10 seconds until the game ends
        self.finishGame(ConnectionThread.DRAW_INDEX) # trying to create draw situation

    """ Sending all players a message and closing the connections """
    def SendPlayersAndFinish(self, msg):
        for player in self.players:
            t = threading.Thread(target=player.sendAndFinish, args=(msg))
            t.start()

    """Returns true if finished properly or false otherwise -> meaning not
    all participants are connected properly ??????????????????????????????"""
    def startGame(self):
        # try:
        #     checkPlayersNames(players)
        # except PlayerNameException as e:
        #     # return False???
        #     handleNoNameSent(e.player)

        welcome_str = self.createWelcomeString()
        # need to sleep for 10 seconds after all clients joined
        conThreadsCreation_thread = threading.Thread(target=self.addConnectionThreads, args=(welcome_str))
        conThreadsCreation_thread.start()
        time.sleep(Server.TIME_AFTER_LAST_JOINED) # Waiting 10 seconds after second user joined.
        conThreadsCreation_thread.join() # Making sure all connection threads are created.
        

        # We start the game after knowing all players are connected and have names
        # send message to all players : 'All players connected, starting in 10 seconds....'
        game_timeout_thread = threading.Thread(target=self.gameTimeout)
        for player in self.players:
            # The timeout is not really relevant as we will not wait for it. 
            # Therefore, we put the answer timeout that is already the max time out.
            t = threading.Thread(target=player.sendMessage, args=(welcome_str, Server.ANSWER_TIMEOUT))
            t.start()

        # GAME STARTING!!!!!
        game_timeout_thread.start()

    """ Reseting the important server fields in order to be able to start a new game session """
    def resetServer(self):
        # Players related variables
        self.team_number_counter = 1
        self.players = [] 
        self.connection_threads = [] 

        # Game variables
        self.isGameFinished = False
        self.question = ""
        self.answer = 0

        # Server variables
        self.welcome_socket = None

    

    

def main():
    server_port = 31310
    num_of_players = 2
    lock = threading.Lock()
    server = Server(lock, server_port, num_of_players)
    server.startServer()
    
main()







