import threading

from Player import Player
class ConnectionThread(threading.Thread):
    LOSS_INDEX = 0
    WIN_INDEX = 1
    DRAW_INDEX = -1
    
    def __init__(self, player, welcome_msg, answer, timeout, won_func):
        threading.Thread.__init__(self)
        self.timeout = timeout
        self.welcome_msg = welcome_msg #encoded string
        self.answer = answer
        self.player = player
        self.won_func = won_func

    def isCorrectAnswer(self, c):
        return c == str(self.answer)



    def run(self):
        try:
            self.player.sendMessage(self.welcome_msg, 1)
            player_ans = self.player.receiveChar(self.timeout)
            print("{} answered: ".format(self.player.getName()) ,player_ans)
            if player_ans is None: # Something that shouldn't be possible
                print("{} lost - answered a non-acceptable answer (they sent empty message)".format(self.player.getName()))
                self.won_func(ConnectionThread.LOSS_INDEX, self.player)

            if player_ans is not Player.GAME_TIMEOUT:
                isCorrect = self.isCorrectAnswer(player_ans)
                if isCorrect:
                    self.won_func(ConnectionThread.WIN_INDEX, self.player)
                else:
                    self.won_func(ConnectionThread.LOSS_INDEX, self.player)
                    
        except Exception as e:
            # If some error occurd, the player lost
            self.won_func(ConnectionThread.LOSS_INDEX, self.player)
        try: # anyway dont want to keep any socket on.
            self.player.closeSocket()
        except:
            return
        

        

        