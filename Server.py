import random
import socket
import struct
import threading
import time
from _thread import start_new_thread


class Server:
    def __init__(self, ip, tcp_port, udp_port):
        self.ip = ip
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.broadcast_mode = True
        self.num_of_players = 0
        self.groups = []
        self.score = [0, 0]
        self.lock = threading.Lock()
        self.game_mode = False

    def start_broadcast(self):
        broadcast_thread = threading.Thread(target=self.broadcast)
        broadcast_thread.start()

    def broadcast(self):
        print("Server started, listening on IP address", self.ip)
        while True:
            # if not self.gamemode
            time_0 = time.time()
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            server_socket.settimeout(0.2)
            while time.time() - time_0 < 10:
                server_socket.sendto(struct.pack('Ibh', 0xfeedbeef, 2, 2039), ('<broadcast>', self.udp_port))
                time.sleep(1)
            self.game_mode = True
            self.broadcast_mode = False

    def start_server(self):
        thread = threading.Thread(target=self.start_tcp_server)
        thread.start()

    def start_tcp_server(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.tcp_port))
        self.start_broadcast()
        server_socket.listen()
        while True:
            print("b")
            connection, address = server_socket.accept()
            print("here")

            self.lock.acquire()
            self.num_of_players += 1
            if self.num_of_players == 1:
                random.shuffle(self.groups)
            self.lock.release()

            # Start a new thread and return its identifier
            start_new_thread(self.make_game, (connection,))
        server_socket.close()

    def make_game(self, connection):
        print("work tcp connection")
        group_name = str(connection.recv(1024), 'utf-8')
        self.groups.append(group_name)
        while not self.game_mode: time.sleep(1)
        group_1 = ''
        group_2 = ''
        for idx, group in enumerate(self.groups):
            if idx % 2 == 0:
                group_1 += group
            else:
                group_2 += group
        connection.send(bytes(
            f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n{group_1}Group 2:\n{group_2}\nStart pressing keys on your keyboard as fast as you can!!",
            encoding='utf8'))
        idx = self.groups.index(group_name)
        if idx % 2 == 0:
            client_team = 0
        else:
            client_team = 1
        # While not past 10 seconds - listen to key presses.
        time_0 = time.time()
        while time.time() - time_0 < 10:
            # data received from client
            data = connection.recv(1024)
            if not data:
                continue
            self.score[client_team] += 1
        if self.score[0] > self.score[1]:
            win = 0
            win_group = self.groups[0]
        else:
            win = 1
            win_group = self.groups[1]

        # Game Over Message
        message = f"\nGame over!\nGroup 1 typed in {self.score[0]} characters. Group 2 typed in {self.score[1]} characters.\nGroup {win + 1} wins!\n\nGlobal Results:\nCongratulations to the winners:\n{win_group}"
        connection.send(bytes(message, encoding='utf8'))
        self.game_mode = False
        # connection closed
        connection.close()


server = Server("", 2039, 13117)
server.start_server()
