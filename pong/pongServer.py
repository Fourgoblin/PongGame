# =================================================================================================
# Contributing Authors:	    <Anyone who touched the code>
# Email Addresses:          <Your uky.edu email addresses>
# Date:                     <The date the file was last edited>
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

# 11/13 comment, goals for tomorrow: 
# game start syncronization (use a player count variable to ensure both are connectd?)
# sending data (position, clock, score, id) from server to client and vice versa

import socket
import threading
import sys
import time
import select

server = '192.168.1.26'
port = 12321
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #changed from socket to sock to avoid possible keyword
playerCount = 0 #number of players

try:
    sock.bind((server, port))
except:
    print('Failed to bind socket')

sock.listen(2)  # Controls the number of connections
print('Waiting for connections...')

clientList = []  # List to keep track of connected clients


#ypos = [] * 2
def clientHandler(connection, cId):
    global clientList
    connection.send(str.encode(str(cId)))  #tells first connection what its id is
    while playerCount < 2:
        connection.sendall(str.encode("wait"))
        time.sleep(1)
        #try:
            #data = connection.recv(1024).decode("utf-8") 
            #if data == "Waiting":
                #pass
        

    reply = ''
    while True:
        try:
            data = connection.recv(1024) #1024 is num of bits
            reply = data.decode("utf-8") #reply is string separated by :, split turns it into array based off of colons

            if not data:
                print('Disconnected')
                break
            else:
                print(f'Received from Client {cId}: {reply}') #will be in form [id, sinc, ypos, clock, score]
            
            connection.sendall(str.encode(reply))
        except:
            break
    
    print(f'Connection with client {cId} closed')
    connection.close()
    clientList[cId] = None  # Set the client slot to None

cId = 0
while True:
    connection, address = sock.accept()
    print(f"Connected to {address}")
    clientList.append(connection)  # Add the new connection to the list
    clientThread = threading.Thread(target=clientHandler, args=(connection, cId))
    clientThread.start()

    cId += 1
    if cId == 1:
        playerCount = 2 #since 2 IDs have been given, there must be 2 players conected

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games
