Brady Wales' Term Project v1.0
####################################################################################

PROPOSAL:

Title: Zomb112

Description: A raycasting 3d game with visuals similar to Wolfenstien 3D (1992). The gameplay will be similar to the COD Zombies franchise where waves of zombies will spawn on the map and use ai to chase you down. The game will get progressively harder as you continue by spawning more in as waves increase. Once MVP is reached I hope to add randomly generated maps with maze algorithms to make sure the map is playable.

Comp Analysis: I have found people make raycasting games in python and while Zomb112 will be similar technically, I would like to have my gameplay be unique. I haven't seen anyone do a wave based shooter and I feel like I could accomplish that and make it my own. Also I am only using 112 graphics and I have seen others make it but using game engines which I will not be using.

Structural/Algorithmic Plan:
I have my code organized by functions, I haven't needed multiple files, but the main functions are raycast(app) and the draw() functions. I will need more functions such as pathfind(app,zombie) and generateMap(app).
The algorithms work together so that every time the timer is fired, it will cast rays and save the path so that when the draw() functions are called they have data of the visuals to draw.

Timeline Plan:
TP0: Working player movement with collisions
TP1: Working raycasting 
TP2: MVP: Menu Screen, Working AI with pathfinding and shooting mechanics
TP3: Extra features: Maze generation, increasing waves of ai, player upgrades, audio

Version Control Plan:
All files in termProject folder are backed up to Google Drive, see versionControlPlan.png

Module List:
pygame

TP2 Update:
Shooting, new rounds

TP3 Update:
Different modes for menu screen and gameplay
Reworked rendering and collisions
Working pathfinding, gameplay elements such as player upgrades, audio

####################################################################################
README:

DESCRIPTION:
Zomb112 is an action survival game much like the Call of Duty: Zombies franchise. In Zomb112, the player takes on increasing waves of enemies as it gets progressively harder. While the zombies get stronger so does the player. Killing zombies will award the player points that they can bring to a colored wall on the map to purchase upgrades. The game continues until the player is swarmed by the zombies and cannot keep fighting.

RUNNING:
open zomb112.py in vscode or any editor and run 

REQUIREMENTS:
pygame for audio

CONTROLS:

W: move forward		E: turn camera right
S: move backwards	Q: turn camera left
A: move left		R: reload
D: move right		F: purchase upgrades
SPACE: shoot

SHORTCUTS:
First enable debugShortCuts by pressing x on the main page
x toggles pathfinding ai
p gives player 20000 points
