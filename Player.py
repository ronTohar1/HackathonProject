import socket
from struct import iter_unpack

class Player():
    GAME_TIMEOUT = -1
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

    """ Receives and send an encoded msg to the player """
    def sendAndFinish(self, msg):
        try:
            self.socket.send(msg)
            self.closeSocket()
        except Exception as e:
            print("Error closing socket: ", e, self.closeSocket())

    def closeSocket(self):
        if self.socket:
            self.socket.close()


    """ Receiving a char from the client (or none if nothing was recevied) """
    def receiveChar(self, timeout):
        self.setTimeOut(timeout)
        try:
            data = self.socket.recv(1024)
            if not data:
                return None
            else:
                return chr(data[0])
        except socket.timeout as e:
            return Player.GAME_TIMEOUT
        except Exception as e:
            return Player.GAME_TIMEOUT


    """ Requesting the name from the client and setting it as this player name """
    def receiveName(self, receiveNameTimeout ,defaultTeamName):
        self.setTimeOut(receiveNameTimeout)
        name_buffer =[]
        continue_recv = True
        name_set = False
        while continue_recv:
            try:
                recv_buffer = self.socket.recv(1024) # Receiving the name of the player.
                # for c in iter_unpack('c',recv_buffer):
                #     next_char = c[0]
                #     if next_char == bytearray(("\n").encode()):
                #         continue_recv = False
                #     else:
                #         name_buffer += next_char

                name = decode(recv_buffer)
                #name = str(name.join(map(chr, name_buffer))) # decoding the name 
                #print("Received player name:", name)
                self.setName(name) # setting the name of the current player.
                name_set = True
            except socket.timeout as e:
                if not name_set:
                    self.setName(defaultTeamName)
                break
            except Exception as e:
                print("Exception Receiving name of player: " ,e)

def decode(msg):
    return msg.decode('utf-8')

            