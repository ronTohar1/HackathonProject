import socket
import sys
from struct import pack
import threading
import time
from connectionThread import ConnectionThread
from Player import Player
import queue
import random

class Server():

    BROADCAST_PORT = 13118

    ANSWER_TIMEOUT = 10
    TIME_AFTER_LAST_JOINED = 7
    RECEIVE_NAME_TIMEOUT = TIME_AFTER_LAST_JOINED
    HOST_IP = '172.1.0.61'
    DEV_BROADCAST = '172.1.255.255'

    MAGIC_COOKIE = 0xabcddcba #bytearray([0xba , 0xdc, 0xcd, 0xab])
    MSG_TYPE = 0x2

    # initiating the server object. expacting a lock object to be received!.
    def __init__(self, lock, port : int , num_of_players=2):
        self.lock = lock

        # Server related variables
        self.port : int = port # Server port
        self.welcome_socket = None # TCP 'welcome' socket
        self.connectingPlayers = True

        # Players related variables 
        self.team_number_counter = 1 # used for default team numbers
        self.players = [] # Player objects that play in the game.
        self.connection_threads = [] # Array of Connection Threads (game members).
        self.player_name_threads = []

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
        self.get_loserCongrats_str = lambda p_loss: "Congratulations to the LOSER : {}".format(p_loss)
        
    def getLoseStr(self, PlayerName):
        return self.get_finish_str(self.answer) + self.get_loserCongrats_str(PlayerName)
    def getWinStr(self, PlayerName):
        return self.get_finish_str(self.answer) + self.get_congrats_str(PlayerName)
    def getDrawStr(self):
        return self.get_finish_str(self.answer) + self.draw_str

    def debug(self, msg):
        print(msg)

    """broadcast the invitation message"""
    """Receives a message string and sends it as a broadcast"""
    def broadcast_message(self):
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_socket.bind((Server.HOST_IP, 0))
        formatted_msg = pack('=IbH',Server.MAGIC_COOKIE, Server.MSG_TYPE, self.port)
        while self.connectingPlayers:
            broadcast_socket.sendto(formatted_msg , (Server.DEV_BROADCAST, Server.BROADCAST_PORT))
            time.sleep(1)
        
        broadcast_socket.close()


    """ Creating a math question as a string, and returns it and the 
        answer to the question as (question, ans) tuple """
    def create_math_question(self):
        first = random.randint(0, 4)
        second = random.randint(0, 5)
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
        target_func = player.receiveName
        target_args = (Server.RECEIVE_NAME_TIMEOUT, defaultName)
        setNameThread = threading.Thread(target=target_func , args=target_args)
        setNameThread.start()
        self.player_name_threads.append(setNameThread)
        return setNameThread

    """ Creating the welcoming TCP socket and listening on the selected port"""
    def startServer(self):

        self.debug("starting fresh")
        # Starting TCP 'welcome' socket for the server

        #broadcasting contantly until all connected
        
        self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.welcome_socket.bind((Server.HOST_IP, self.port))
        self.welcome_socket.listen(1)
        
        wakeup_str = self.server_wakeup_str(host_addr=Server.HOST_IP)
            # Sending broadcast and starting to connect players.
        while True:
            print(wakeup_str) # Printing that started listening
            self.resetServer() # Making sure server is ready for new game.
            self.question, self.answer = self.create_math_question() # Setting math question and ans
            broadcast_thread = threading.Thread(target=self.broadcast_message)
            broadcast_thread.start()
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
            self.debug("Added a player")
        self.connectingPlayers = False

        for player in self.players:
            defaultName = self.getDefaultTeamName()
            t = self.setPlayerName(player, defaultName)


        
        
    """ Creating the string that will be sent to all players when the game begins"""
    def createWelcomeString(self):
        welcome_str = "Welcome to Quick Maths! YOU HAVE 10 SECONDS\n"
        for i in range(len(self.players)):
            welcome_str = welcome_str + "Player {}: {}\n".format(i, self.players[i].getName())
        welcome_str = welcome_str + "== \nPlease answer as fast as you can :\n{}".format(self.question)
        return welcome_str

    """ This method is being called when the game is finished by one of the threads """
    # num = 0 is loss, num = 1 is win, other num is draw
    def finishGame(self, num, player=None):
        if not self.isGameFinished: # If entered after that the game finished than leave.
            
            self.lock.acquire()
            if not self.isGameFinished :
                self.isGameFinished = True
               
                if num == ConnectionThread.LOSS_INDEX:
                    finStr = self.getLoseStr(player.getName())
                    self.SendPlayersAndFinish(self.getLoseStr(player.getName()))
               
                elif num == ConnectionThread.WIN_INDEX:
                    finStr = self.getWinStr(player.getName())
                    self.SendPlayersAndFinish(self.getWinStr(player.getName()))
               
                else:
                    finStr = self.getDrawStr()
                    self.SendPlayersAndFinish(self.getDrawStr())
           
            self.lock.release()

    """ Saving connection threads, where each thread manages the game flow of a player """
    def addConnectionThreads(self, welcomeMsg):
        for player in self.players:
            conThread = ConnectionThread(player, welcomeMsg, self.answer, Server.ANSWER_TIMEOUT, self.finishGame)
            self.connection_threads.append(conThread)

    

    
    """ Sending all players a message and closing the connections """
    def SendPlayersAndFinish(self, msg):
        msg = Server.encodeStr(msg)
        for player in self.players:
            t = threading.Thread(target=player.sendAndFinish, args=(msg,))
            t.start()

    """Returns true if finished properly or false otherwise -> meaning not
    all participants are connected properly ??????????????????????????????"""
    def startGame(self):
        # try:
        #     checkPlayersNames(players)
        # except PlayerNameException as e:
        #     # return False???
        #     handleNoNameSent(e.player)
        

        print("{} players joined, starting in {} seconds".format(self.num_of_players , Server.TIME_AFTER_LAST_JOINED))
        time.sleep(Server.TIME_AFTER_LAST_JOINED) # Waiting 10 seconds after second user joined.
         
        print("Making sure all players sent their names before starting....")
        # Making sure all players name threads are done (Should have been)
        for psThr in self.player_name_threads:
            psThr.join()
        print("All players ready!")
        

        # Creating welcome string and starting all connection threads -> starting game.
        welcome_str : str = self.createWelcomeString()
        encoded_welcome = Server.encodeStr(welcome_str)
        self.addConnectionThreads(encoded_welcome)
        
        
        # GAME STARTING!!!!!
        print("Game starting!")
        for conThr in self.connection_threads:
            # The timeout is not really relevant as we will not wait for it. 
            # Therefore, we put the answer timeout that is already the max time out.
            conThr.start()


        for conThr in self.connection_threads:
            conThr.join()
        
        # Announcing a draw and closing all socket
        if not self.isGameFinished:
            self.finishGame(ConnectionThread.DRAW_INDEX)
        
        print("Game finished!")




        

    """ Reseting the important server fields in order to be able to start a new game session """
    def resetServer(self):
        # Players related variables
        self.team_number_counter = 1
        self.players = [] 
        self.connection_threads = [] 

        self.connectingPlayers = True
        # Game variables
        self.isGameFinished = False
        self.question = ""
        self.answer = 0


    def encodeStr(msg : str):
        encoded = msg.encode()
        return bytearray(encoded)

     
    

    

def main():
    server_port = 2061 # we are student61
    num_of_players = 1
    lock = threading.Lock()
    server = Server(lock, server_port, num_of_players)
    server.startServer()
    
main()







