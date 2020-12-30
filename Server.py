import time
import socket
import threading
import struct
from select import select


class Server:
    def __init__(self, port):
        # init server settings
        self.ip = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.clients = {}
        self.game_threads = {}
        self.teamA = {}
        self.teamB = {}
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def brodcasting(self, udp_socket):
        # broadcasting to clients udp messages
        msg = struct.pack('Ibh', 0xfeedbeef, 0x2, self.port)
        time_0 = time.time()
        while time.time() - time_0 <= 10:
            udp_socket.sendto(msg, ('<broadcast>', 13117))
            time.sleep(1)

    def tcp_connect(self, t, sock):
        # connecting to client
        while t.is_alive():
            try:
                client_socket, address = sock.accept()
                # adr
                self.clients[client_socket.recv(2048).decode()] = {"sock": client_socket}
            except socket.timeout:
                continue

    def searching_clients(self):
        # looking for clients
        self.udp_socket.bind((self.ip, self.port))
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcp_socket.bind((self.ip, self.port))
        self.tcp_socket.listen()
        self.tcp_socket.settimeout(1)
        # init threads for parallel running
        broadcasting = threading.Thread(target=self.brodcasting, args=(self.udp_socket,))
        connecting = threading.Thread(target=self.tcp_connect, args=(broadcasting, self.tcp_socket))
        broadcasting.start()
        connecting.start()
        broadcasting.join()
        connecting.join()
        self.udp_socket.close()
        self.tcp_socket.close()

    def game_play(self):
        if len(self.clients) == 0:
            print("There is no players - restarting server.")
            for client in self.clients:
                self.clients[client]['sock'].close()
            return

        which = True
        for team in self.clients.keys():
            if which:
                which = False
                self.teamA[team] = 0
            else:
                which = True
                self.teamB[team] = 0
            start_game = threading.Thread(target=self.one_client_game_thread, args=(self.clients[team], team))
            self.game_threads[team] = start_game
            # start game for each group as a thread.
            start_game.start()

        for thread in self.game_threads:
            self.game_threads[thread].join()
        if len(self.teamA.keys()) == 0:
            score_1 = 0
        else:
            score_1 = sum(self.teamA.values())
        if len(self.teamB.keys()) == 0:
            score_2 = 0
        else:
            score_2 = sum(self.teamB.values())
        # end game msg
        msg = "\nGame over!\n"
        msg += f"Group 1 typed in {str(score_1)} characters. Group 2 typed in {str(score_2)} characters.\n"
        if score_1 > score_2:
            msg += "Group 1 wins!\n\nCongratulations to the winners:\n==\n"
            for name in self.teamA:
                msg += name
        elif score_1 < score_2:
            msg += "Group 2 wins!\n\nCongratulations to the winners:\n==\n"
            for name in self.teamB:
                msg += name
        else:
            msg += "DRAW\n "
        for team in self.clients:
            self.clients[team]['sock'].send(msg.encode())
            self.clients[team]['sock'].close()
        print("Game over, sending out offer requests...")

    def one_client_game_thread(self, links, team_name):
        msg = """Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"""
        for name in self.teamA:
            msg += name
        msg += """Group 2:\n==\n"""
        for name in self.teamB:
            msg += name
        msg += "\nStart pressing keys on your keyboard as fast as you can!!"

        # sending the msg to coressponding client.
        links['sock'].send(msg.encode())
        num_of_chars = 0
        time_0 = time.time()
        # for 10 seconds, recive pressed keys from client.
        while time.time() - time_0 <= 10:
            incoming_character, nothing1, nothing2 = select([links['sock']], [], [], 0)
            if incoming_character:
                non = links['sock'].recv(2048).decode()
                num_of_chars += 1

        # add the accumulated key presses to the team counters dictionary.
        if team_name in self.teamA:
            self.teamA[team_name] += num_of_chars
        else:
            self.teamB[team_name] += num_of_chars


print(f'Server started, listening on IP address {socket.gethostbyname(socket.gethostname())}')
while True:
    server = Server(2039)
    try:
        server.searching_clients()
    except:
        for t in server.clients:
            server.clients[t]['sock'].close()
        server.tcp_socket.close()
        server.udp_socket.close()
        continue
    try:
        server.game_play()
    except:
        for t in server.clients:
            server.clients[t]['sock'].close()
        continue
