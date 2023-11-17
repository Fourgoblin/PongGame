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
import pickle
import pygame

server = "localhost"   #'192.168.1.26'
port = 12321
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #changed from socket to sock to avoid possible keyword

sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    sock.bind((server, port))
except:
    print('Failed to bind socket')

sock.listen(2)  # Controls the number of connections
print('Waiting for connections...')

clientList = []  # List to keep track of connected clients

#[cId, sync, playerPaddleObj.rect.y, opponentPaddleObj.rect.y, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel, lScore, rScore]
#[cId, sync, playerPaddleObj.rect.y, playSendMove, opponentPaddleObj.rect.y, oppSendMove, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel, lScore, rScore]

info = [[0 for i in range(12)] for j in range(2)]
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
            gameData = connection.recv(256) #256 is num of bits
            dataList = pickle.loads(gameData)
            #if dataList
            #dataList = data.decode("utf-8") #dataList is string separated by :, split turns it into array based off of colons
#[cId, sync, playerPaddleObj.rect.y, playSendMove, opponentPaddleObj.rect.y, oppSendMove, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel, lScore, rScore]

            if not gameData:
                print('Disconnected')
                break
            else:
                threadLock.acquire()
                if dataList[0] == 0:
                    #threadLock.acquire()
                    dataList[4] = info[1][2]
                    dataList[5] = info[1][3]
                    info[0] = dataList
                    print(info[0], info[1])
                    
                    if info[0][1] > info[1][1]:
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    else:
                        dataList = info[1]
                        print(dataList)
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    #threadLock.release()
                elif dataList[0] == 1:
                    #threadLock.acquire()
                    dataList[4] = info[0][2]
                    dataList[5] = info[0][3]
                    print(info)
                    info[1] = dataList
                    if info[1][1] > info[0][1]:
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    else:
                        dataList = info[0]
                        gameData = pickle.dumps(dataList)
                        connection.sendall(gameData)
                    
                threadLock.release()
                #print(f'Received from Client {cId}: {dataList}') #will be in form [id, sinc, ypos, clock, score]
            
            #connection.sendall(str.encode(dataList))
        except connection as e: #connection has ended
            print(e)
            break
    
    print(f'Connection with client {cId} closed')
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

        if len(clientList) == 2:
            for client in clientList:
                client.sendall(str.encode("start"))
            break
    sock.close()
    for thread in threadList:
        thread.join()

if __name__ == "__main__":
    server()

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games