class Player():
    def __init__(self, socket, question, math_real_answer):
        self.question = question
        self.math_real_answer = math_real_answer
        self.socket = socket
        self.name = ""

    def setName(self, name):
        self.name = name

    def setTimeOut(self, timeout):
        self.socket.settimout(timeout)

    def receiveName(player, receiveNameTimeout):
        player.setTimeOut(receiveNameTimeout)
        name = player.socket.recv() # Receiving the name of the player. 
        player.setName(name)
        
