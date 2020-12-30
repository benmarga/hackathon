import sys
import os
import struct
import socket
from threading import Thread
from select import select


class Client:
    def __init__(self, udp_port, tcp_port):
        # init client settings
        self.ip = socket.gethostbyname(socket.gethostname())
        self.udp_port = udp_port
        self.tcp_port = tcp_port
        self.game_mode = False
        self.name = "The-SockeTeam\n"
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def get_char_input(self):
        # for not blocking
        os.system("stty raw -echo")
        while self.game_mode:
            data, d1, d2 = select([sys.stdin], [], [], 0)
            if data:
                character = sys.stdin.read(1)
                try:
                    self.tcp_socket.send(character.encode())
                except:
                    pass
        # reset
        os.system("stty -raw echo")


sys.stdout.write("\033[1;36m")
print("Client started, listening for offer requests...")
while True:
    client = Client(13117, 2039)
    client.udp_socket.bind(('', client.udp_port))
    while True:
        try:
            # receive message from server and unpack it
            b, addr = client.udp_socket.recvfrom(1024)
            packet = struct.unpack('Ibh', b)
            magic_cookie = packet[0]
            message_type = packet[1]
            server_port = packet[2]
            # check validation of message
            if magic_cookie != 0xfeedbeef or message_type != 0x2:
                continue
            # connecting to server
            sys.stdout.write("\033[1;34m")
            print(f'Received offer from {addr[0]}, attempting to connect...')
            client.tcp_socket.connect((addr[0], server_port))
            # send client team name
            try:
                client.tcp_socket.send(client.name.encode())
            except:
                client.tcp_socket.close()
                continue
            break
        except:
            continue
    client.udp_socket.close()
    try:
        getch_thread = Thread(target=client.get_char_input)
        # START MSG
        sys.stdout.write("\033[0;32m")
        print(client.tcp_socket.recv(2048).decode())
        client.game_mode = True
        getch_thread.start()
        msg = client.tcp_socket.recv(2048).decode()
        client.game_mode = False
        getch_thread.join()
        # END
        sys.stdout.write("\033[1;31m")
        print(msg)
        sys.stdout.write("\033[1;36m")
        print("Server disconnected, listening for offer requests...")
        client.tcp_socket.close()
    except:
        client.tcp_socket.close()
        pass
    # close all ports
    client.tcp_socket.close()
