import json
import socket
import time
from datetime import datetime

"""
CLIENT-PACKETS:

LOGIN : Requests a Login
LOGOUT : Requests a Logout
KEEPALIVE : If the Client doesnt send a Keep-alive packet for 30 seconds, the Server disconnects and logs out the Client.

SERVER-RESPONSES:

SUCCESSFULLOGIN : When Client logs in successful.
ALREADYLOGGEDIN : The Client sent a Login request but the Client is already logged in.
DISCONECT : Disconnets the Client from the Server.
FAILEDDISCONNECT : Failed to either logout or to disconnect.

"""
users = [

]

server_running = True
# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific IP address and port
server_address = ('localhost', 55555)
sock.bind(server_address)


def sendToClient(response, address):
    sock.sendto(response.encode(), address)


def tryJoinPlayer(address):
    """
    @:param: returns 0 if fails
    """
    global users
    currenttime = time.time()
    for user in users:
        if user[0] == address:
            sendToClient("ALREADYLOGGEDIN", address)
            return 0
    users.append([address, currenttime])
    sendToClient("SUCCESSFULLOGIN", address)
    return 1


def tryDisconnectPlayer(address):
    """
    @:param: returns 0 if fails
    """
    global users
    t = 0
    for user in users:
        if user[0] == address:
            users[t] = "--TOREMOVE--"
            users.remove("--TOREMOVE--")
            sendToClient("DISCONNECT", address)
            return 1
        t += 1
    return 0


def keepAliveCheck():
    global users

    t = 0
    for user in users:
        if not user[1] >= time.time() - 30:
            tryDisconnectPlayer(users[t][0])
            print("DISCONECTED", users[t][0])
        t += 1


while True:
    # Receive data from the client
    print("Starting listening...")
    data, address = sock.recvfrom(1024)

    print("test")

    if data == "LOGIN":
        tryJoinPlayer(address)

    if data == "LOGOUT":
        tryDisconnectPlayer(address)