import socket
from struct import unpack
import sys
import select
import time

BROADCAST_PORT =13117
MAGIC_COOKIE = 0xabcddcba
OFFER_MSG_TYPE = 0x2
TEAM_NAME = "La Casa De Packet"
MY_NET = '172.1'

def isInNet(ip):
    print("ip", ip, "length of ip:",len(ip))
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
        if isInNet(address):
            connected = True
        else:
            print("address not in net: ", address)
    
    while len(packet)<7: #Not supposed to happen
        packet += socket.recvfrom(1024)[0]

    if(len(packet)) == 7:
        cookie, msg_type, server_port = unpack('=IbH',packet)
        if cookie == MAGIC_COOKIE and msg_type ==OFFER_MSG_TYPE:
            print("Received offer from ip: {}, attempting to connect...".format(address[0])) # printing ip
            connect_to_server(server_port,address[0])

def connect_to_server(server_port, server_address):
    ClientConnectionSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ClientConnectionSocket.connect((server_address, server_port))
        ClientConnectionSocket.send(encodeStr(TEAM_NAME)) # Sedning team name
        game_mode(ClientConnectionSocket, server_address)
    except Exception as e:
        print("Failed to connect. Error:", e)

def game_mode(connection_socket, server_ip):
    print("Connected successfuly to", server_ip)
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
    
    
def handle_msg_from_socket(s):
    print("handle socket")
    try:
        data= s.recv(1024)
    except Exception as e:
        print(sys.stderr, 'closing', s.getpeername(), 'after', e)
        return True
    while len(data)<7:
        if data:
            data += s.recv(1024)
        else:
            return True
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
    chars = []
    for c in input:
        chars.append(c) #todo use this in ans
    return input

def handle_send(o,msg):
    print("sending", msg)
    o.send(encodeStr(msg))

def encodeStr(msg):
    return msg.encode('utf-8')

if __name__=="__main__":
    start_client()