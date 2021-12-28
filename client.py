import socket
from struct import unpack
import sys
import select

BROADCAST_PORT =13117
MAGIC_COOKIE = 0xabcddcba
OFFER_MSG_TYPE = 0x2
msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)


def start_client():
    # Create a UDP socket at client side
    ClientBroadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ClientBroadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ClientBroadcastSocket.bind(("", BROADCAST_PORT))
    recive_broadcast(ClientBroadcastSocket)

def recive_broadcast(socket):
    packet, address= socket.recvfrom(1024)
    cookie = packet[:4]
    msg_type = packet[4:5]
    if cookie == MAGIC_COOKIE and msg_type ==OFFER_MSG_TYPE:
        server_port = unpack('h', packet[5:7])
        connect_to_server(server_port,address)
    recive_broadcast(socket)

def connect_to_server(server_port, server_address):
    ClientConnectionSocket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ClientConnectionSocket.connect((server_address, server_port))
    except ConnectionRefusedError:
        ClientConnectionSocket.close()
        recive_broadcast()
    game_mode(ClientConnectionSocket)

def game_mode(connection_socket):
    msg_queue = []
    should_finish = False
    while not should_finish:
        readable,writable,e = select.select([sys.stdin,connection_socket],[],[],0.0001)
        for s in readable:
            if s == sys.stdin:
                msg_queue.extend(handle_keyboard(s))
                writable.append(connection_socket)
            if s == connection_socket:
                if handle_msg_from_socket(s):
                    should_finish = True 
        for o in writable:
            handle_send(o,msg_queue.pop())
            if(len(msg_queue)==0):
                writable.remove(o)
        for s in e:
            print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
            # Stop listening for input on the connection
            readable.remove(s)
            if s in writable:
                writable.remove(s)
            s.close()
            should_finish = True
    
def handle_msg_from_socket(s):
    data = s.recv(1024)
    if data:
        # A readable client socket has data
        print >>sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
        return False #should not finish
    else:
            # Interpret empty result as closed connection
            print >>sys.stderr, 'closing', s.getpeername(), 'after reading no data'
            # Should finish
            return True
                
def handle_keyboard(s):
    # gets a msg from server using created TCP socket
    input = s.readline()
    chars = []
    for c in input:
        chars.append(c)
    return chars

def handle_send(o,msg):
    o.send(msg)