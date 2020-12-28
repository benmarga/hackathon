import os
import socket
import sys
import threading
import random
import colorama
import colors as color


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.team = "yosi-oren\n"
        self.recv_data = False

    def looking_for_server(self):
        # Creates a thread to start looking for server.
        thread = threading.Thread(target=self.looking)
        thread.start()

    def looking(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        color.print("Client started, listening for offer requests...")
        # connect client on server port
        try:
            sock.bind(('', self.port))
        except:
            self.looking()
        # Message arrives
        message = sock.recvfrom(1024)[0]

        magic_cookie = message[:4]
        message_type = message[4]
        tcp_port = message[5:]
        self.connect(int.from_bytes(
            tcp_port, byteorder='big', signed=False))

    def connect(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.ip, port))
        except:
            self.looking()
        sock.send(bytes(self.team, encoding='utf8'))
        data = str(sock.recv(1024), 'utf-8')
        color.print(data)
        thread = threading.Thread(target=self.recv_Data, args=(sock,))
        thread.start()
        while not self.recv_data:
            os.system("stty raw -echo")
            c = sys.stdin.read(1)
            sock.send(bytes(c, encoding='utf8'))
            os.system("stty -raw echo")
        sock.close()

    def recv_Data(self, sock):
        while not self.recv_data:
            data = str(sock.recv(8), 'utf-8')
            if data:
                self.recv_data = True
                os.system("stty -raw echo")
                color.print(data)
