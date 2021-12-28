import threading
import Server
class ConnectionThread(threading.Thread):
    LOSS_INDEX = 0
    WIN_INDEX = 1
    DRAW_INDEX = -1
    
    def __init__(self, player, welcome_msg, answer, timeout):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.welcome_msg = welcome_msg
        self.answer = answer
        self.player = player
        self.won_func = Server.finishGame

    def getCharOrLoseEvent(self):
        NotImplemented



    def run(self):
        try:
            self.player.setTimeOut(self.timeout)
            self.player.sendMessage(self.welcome_msg)
            answer = self.player.receiveChar()
            if answer is None: # Something that shouldn't be possible
                self.won_func(ConnectionThread.LOSS_INDEX)
            if answer == self.answer:
                self.won_func(ConnectionThread.WIN_INDEX)
            else:
                self.won_func(ConnectionThread.LOSS_INDEX)
        except:
            #print("Too bad for this player: {}, something went wrong".format(self.player.getName))
            return
        

        

        