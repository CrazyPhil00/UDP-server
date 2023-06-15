"""
CLIENT-PACKETS:

LOGIN : Requests a Login
LOGOUT : Requests a Logout
KEEPALIVE : If the Client doesn't send a Keep-alive packet for 30 seconds, the Server disconnects and logs out the Client.

SERVER-RESPONSES:

SUCCESSFULLOGIN : When Client logs in successful.
ALREADYLOGGEDIN : The Client sent a Login request but the Client is already logged in.
DISCONECT : Disconnets the Client from the Server.
FAILEDDISCONNECT : Failed to either logout or to disconnect.
SUCCESSFULLKEEPALIVE : Successfull keepalive request.


user = [
    ["192.168.1.168", TIME, [x, y]],
    ["192.168.1.164", TIME, [x, y]]
]

"""
import socket
import threading
import time

users = []
running = True

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to a specific IP address and port
server_address = ('localhost', 55555)
sock.bind(server_address)


def sendToClient(response, address):
    sock.sendto(response.encode(), address)


def tryJoinPlayer(address):
    global users
    currenttime = time.time()
    for user in users:
        if user[0] == address:
            sendToClient("ALREADYLOGGEDIN", address)
            return 0
    users.append([address, currenttime])
    sendToClient("SUCCESSFULLOGIN", address)
    return 1


def tryDisconnectPlayer(address, user_request=True):
    global users
    t = 0
    for user in users:
        if user[0] == address:
            del users[t]
            if user_request:
                sendToClient("DISCONNECT", address)
            return 1
        t += 1
    if user_request:
        sendToClient("FAILEDDISCONNECT", address)
    return 0


def keepAlive(address, user_request):
    global users
    t = 0
    for user in users:
        if user[0] == address:
            users[t][1] = time.time()
            if user_request:
                sendToClient("SUCCESSFULLKEEPALIVE", address)
            return 0
        t += 1


def keepAliveCheck():
    global users
    print(users)
    while running:
        print("Checking for timeout...")
        t = 0
        for user in users:
            if not user[1] >= time.time() - 30:
                print("DISCONECTED", users[t][0])
                tryDisconnectPlayer(users[t][0], False)
                return 0

            t += 1
        time.sleep(30)
    return 1


def addToList(address, toAdd):
    # Find the index of the desired address
    index = None
    for i, user in enumerate(users):
        if user[0] == address:
            index = i
            break

    # Replace the position if the address exists
    if index is not None:
        if len(users[index]) < 3:
            users[index].append(toAdd)
        else:
            users[index][2] = toAdd


keepAliveCheckthread = threading.Thread(target=keepAliveCheck)

keepAliveCheckthread.start()

while True:
    # Receive data from the client
    print("Starting listening...")
    data, address = sock.recvfrom(1024)

    # print(f"Received data from {address}:", data.decode())

    if data.decode() == "LOGIN":
        tryJoinPlayer(address)
        print("Trying to login")

    if data.decode() == "LOGOUT":
        tryDisconnectPlayer(address)
        print("Trying to logout")

    if data.decode() == "KEEPALIVE":
        keepAlive(address, True)
        print("Trying to keep alive")

    if "POS" in data.decode():
        position = data.decode().split(",")
        del position[0]
        addToList(address, position)

        print("Updated position for", address)
        keepAlive(address, False)

        sendToClient(f"{users}", address)

    print(users)
