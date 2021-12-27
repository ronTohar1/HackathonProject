import threading
class ConnectionThread(threading.Thread):
    def __init__(self, player):
        threading.Thread.__init__(self)
        self.player = player

    # Receives the name of the client, and returns it, and update self.name .
    def receiveName(self):
        NotImplemented

    

    def startGame(self):
        NotImplemented

    def run(self):
        self.receiveName()
        self.startGame()
        