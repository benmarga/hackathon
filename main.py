import socket
from Server import Server
from Client import Client

my_server = Server('localhost', 1337, 13117)
my_server.start()
my_client = Client('localhost', 13117)
my_client.looking_for_server()
