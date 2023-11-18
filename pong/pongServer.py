# =================================================================================================
# Contributing Authors:	    Mark Richter, Andrew Mortimer
# Email Addresses:          meri231@uky.edu, aamo231@uky.edu
# Date:                     11/17/2023
# Purpose:                  The file manages connections between clients, and acts to relay information between them.
# Misc:                     Runs into issues when ran on the same machine as a client.
# =================================================================================================

import socket
import threading
import sys
import time
import pickle
import pygame

server = '192.168.1.26' #IP address; must match the current wifi's IP address
port = 12321
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #changed from socket to sock to avoid possible keyword

#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.bind((server, port))
except:
    print('Failed to bind socket')

sock.listen(2)  # Controls the number of connections
print('Waiting for connections...')

clientList = []  # List to keep track of connected clients

info = [[0 for i in range(12)] for j in range(2)]
# How information is layed out for sending and receiving:
# [cId, sync, playerPaddleObj.rect.y, playSendMove, opponentPaddleObj.rect.y, oppSendMove, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel, lScore, rScore]
threadLock = threading.Lock()
def clientHandler(connection: socket.socket, cId: int) -> None:
    global clientList, info, threadLock
    connection.send(str.encode(str(cId)))  #tells first connection what its id is

    if len(clientList) == 2:
        connection.sendall(str.encode("start"))
    else:
        connection.sendall(str.encode("wait"))
    while True:
        try:
            gameData = connection.recv(256) #256 is num of bits sent and received
            dataList = pickle.loads(gameData)

            if not gameData:
                print('Disconnected')
                break
            else:
                threadLock.acquire() #Threads will be accessing shared data so make sure to lock
                if dataList[0] == 0: #check id
                    dataList[4] = info[1][2] #only the player will be updating the global knowledge of their own paddle
                    dataList[5] = info[1][3]
                    info[0] = dataList
                    #print(info[0], info[1])
                    
                    if info[0][1] > info[1][1]: #sends the information based off of the higher sync variable
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    else:
                        dataList = info[1]
                        
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    
                elif dataList[0] == 1: #same as above except for other player
                    dataList[4] = info[0][2]
                    dataList[5] = info[0][3]
                    #print(info)
                    info[1] = dataList
                    if info[1][1] > info[0][1]:
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    else:
                        dataList = info[0]
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    
                threadLock.release() #Release the lock so other threads can access the shared data
                
        except: 
            break
    
    print(f'Connection with client {cId} closed') #client closed connection
    connection.close()
    clientList[cId] = None  # Set the client slot to None

def server()-> None:
    cId = 0
    threadList = []
    while True:
        connection, address = sock.accept()
        print(f"Connected to {address}")
        clientList.append(connection)  # Add the new connection to the list
        clientThread = threading.Thread(target=clientHandler, args=(connection, cId))
        threadList.append(clientThread)  # Add the new thread to the list
        clientThread.start()

        cId += 1

        if len(clientList) == 2: #Waits for there to be two clients connected before allowing them to start the game
            for client in clientList:
                client.sendall(str.encode("start"))
            break
    
    sock.close() #game has finished, close connections and join threads
    for thread in threadList:
        thread.join()

if __name__ == "__main__": #Thread protection
    server()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games