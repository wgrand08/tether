# Reason for Scorched Moon #

MoonPy was created somewhat haphazardly by modifying openRTS into an ATS game similar to OMBC. Scorched Moon is going to be built from the ground up to make a game that is designed with the exact capabilities that we need.


# Design Plans #

Scorched Moon is being designed in two parts, the server and the client. Each is going to be completely independent of the other.

## Server Design ##

The server is planned to run as a persistent service on a dedicated machine. This will allow for matchmaking capabilities and be easier for players to find others to play with. The server will handle all game logic in Scorched Moon, this includes map data. The user will submit commands directly to the server. The server will process this data then send complete map data back to the user as raw data. This includes FoW and SoW. By setting up the server this way it will allow for custom servers as well as limit player cheating as only information that the player is supposed to know is transmitted instead of all map data.

## Client Design ##

The client will be a standard GUI client using pygame and PGU as the GUI library. No game data will be handled by the client and it will simply display the map graphically, send user input to the server for processing, and play sounds. The client will also be in charge of showing reticles and aiming indicators.

## Map Ideas ##
To better fit OMBC the map will be a grid format. Each building will take a 2x2 section of the grid which each tether will take one. Each hub will be able to launch up to 12 tethers as shown in [OMBC facts](http://code.google.com/p/tether/wiki/OMBCfacts). The map will have layers so that items can be placed on top of each other. Layers from top to bottom will go, FoW, SoW, balloons, buildings, doodads (like craters), and then ground type. If sending FoW then no other layers will be sent, if sending SoW then only ground type will be sent.