import threading
class ConnectionThread(threading.Thread):
    LOSS_INDEX = 0
    WIN_INDEX = 1
    DRAW_INDEX = -1
    
    def __init__(self, player, welcome_msg, answer, timeout):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.welcome_msg = welcome_msg #encoded string
        self.answer = answer
        self.player = player
        self.won_func = None

    def getCharOrLoseEvent(self):
        NotImplemented



    def run(self):
        try:
            self.player.sendMessage(self.welcome_msg, 1)
            answer = self.player.receiveChar(self.timeout)
            print("CT Answer : " ,answer)
            if answer is None: # Something that shouldn't be possible
                self.won_func(ConnectionThread.LOSS_INDEX)
            if answer == self.answer:
                self.won_func(ConnectionThread.WIN_INDEX)
            else:
                self.won_func(ConnectionThread.LOSS_INDEX)
        except Exception as e:
            print("CT run error: ", e)
        

        

        