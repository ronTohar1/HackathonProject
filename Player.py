

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

    """ Sending a message to the client throught the player's socket .
        msg should be encoded"""
    def sendMessage(self, msg, timeout):
        try:
            self.setTimeOut(timeout)
            self.socket.send(msg)
        except Exception as e:
            print("Error sending message: {}".format(e)) 

    def sendAndFinish(self, msg):
        try:
            msg = bytearray([1,1,1,2])
            self.sendMessage(msg)
            self.socket.close()
        except:
            print("Error closing socket")

    """ Receiving a char from the client (or none if nothing was recevied) """
    def receiveChar(self, timeout):
        self.setTimeOut(timeout)
        try:
            data = self.socket.recv()
            if not data:
                return None
            else:
                return chr(data[0])
        except socket.timeout as e:
            print("Timeout exception", e)
        except Exception as e:
            print("Exception", e)

    """ Requesting the name from the client and setting it as this player name """
    def receiveName(self, receiveNameTimeout ,defaultTeamName):
        self.setTimeOut(receiveNameTimeout)
        name_buffer =[]
        continue_recv = True
        while continue_recv:
            # IMPLEMENT EXCEPTION HANDLING
            try:
                recv_buffer = self.socket.recv(1024) # Receiving the name of the player.
            except socket.timeout as e:
                self.setName(defaultTeamName)
                break
            except Exception as e:
                print("Exception: ",e)
            for c in iter_unpack('c',recv_buffer):
                next_char = c[0]
                if next_char == bytearray(("\n").encode()):
                    continue_recv = False
                else:
                    name_buffer += next_char
        print("Received name:!!!!!")
        name = ""
        name = str(name.join(map(chr, name_buffer))) # decoding the name 
        self.setName(name) # setting the name of the current player.
        print(":Finished recieveing1")
