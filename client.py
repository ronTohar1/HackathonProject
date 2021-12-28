import socket
from struct import unpack
import sys
import select
import time

BROADCAST_PORT =13117
MAGIC_COOKIE = 0xabcddcba
OFFER_MSG_TYPE = 0x2
msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)


def start_client():
    # Create a UDP socket at client side
    while True:
        ClientBroadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ClientBroadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        ClientBroadcastSocket.bind(("", BROADCAST_PORT))
        recive_broadcast(ClientBroadcastSocket)

def recive_broadcast(socket):
    packet, address= socket.recvfrom(1024)
    while len(packet)<7:
        packet += socket.recvfrom(1024)[0]
    socket.close()
    print(packet)
    cookie = unpack('I',packet[:4])[0]
    msg_type = unpack('b',packet[4:5])[0]
    print(packet[:4])
    print(packet[4:5])
    print(packet[5:7])
    print(unpack('H', packet[5:7])[0])
    if cookie == MAGIC_COOKIE and msg_type ==OFFER_MSG_TYPE:
        server_port = unpack('H', packet[5:7])[0]
        print("got cookie")
        connect_to_server(server_port,address[0])

def connect_to_server(server_port, server_address):
    ClientConnectionSocket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(server_address)
        print(server_port)
        ClientConnectionSocket.connect((server_address, server_port))
        game_mode(ClientConnectionSocket)
    except Exception as e:
        print("failed to connect", e)
        ClientConnectionSocket.close()

def game_mode(connection_socket):
    print("hi")
    msg_queue = []
    should_finish = False
    while not should_finish:
        readable,writable,e = select.select([sys.stdin,connection_socket],[],[],11)
        for s in readable:
            if s == sys.stdin:
                msg_queue.append(handle_keyboard(s))
                writable.append(connection_socket)
                print(msg_queue)
            if s == connection_socket:
                if handle_msg_from_socket(s):
                    should_finish = True 
        for o in writable:
            handle_send(o,msg_queue.pop(0))
            if(len(msg_queue)==0):
                writable.remove(o)
        for s in e:
            print('handling exceptional condition for', s.getpeername())
            # Stop listening for input on the connection
            readable.remove(s)
            if s in writable:
                writable.remove(s)
            s.close()
            should_finish = True
        print("1 sec")
        time.sleep(1)
        print("dealy")
    
    
def handle_msg_from_socket(s):
    print("handle socket")
    try:
        data= s.recv(1024)
    except Exception as e:
        print(sys.stderr, 'closing', s.getpeername(), 'after', e)
        return True
    print(s)
    while len(data)<7:
        print(data)
        data += s.recv(1024)
    if data:
        # A readable client socket has data
        data = "".join(map(chr, data))
        print(sys.stderr, 'received "%s" from %s' % (data, s.getpeername()))
        return False #should not finish
    else:
            # Interpret empty result as closed connection
            print(sys.stderr, 'closing', s.getpeername(), 'after reading no data')
            # Should finish
            return True
                
def handle_keyboard(s):
    # gets a msg from server using created TCP socket
    input = s.readline()
    print(input)
    chars = []
    for c in input:
        chars.append(c) #todo use this in ans
    return input

def handle_send(o,msg):
    print("sending", msg)
    o.send(bytearray(msg.encode()))

if __name__=="__main__":
    start_client()