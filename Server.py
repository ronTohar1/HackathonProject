import socket
import sys
from struct import pack
import threading
import time
from Player import Player
import queue
import random

class Server():

    BROADCAST_PORT = 13333

    ANSWER_TIMEOUT = 10
    TIME_AFTER_LAST_JOINED = 7
    RECEIVE_NAME_TIMEOUT = TIME_AFTER_LAST_JOINED
    HOST_IP = '172.1.0.61'
    DEV_BROADCAST_IP = '172.1.255.255'

    MAGIC_COOKIE = 0xabcddcba #bytearray([0xba , 0xdc, 0xcd, 0xab])
    MSG_TYPE = 0x2

    LOSS_INDEX = 0
    WIN_INDEX = 1
    DRAW_INDEX = -1

    questions = [("How many characters are in the word - happiness?",9), ("How many continents there are?",7), ("what is the best digit?",7),("3 + 5 - 7 + 1 - 2 =",0),("what digit rymes with heaven?",7)]

    
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
        self.server_wakeup_str = lambda host_addr : "Server started, listening on IP address {} and Port {}".format(host_addr, self.port)
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
            broadcast_socket.sendto(formatted_msg , (Server.DEV_BROADCAST_IP, Server.BROADCAST_PORT))
            time.sleep(1)
        
        broadcast_socket.close()


    """ Creating a math question as a string, and returns it and the 
        answer to the question as (question, ans) tuple """
    def create_math_question(self):
        
        index = random.randint(0, len(Server.questions) - 1)
        question = Server.questions[index][0]
        answer  = Server.questions[index][1]
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
        self.debug("Starting a fresh server. FUN!")
        # Starting TCP 'welcome' socket for the server

        #broadcasting contantly until all connected
        connected = False
        while not connected:
            try:
                self.welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.welcome_socket.bind((Server.HOST_IP, self.port))
                self.welcome_socket.listen(1)
                connected = True
            except:
                print("The ip we are trying to connect is not available: {}, {}".format(Server.HOST_IP,self.port))
                time.sleep(1)

        try:
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
        except:
            self.welcome_socket.close()




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
            print("Added player: (ip, port) {}".format(addr))
            defaultName = self.getDefaultTeamName()
            self.setPlayerName(player, defaultName)
        self.connectingPlayers = False


        
        
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
            self.lock.acquire()
            try:
                if not self.isGameFinished:
                    self.isGameFinished = True
                
                    if num == Server.LOSS_INDEX:
                        finStr = self.getLoseStr(player.getName())
                        print("Lossers :",player.getName() )
                        self.SendPlayersAndFinish(self.getLoseStr(player.getName()))
                
                    elif num == Server.WIN_INDEX:
                        finStr = self.getWinStr(player.getName())
                        print("Winners: ",player.getName() )
                        self.SendPlayersAndFinish(self.getWinStr(player.getName()))
                
                    else:
                        print('Draw!!!!')
                        finStr = self.getDrawStr()
                        self.SendPlayersAndFinish(self.getDrawStr())
            
                self.lock.release()
            except: # Making sure that the lock is released
                self.lock.release() 

    """ Saving connection threads, where each thread manages the game flow of a player """
    def addConnectionThreads(self, welcomeMsg):
        for player in self.players:
            args = (player, welcomeMsg, self.answer, Server.ANSWER_TIMEOUT)
            conThread = threading.Thread(target=self.playFunc, args=args)
            self.connection_threads.append(conThread)

    
    """ Sending all players a message and closing the connections """
    def SendPlayersAndFinish(self, msg):
        msg = Server.encodeStr(msg)
        for player in self.players:
            t = threading.Thread(target=player.sendAndFinish, args=(msg,))
            t.start()

    def isCorrectAnswer(self, c):
        return c == str(self.answer)

    def playFunc(self, player, welcome_msg, answer, timeout):
        try:
            player.sendMessage(welcome_msg, 1)# send welcome msg

            # receiving if not passed 10 seconds
            current_time = time.time()
            while (not self.isGameFinished) and time.time() < current_time + timeout:
                player_ans = player.receiveChar(self.isGameFinished)
                if not (player_ans == None):
                    isCorrect = self.isCorrectAnswer(player_ans)
                    if isCorrect:
                        self.finishGame(Server.WIN_INDEX, player)
                    else:
                        self.finishGame(Server.LOSS_INDEX, player)
                time.sleep(0.2)
        except:
            player.closeSocket()

    """Returns true if finished properly or false otherwise -> meaning not
    all participants are connected properly ??????????????????????????????"""
    def startGame(self):

        print("{} players joined, starting in {} second\n".format(self.num_of_players , Server.TIME_AFTER_LAST_JOINED))
        time.sleep(Server.TIME_AFTER_LAST_JOINED) # Waiting 10 seconds after second user joined.
         
        print("Making sure all players sent their names before starting.... (waiting up to {} seconds after the last joined)".format(Server.TIME_AFTER_LAST_JOINED))
        # Making sure all players name threads are done (Should have been)
        for psThr in self.player_name_threads:
            psThr.join()
        
        # for player in players:
        #     if not player.isConnected():
        #         print("a player has crashed!")
        #         return

        print("All players ready!\n")
        

        # Creating welcome string and starting all connection threads -> starting game.
        welcome_str : str = self.createWelcomeString()
        encoded_welcome = Server.encodeStr(welcome_str)
        self.addConnectionThreads(encoded_welcome)
        
        
        # GAME STARTING!!!!!
        print("Game starting! sending questions...\n")
        for conThr in self.connection_threads:
            # The timeout is not really relevant as we will not wait for it. 
            # Therefore, we put the answer timeout that is already the max time out.
            conThr.start()


        for conThr in self.connection_threads:
            conThr.join()
        
        # Announcing a draw and closing all socket
        if not self.isGameFinished:
            self.finishGame(Server.DRAW_INDEX)
        
        print("Game finished!------------------------------\n\n")




        

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
        encoded = msg.encode('utf-8')
        return encoded


def main():
    server_port = 2061 # we are student61
    num_of_players = 2
    lock = threading.Condition(threading.Lock())
    server = Server(lock, server_port, num_of_players)
    server.startServer()
    
main()







