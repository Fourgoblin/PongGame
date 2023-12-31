# =================================================================================================
# Contributing Authors:	    Mark Richter, Andrew Mortimer
# Email Addresses:          meri231@uky.edu, aamo231@uky.edu
# Date:                     11/17/2023
# Purpose:                  This file acts to run the pong game, and to update any information related to it.
#                           Receives information from the other client from the server, and updates accordingly.                            
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import time
import pickle

setWidth = 640 #constant for screen width
setHeight = 480 #constant for screen height

from assets.code.helperCode import *

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket, cId:int) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 1024)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 50
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

    if playerPaddle == "left":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    sync = 0

    while True:
        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""

        # =========================================================================================
        # We did all of the sending and receiving of information at the end of the loop
        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # If the game is over, display the win message
        if lScore > 4 or rScore > 4:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            screen.blit(textSurface, textRect)
            
        else:

            # ==== Ball Logic =====================================================================
            ball.updatePos()

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screenWidth:
                lScore += 1
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
                
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        updateScore(lScore, rScore, screen, WHITE, scoreFont)
        pygame.display.flip()
        clock.tick(60)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        sync += 1
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game

        playSendMove = 0
        oppSendMove = 0
        if playerPaddleObj.moving == "up": #encode the string for movement as an integer before sending
            playSendMove = 1
        elif playerPaddleObj.moving == "down":
            playSendMove = 2
       
        if opponentPaddleObj.moving == "up":
            oppSendMove = 1
        elif opponentPaddleObj.moving == "down":
            oppSendMove = 2
        #all of the information being sent to the server is a list of integers
        dataList = [cId, sync, playerPaddleObj.rect.y, playSendMove, opponentPaddleObj.rect.y, oppSendMove, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel, lScore, rScore] 
        
        try:
            gameData = pickle.dumps(dataList) #pickle to encode the data
            client.sendall(gameData)
        except:
            break
        

        try:       
            incomeData = client.recv(1024)
            updateData = pickle.loads(incomeData) #receive and decode the data from server, will be from higher of the two sync variables
            plUpdateMove = 0
            if updateData[5] == 1:
                plUpdateMove = "up"
            elif updateData[5] == 2:
                plUpdateMove = "down"
            elif updateData[5] == 0:
                plUpdateMove = ""

            if updateData[0] != cId: #update all of the information from the server to the player's based of ID

                sync = updateData[1]

                opponentPaddleObj.moving = plUpdateMove
                opponentPaddleObj.rect.y = updateData[2]
                ball.rect.x = updateData[6]
                ball.rect.y = updateData[7]
                ball.xVel = updateData[8]
                ball.yVel = updateData[9]
                lScore = updateData[10]
                rScore = updateData[11]
            else:
                opponentPaddleObj.rect.y = updateData[4]
                opponentPaddleObj.moving = plUpdateMove
                ball.rect.x = updateData[6]
                ball.rect.y = updateData[7]
                ball.xVel = updateData[8]
                ball.yVel = updateData[9]
        except:
            break
  
        # =========================================================================================




# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip: str, port: str, errorLabel: tk.Label, app: tk.Tk) -> None:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((ip, int(port)))
        ID = client.recv(1024).decode()
        ID = int(ID)
        side = ""

        if ID == 0:
            side = "left"
        elif ID == 1:
            side = "right"
        else:
            pass  # Add spectator logic here if needed


        # Wait for the second player to join before starting the game loop
        startData = client.recv(1024).decode()
        while startData == "wait":
            errorLabel.config(text=f'Waiting for the other player to connect')
            errorLabel.update()
            startData = client.recv(1024).decode()


        app.withdraw()

        playGame(setWidth, setHeight, side, client, ID)

        app.quit()
        client.close()

    except:
        pass
        #print(socket.error())

    # Get the required information from your server (screen width, height & player paddle, "left or "right)

    # Close this window and start the game with the info passed to you from the server
    #app.withdraw()     # Hides the window (we'll kill it later)
    #playGame(screenWidth, screenHeight, ("left"|"right"), client)  # User will be either left or right paddle
    #app.quit()         # Kills the window


# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

if __name__ == "__main__":
    startScreen()
    
    # Uncomment the line below if you want to play the game without a server to see how it should work
    # the startScreen() function should call playGame with the arguments given to it by the server this is
    # here for demo purposes only
    # playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))