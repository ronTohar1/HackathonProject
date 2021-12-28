

import socket
from struct import iter_unpack

class Player():
    def __init__(self, socket):
        self.socket = socket
        self.name = ""

    def getName(self):
        return self.name

    def setName(self,name):
        self.name = name

    def setDefaultName(self, teamNum):
        self.setName("Team {}".format(teamNum))

    """ Setting the timeout for the socket of the playerm"""
    def setTimeOut(self, timeout):
        self.socket.settimeout(timeout)
    
    def isNameValid(self):
        return self.name != ""

    """ Sending a message to the client throught the player's socket """
    def sendMessage(self, msg, timeout):
        try:
            self.setTimeOut(timeout)
            self.socket.send(msg)
        except:
            print("Error sending message") 

    def sendAndFinish(self, msg):
        try:
            self.sendMessage(msg)
            self.socket.close()
        except:
            print("Error closing socket")

    """ Receiving a char from the client (or none if nothing was recevied) """
    def receiveChar(self, msg, timeout):
        self.setTimeOut(timeout)
        data = self.socket.recv()
        if not data:
            return None
        else:
            return data[0]

    """ Requesting the name from the client and setting it as this player name """
    def receiveName(player, receiveNameTimeout ,defaultTeamName):
        player.setTimeOut(receiveNameTimeout)
        name_buffer =[]
        while continue_recv:
            # IMPLEMENT EXCEPTION HANDLING
            try:
                recv_buffer = player.socket.recv() # Receiving the name of the player.
            except socket.timeout:
                player.setName(defaultTeamName)
                break
            for c in iter_unpack('c',recv_buffer):
                next_char = c[0]
                if next_char == '\n':
                    continue_recv = False
                else:
                    name_buffer += next_char
        player.setName(str.join(name_buffer)) # setting the name of the current player.
