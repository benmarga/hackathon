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
        self.name = "GOGO\n"
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def searching_server(self):
        # binds server
        self.udp_socket.bind(('', self.udp_port))
        while True:
            try:
                # receive message from server and unpack it
                b, addr = self.udp_socket.recvfrom(1024)
                packet = struct.unpack('Ibh', b)
                magic_cookie = packet[0]
                message_type = packet[1]
                server_port = packet[2]
                # check validation of message
                if magic_cookie != 0xfeedbeef or message_type != 0x2:
                    continue
                # connecting to server
                print(f'Received offer from {addr[0]}, attempting to connect...')
                self.tcp_socket.connect((addr[0], server_port))
                # send client team name
                try:
                    self.tcp_socket.send(self.name.encode())
                except:
                    self.tcp_socket.close()
                    continue
                break
            except:
                continue
        self.udp_socket.close()

    def get_char_input(self):
        # for not blocking
        os.system("stty raw -echo")
        while self.game_mode:
            data, d1,d2 = select([sys.stdin], [], [], 0)
            if data:
                character = sys.stdin.read(1)
                try:
                    self.tcp_socket.send(character.encode())
                except:
                    pass
        #reset
        os.system("stty -raw echo")

    def play(self):
        try:
            getch_thread = Thread(target=self.get_char_input)
            # START MSG
            print(self.tcp_socket.recv(2048).decode())
            self.game_mode = True
            getch_thread.start()
            msg = self.tcp_socket.recv(2048).decode()
            self.game_mode = False
            getch_thread.join()
            # END
            print(msg)
            print("Server disconnected, listening for offer requests...")
            self.tcp_socket.close()
        except:
            self.tcp_socket.close()
            pass
        # close all ports
        self.tcp_socket.close()


print("Client started, listening for offer requests...")
while True:
    client = Client(13117, 2039)
    client.searching_server()
    client.play()
