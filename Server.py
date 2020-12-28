import socket
import threading
from _thread import start_new_thread
import time
import random
import colors
import colorama
from termcolor import colored, cprint


class Server:
    def __init__(self, ip, port, udp_port):
        self.ip = ip
        self.port = port
        self.broadcast_mode = True
        self.udp_port = udp_port
        self.players = 0
        # self.startTCPServer()
        self.groups = []
        self.statistics = [{}, {}, {}, {}]
        self.team_score = [0, 0]
        self.players_score = [0, 0, 0, 0]
        self.game_mode = False
        self.lock = threading.Lock()

    def start(self):
        # Starts tcp server
        thread = threading.Thread(target=self.tcp_server)
        thread.start()

    def tcp_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.ip, self.port))
        colors.print(f"Server started, listening on IP address {self.ip}")
        self.start_broadcast_mode()
        sock.listen()
        while True:
            # connect with client
            connection, addr = sock.accept()
            self.lock.acquire()
            self.players += 1
            if self.players == 1:
                random.shuffle(self.groups)
            self.lock.release()

            # Start a new thread and return its identifier
            start_new_thread(self.control_game, (connection,))
        sock.close()

    def start_broadcast_mode(self):
        # Starts Broadcasting via a thread.
        thread = threading.Thread(target=self.broadcast)
        thread.start()

    def broadcast(self):
        while True:
            if not self.game_mode:
                time_0 = time.time()
                # port reuse,broadcasting mode,init timeout
                server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                server.settimeout(0.2)

                # TODO: change to struct.pack

                magic_cookie = "feedbeef"
                message_type = "02"
                x = bytes.fromhex(magic_cookie)
                y = bytes.fromhex(message_type)
                z = self.port.to_bytes(2, byteorder='big')
                msg = x + y + z

                while time.time() - time_0 < 10:
                    server.sendto(msg, ('<broadcast>', self.udp_port))
                    time.sleep(1)
                self.game_mode = True

    def control_game(self, connection):
        group_name = str(connection.recv(1024), 'utf-8')
        self.groups += [group_name]
        while not self.game_mode:
            time.sleep(0.5)

        group_1 = ''.join(self.groups[:int(len(self.groups) / 2)])
        group_2 = ''.join(self.groups[int(len(self.groups) / 2):])
        connection.send(
            bytes(f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{group_1}Group 2:\n==\n{group_2}\n"
                  f"Start pressing keys on your keyboard as fast as you can!!", encoding='utf8'))

        idx = self.groups.index(group_name) // 2
        time_0 = time.time()
        while time.time() - time_0 < 10:
            # data received from client
            data = connection.recv(1024)
            if not data:
                continue
            self.team_score[idx] += 1
            num_key = self.statistics[idx].get(data, 0) + 1
            self.statistics[idx][data] = num_key
            self.players_score[idx] += 1

        # send back string to client
        winner = 0 if (self.team_score[0] > self.team_score[1]) else 1

        # BONUS
        winner_team = group_1 if (self.team_score[0] > self.team_score[1]) else group_2
        sorted_keys = sorted(self.statistics[idx].items(), key=lambda x: x[1], reverse=True)
        most_common_key = sorted_keys[0][0].decode('utf-8')
        most_common_key_pressed = sorted_keys[0][1]
        least_common_key = sorted_keys[-1][0].decode('utf-8')
        least_common_key_pressed = sorted_keys[-1][1]
        max_press = max(self.players_score)
        fastest_typer_index = self.players_score.index(max_press)
        name = self.groups[fastest_typer_index].split('\n')[0]

        msg = f"\nGame over!\nGroup 1 typed in {self.team_score[0]} characters. Group 2 typed in {self.team_score[1]} characters.\nGroup {winner + 1} wins!\n\nGlobal Results:\nThe fastest team was {name} with {max_press} characters!\n\nPersonal Results:\nYou pressed {self.players_score[idx]} characters\nYour most common character was '{most_common_key}' with {most_common_key_pressed} presses!\nYour least common character was '{least_common_key}' with {least_common_key_pressed} presses.\n\nCongratulations to the winners:\n==\n{winner_team}"
        connection.send(bytes(msg, encoding='utf8'))
        self.game_mode = False
        # connection closed
        connection.close()
        self.lock.acquire()
        self.players -= 1
        self.lock.release()
        self.players_score = [0, 0, 0, 0]
        self.statistics = [{}, {}, {}, {}]
