import socket
from struct import unpack
import sys
import select
import time

from Player import decode

BROADCAST_PORT =13333
MAGIC_COOKIE = 0xabcddcba
OFFER_MSG_TYPE = 0x2
TEAM_NAME = "La Casa De Packet\n"
MY_NET = '172.1'

def isInNet(ip):
    l = len(MY_NET)
    if len(ip) < l:
        return False
    return ip[:l] == MY_NET


def start_client():
    # Create a UDP socket at client side
    ClientBroadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ClientBroadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ClientBroadcastSocket.bind(('', BROADCAST_PORT))
    while True:
        recive_broadcast(ClientBroadcastSocket)

def recive_broadcast(socket):
    print("Waiting for broadcasts")
    connected = False
    # Trying to connect a host in the net
    while not connected:
        packet, address= socket.recvfrom(1024)
        if isInNet(address[0]):
            connected = True
        
    
    while len(packet)<7: #Not supposed to happen
        packet += socket.recvfrom(1024)[0]

    if(len(packet)) == 7:
        cookie, msg_type, server_port = unpack('=IbH',packet)
        if cookie == MAGIC_COOKIE and msg_type ==OFFER_MSG_TYPE:
            print("Received offer from ip: {}, attempting to connect...".format(address[0])) # printing ip
            connect_to_server(server_port,address[0])
        print(address[0], server_port)

def connect_to_server(server_port, server_address):
    ClientConnectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcc = 0
    try:
        ttc = time.time()
        ClientConnectionSocket.connect((server_address, server_port))
        ClientConnectionSocket.send(encodeStr(TEAM_NAME)) # Sedning team name
        print(tcc - time.time())
        game_mode(ClientConnectionSocket, server_address)
    except Exception as e:
        print("Failed to connect. Error:", e)

def game_mode(connection_socket, server_ip):
    print("Connected successfuly to", server_ip)

    msg_queue = []
    should_finish = False

    while not should_finish:
        timeout = 11
        readable, writable, errors = select.select([sys.stdin, connection_socket], [], [], timeout)
        for s in readable:
            
            # If received input from user, adding it to the msg_queue and adding the socket
            # because we can have to send the message through the socket
            if s == sys.stdin:
                msg_queue.append(handle_keyboard(s))
                writable.append(connection_socket)

            # If received input from socket, print it and end select if socket is closed
            if s == connection_socket:
                if handle_msg_from_socket(s):
                    should_finish = True 
    
        # Popping the first appended message and sending it throught the socket o.
        for o in writable:
            handle_send(o, msg_queue.pop(0))
            if(len(msg_queue)==0):
                writable.remove(o)

        # If found error -> closing s and should finish.
        for s in errors:
            print('handling exceptional condition for', s.getpeername())
            # Stop listening for input on the connection
            readable.remove(s)
            if s in writable:
                writable.remove(s)
            s.close()
            should_finish = True
    
""" Receiving a message from server. Returning true if should finish or false else"""
def handle_msg_from_socket(sock):
    print("Receiving message from socket:")
    try:
        data = sock.recv(1024)
    except Exception as e:
        print('closing', sock.getpeername(), 'after gett exception:', e)
        return True
    
    if not data:
        return True # Should finish
    
    # A readable client socket has data
    data = decodeStr(data)
    print(sys.stderr, 'received "%s" from %s' % (data, sock.getpeername()))
    
    return False # Should not finish
                
def handle_keyboard(s):
    # gets a msg from server using created TCP socket
    input = s.readline()
    chars = []
    for c in input:
        chars.append(c) #todo use this in ans
    return input

def handle_send(o,msg):
    print("sending:", msg)
    o.send(encodeStr(msg))

def encodeStr(msg):
    return msg.encode('utf-8')

def decodeStr(msg):
    return msg.decode('utf-8')

if __name__=="__main__":
    start_client()