import threading
class ConnectionThread(threading.Thread):
    def __init__(self, player, welcome_msg, answer, timeout, won_func):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.welcome_msg = welcome_msg
        self.answer = answer
        self.player = player
        self.won_func = won_func

    def getCharOrLoseEvent(self):
        NotImplemented



    def run(self):
        self.player.sendMessage(self.welcome_msg)
        answer = self.player.receiveChar()
        if answer is None: # Something that shouldn't be possible
            self.won_func(False)
        if answer == self.answer:
            self.won_func(True)
        else:
            self.won_func(False)
            
        

        

        