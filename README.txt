Contact Info
============

Group Members & Email Addresses:
	
    Mark Richter, meri231@uky.edu
    Andrew Mortimer, aamo231@uky.edu

Versioning
==========

Github Link: https://github.com/Fourgoblin/PongGame

General Info
============
These files implement the game pong, and allows up to two people to connect at a time. The first player to reach the score of five 
wins the game. It utilizes the pygames library and socket programming to allow each client to play on their own device across 
the same local network.

Install Instructions
====================
First download all files from the GitHub link and make sure they are in the same directory. Make sure you have pipped 
the requirements.txt file with the command below to get the proper libraries. You will want to run pongServer first on 
its own machine. You will need to make sure that the variable is equal to your current wifi's IPv4 which can be found by looking the wifi's properties.Then on separate machines each run pongClient. A menu will pop up and ask for an IP and port number. The IP
will be the same as the IP you set in pongServer, and the port will be 12321. The port can be changed to a different 
empty port if needed, but the port variable in pongServer must also be changed accordingly

`pip3 install -r requirements.txt`

Known Bugs
==========
- The opposing player's paddle will occasionally jiggle. Does not seem to have affect on game play
- Pygame continues to run after client exits.
- Server cannot be ran on same machine as a client.

