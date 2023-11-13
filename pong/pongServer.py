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
import time

server = '192.168.1.26'
port = 12321
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    socket.bind((server, port))
#except socket.error as e:
except:
    #str(e)
    print('fail"')

socket.listen(2) #controls number of connections
print('Waiting for connection...')


cId = "0"
ypos = [] * 2
def Clients(connection):
    global cId, ypos
    connection.send(str.encode(cId)) #tells first connection what its id is
    cId = "1" #sets id to 1 so that second connection will have correct id number
    reply = ''
    while True:
        try:
            data = connection.recv(1024) #1024 is num of bits
            reply = data.decode("utf-8")

            
            if not data:
                print('Disconnected')
                break
            else:
                print('Recieved: ', reply) #will be in form [id, sinc, ypos, clock, score]
                # ar = reply.split(":") #reply is string separated by :, split turns it into array based off of colons
                # id = int(ar[0]) #id of client
                # ypos[id] = reply
                
                # if id == 0: #determine other player
                #     nid = 1
                # if id == 1:
                #     nid = 0

                #reply = ypos[nid][:]


            connection.sendall(str.encode(reply)) #update all pos
        except:
            break
    
    print('Connection closed')
    connection.close()

while True:
    connection, address = socket.accept()
    print("Connected to", address)
    msg = connection.recv(1024).decode()          # Received message from client
    print(f"Client sent: {msg}")
    time.sleep(2)
    connection.send(msg.encode())

    Clients(connection)
    #threading.Thread(Clients, (connection,))


# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games
