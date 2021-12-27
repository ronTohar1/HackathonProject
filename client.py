import socket
from struct import unpack

BROADCAST_PORT =13117
MAGIC_COOKIE = 0xabcddcba
OFFER_MSG_TYPE = 0x2
msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)
serverAddressPort   = ("127.0.0.1", 20001)
bufferSize          = 1024


def start_client():
    # Create a UDP socket at client side
    ClientBroadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ClientBroadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    ClientBroadcastSocket.bind(("", BROADCAST_PORT))
    self.recive_broadcast(ClientBroadcastSocket)

def recive_broadcast(socket):
    packet, address= socket.recvfrom(1024)
    cookie = packet[:4]
    msg_type = packet[4:5]
    if cookie == MAGIC_COOKIE and msg_type ==:
        server_port = unpack('h', packet[5:7])
        connect_to_server(server_port)
    recive_broadcast(socket)

def connect_to_server(server_port):
    ClientConnectionSocket =socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ClientConnectionSocket.connect((HOST, server_port))
    except ConnectionRefusedError:
        ClientConnectionSocket.close()
        recive_broadcast()
    game_mode(connection_socket)

def game_mode(connection_socket):
    reciver = threading.Thread(target=print_msg, args=(ClientConnectionSocket))
    sender = threading.Thread(target=send_keys, args=(ClientConnectionSocket))
    reciver.start()
    sender.start()
    reciver.join()

def recive_q(connection_socket):
    data = connection_socket.recv(1024)
    print(data)
    data = connection_socket.recv(1024)
    p

# Send to server using created UDP socket
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
msgFromServer = UDPClientSocket.recvfrom(bufferSize)

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)