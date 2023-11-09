# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading
import sys
from thread import *

server = ""
port = "5555"
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2) #controls number of connections
print('Waiting for connection, server started.')


def threaded_client(connection):
    reply = ""
    while True:
        try:
            data = connection.recv(2048) #2048 is num of bits
            reply = data.decode("utf-8")
            
            if not data:
                print('Disconnected')
                break
            else:
                print('Recieved: ', reply)
                print('Sending: ', reply)
            connection.sendall(str.encode(reply))
        except:
            break

while True:
    connection, address = socket.accept()
    print("Connected to", address)

    start_new_thread(threaded_client, (connection,))


# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games