import threading
class ConnectionThread(threading.Thread):
    def __init__(self, socket, question, math_real_answer):
        threading.Thread.__init__(self)
        self.question = question
        self.math_real_answer = math_real_answer
        self.socket = socket

    # Receives the name of the client, and returns it.
    def receiveName():
        NotImplemented

    def startGame():
        NotImplemented

    def run(self):
        self.startGame()
        

        
message_to_client=
connectionSocket.send(message_to_client)
connectionSocket.close()
client_message = connectionSocket.recv(1024)