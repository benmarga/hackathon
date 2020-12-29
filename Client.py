import socket
import struct
import sys
import threading


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.group_name = "AHMEAD\n"
        self.rcv_data = False

    def start_looking_for_server(self):
        looking_thread = threading.Thread(target=self.look_for_server)
        looking_thread.start()

    def look_for_server(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Client started, listening for offer requests...")
        while True:
            try:
                client_socket.bind(('', self.port))
            except:
                continue
            # Receives Message
            message, address = client_socket.recvfrom(1024)
            try:
                magic_cookie, message_type, port_tcp = struct.unpack('Ibh', message)
            except:
                continue
            if magic_cookie != 0xfeedbeef: continue
            break
        print("Received offer from",address[0],"attempting to connect...")
        self.connecting_to_Server(address[0], port_tcp)

    def connecting_to_Server(self, tcp_ip, tcp_port):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect to tcp server
        while True:
            try:
                tcp_socket.connect((tcp_ip, tcp_port))
                print("sending request")

                break
            except:
                pass

        # Sending team name
        tcp_socket.send(bytes(self.group_name, encoding='utf8'))

        # Receive data from Server
        data = str(tcp_socket.recv(1024), 'utf-8')
        print(data)

        # Setting blocking to false, Data to none and removing key presses representation
        data = None
        tcp_socket.setblocking(False)
        # os.system("stty raw -echo")
        while True:
            # if data is recieved it will stop and print, else it will send every key press to the server.
            try:
                data = tcp_socket.recv(1024)
            except:
                pass
            if data:
                # os.system("stty -raw echo")
                data = str(data, 'utf-8')
                self.rcv_data = True
                print(data)
                break
            else:
                keyboard_input = sys.stdin.read(1)
                tcp_socket.send(bytes(keyboard_input, encoding='utf8'))

        tcp_socket.close()


client = Client("", 13117)
client.start_looking_for_server()
