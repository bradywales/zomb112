################################################################################
# Zomb112
# by Brady Wales
################################################################################
from cmu_112_graphics import *
import math
import time
import random
pi = math.pi
import pygame

# From 112 notes, https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
def almostEqual(d1, d2, epsilon=10**-7):
    return (abs(d2 - d1) < epsilon)
    
class Sound(object):
    def __init__(self, path):
        self.path = path
        self.loops = 1
        pygame.mixer.music.load(path)

    # Returns True if the sound is currently playing
    def isPlaying(self):
        return bool(pygame.mixer.music.get_busy())

    # Loops = number of times to loop the sound. 
    # If loops = 1 or 1, play it once.
    # If loops > 1, play it loops + 1 times.
    # If loops = -1, loop forever.
    def start(self, loops=1):
        self.loops = loops
        pygame.mixer.music.play(loops=loops)

    # Stops the current sound from playing
    def stop(self):
        pygame.mixer.music.stop()


class Zombie(object):
        #Initializes new zombie
        def __init__(self, app, x, y, health = 25):
            self.x = x
            self.y = y 
            self.health = health
            self.renderSize = 1
            self.app = app
            self.distToPlayer = math.sqrt((self.x-app.playerX)**2+(self.y-app.playerY)**2)
            self.size = 1/self.distToPlayer*10
            self.sprite = app.zombieSprite
            self.sprite = app.scaleImage(app.zombieSprite,self.size)
            self.angle = self.getAngleFromPlayer(app)
            self.isVisible = True
            self.offscreen = True
            self.offsetAngle = 0
            self.r = 1
            self.isAlive = 1
            self.type = "Zombie"
            self.path = []
            self.canSeePlayer = False



        # Scales zombie as they move to create distance
        def resize(self,app):
            if self.distToPlayer > 4:
                self.size = 125/self.distToPlayer
            else: 
                self.size = 125/4
            if self.isAlive:
                self.sprite = app.scaleImage(app.zombieSprite,self.size)
            else: self.sprite = app.scaleImage(app.deadZombieSprite,self.size)
            
        # Sets angles needed in calculations
        def getAngles(self,app):
            self.distToPlayer = math.sqrt((self.x-app.playerX)**2+(self.y-app.playerY)**2)
            self.angle = self.getAngleFromPlayer(app)

        # Helper for getAngles()
        def getAngleFromPlayer(self,app):
            dX = self.x - app.playerX
            dY = app.playerY - self.y
            angle = math.atan2(dY,dX)+2*pi
            angle %= 2*pi
            self.angle = angle
            self.angleToPlayer = math.atan2(-dY,-dX)+2*pi
            self.angleToPlayer %= 2*pi
            return(angle)

        # used in calculations and rendering, gets offset from player direction to angle the zombie is at
        def getOffsetAngle(self,app):
            tempPlayerDir = app.playerDir
            if app.playerDir < pi/2 and self.angle > 3*pi/2:
                tempPlayerDir += 2*pi
            self.offsetAngle = tempPlayerDir - self.angle
            return self.offsetAngle

        # Checks if zombie is behind a wall
        def checkIfVisible(self,app):
            if (self.angle < app.playerDir and self.angle > app.playerDir-math.radians(app.rays/2)):
                self.r = int(math.degrees(self.angle - (app.playerDir-math.radians(app.rays/2))))
                self.offscreen = False
            elif ((self.angle) < app.playerDir+math.radians(app.rays/2) and (self.angle) > app.playerDir):
                self.r = int(math.degrees((self.angle) - (app.playerDir-math.radians(app.rays/2))))
                self.offscreen = False
            elif (self.angle > 3*pi/2 and app.playerDir < pi/2 and self.angle < app.playerDir+math.radians(app.rays/2)+2*pi and self.angle > app.playerDir-math.radians(app.rays/2)+2*pi):
                self.r = int(math.degrees((self.angle) - (app.playerDir+2*pi-math.radians(app.rays/2))))
                self.offscreen = False
            elif ((self.angle < pi/2 and app.playerDir > 3*pi/2) and self.angle+2*pi < app.playerDir+math.radians(app.rays/2) and self.angle+2*pi > app.playerDir-math.radians(app.rays/2)):
                self.r = int(math.degrees((self.angle+2*pi) - (app.playerDir-math.radians(app.rays/2))))
                self.offscreen = False
            elif self.angle > app.playerDir-math.radians(app.rays/2) and self.angle < app.playerDir+math.radians(app.rays/2):
                self.offscreen = False
            else: self.offscreen = True
            wallX = app.lines[self.r][0]
            wallY = app.lines[self.r][1]
            distFromPlayerToWall = math.sqrt((wallX-app.playerX)**2+(wallY-app.playerY)**2)
            self.isVisible = distFromPlayerToWall > self.distToPlayer
            return

        # Rewritten raycasting() function, checks if zombie is in field of view
        def checkIfCanSeePlayer(self,app):
            x, y = self.x, self.y
            theta = self.angleToPlayer
            if theta > 2*pi:
                theta %= 2*pi
            if theta < 0:
                theta += 2*pi
            if almostEqual(theta, 0) or almostEqual(theta, 2*pi):
                theta = 0
                hdx, hdy = 0, 0
                vdx, vdy = app.cellSize - x%app.cellSize, 0
                hxOffset, hyOffset = 0, 0
                vxOffset, vyOffset = 1, 0
            elif almostEqual(theta, pi/2):
                theta = pi/2
                hdx, hdy = 0, -y%app.cellSize
                vdx, vdy = 0, 0
                hxOffset, hyOffset = 0, -1
                vxOffset, vyOffset = 0, 0

            elif almostEqual(theta, pi):
                theta = pi
                hdx, hdy = 0, 0
                vdx, vdy = -(x%app.cellSize), 0
                hxOffset, hyOffset = 0, 0
                vxOffset, vyOffset = -1, 0

            elif almostEqual(theta, 3*pi/2):
                theta = 3*pi/2
                hdx, hdy = 0, -(app.cellSize-y%app.cellSize)
                vdx, vdy = 0, 0
                hxOffset, hyOffset = 0, 1
                vxOffset, vyOffset = 0, 0
            else:
                ## find first intersect with horizontal line
                if theta < pi: # looking negative y
                    hdy = app.cellSize - y%app.cellSize
                    hdx = hdy/math.tan(theta)
                    hyOffset = -1
                    vyOffset = -abs(math.tan(theta))

                else: # looking positive y
                    hdy = -(app.cellSize-y%app.cellSize)
                    hdx = hdy/math.tan(theta)
                    hyOffset = 1
                    vyOffset = abs(math.tan(theta))

                ## find first intersect with vertical line
                if theta > 3*pi/2 or theta < pi/2: # looking positive x
                    vdx = app.cellSize - x%app.cellSize
                    vdy = vdx*math.tan(theta)
                    
                    hxOffset = abs(1/math.tan(theta))
                    vxOffset = 1
                else: # looking negative x
                    vdx = -(x%app.cellSize)
                    vdy = vdx*math.tan(theta)

                    hxOffset = -abs(1/math.tan(theta))
                    vxOffset = -1

            #app.rays = [hdx,hdy,vdx,vdy]
            app.offsets = [hxOffset,hyOffset,vxOffset,vyOffset]
            hdist = (hdx**2+hdy**2)**(1/2)
            vdist = (vdx**2+vdy**2)**(1/2)
            #print((hdx,hdy),(vdx,vdy))
            #print((hxOffset,hyOffset),(vxOffset,vyOffset))
            count = 0
            startVCells = getCellFromPixels(app,x+vdx,y-vdy)
            startvXCell = startVCells[0]
            startvYCell = startVCells[1]
            
            foundH = False
            foundV = False
            if theta != pi and theta != pi*2 and theta != 0:
                while True:
                    # Check Horizontal Line
                    # Find intersect with horizontal line:
                    temphX = x+hdx+(count*hxOffset)
                    temphY = y-hdy+(count*hyOffset)
                    if theta == 0 or theta == pi or theta == 2*pi:
                        break
                    if not (temphX > app.cellSize*app.cols or temphX < 0 or 
                            temphY > app.cellSize*app.rows or temphY < 0):
                        cell = getCellFromPixels(app,temphY+hyOffset,temphX)
                        if cell[0] > app.rows or cell[1]>app.cols:
                            break
                        if app.map[cell[0]][cell[1]] != 0:
                            finalhX, finalhY = temphX, temphY
                            #print(finalhCount)
                            foundH = True
                            break
                    else:
                        break
                    count+=1

            count = 0
            if theta != pi/2 and theta != 3*pi/2:
                while True:                
                    # Find intersect with vertical line:
                    tempvX = x+vdx+(count*vxOffset)
                    tempvY = y-vdy+(count*vyOffset)
                    if theta == pi/2 or theta == pi/2:
                        break
                    if not (tempvX > app.cellSize*app.cols or tempvX < 0 or 
                            tempvY > app.cellSize*app.rows or tempvY < 0):
                        cell = getCellFromPixels(app,tempvY,tempvX+vxOffset)
                        if cell[0] > app.rows or cell[1]>app.cols:
                            break
                        elif app.map[cell[0]][cell[1]] != 0:
                            finalvX, finalvY = tempvX, tempvY
                            foundV = True
                            break
                    else:
                        break
                    count+=1

            if foundV and foundH:
                hdist = ((x-finalhX)**2+(y-finalhY)**2)**(1/2)
                vdist = ((x-finalvX)**2+(y-finalvY)**2)**(1/2)
                if hdist < vdist:  
                    foundV = False
                else:
                    foundH = False

            if foundV:
                finalDist = ((x-finalvX)**2+(y-finalvY)**2)**(1/2)
                
                


            elif foundH:
                finalDist = ((x-finalhX)**2+(y-finalhY)**2)**(1/2)
            
            if finalDist < self.distToPlayer:
                self.canSeePlayer = False
            else:
                self.canSeePlayer = True

            
        # Part of pathfinding, moves zombie towards next step in path
        def moveTowardsNextEntryAlongPath(self,app):
            if self.path != False:
                currRow = int(int(self.y)//app.cellSize)
                currCol = int(int(self.x)//app.cellSize)
                if (currRow,currCol) == self.path[0]:
                    dY = (currRow-self.path[1][0])*app.zombieSpeed
                    dX = (currCol-self.path[1][1])*app.zombieSpeed
                else:
                    dY = (currRow-self.path[0][0])*app.zombieSpeed
                    dX = (currCol-self.path[0][1])*app.zombieSpeed
                self.x -= dX
                self.y -= dY

# Called to create a new round, resets health every 5 rounds and ammo every 4
def newRound(app, zombies):
    app.aliveZombies = zombies
    if "Quick Revive" in app.perks or app.round%5 == 0:
        app.playerHealth = app.maxHealth
    if app.round%4 == 0:
        app.tempAmmo = app.maxAmmo
    for zombie in range(zombies):
        spawnZombie(app)
    while len(app.zombies) > zombies+1:
        app.zombies = app.zombies[1:]

# Main function when app started
def appStarted(app):
    app._title = "Zomb112 by Brady Wales"
    app.mode = "splashScreenMode"
    app.debugShortcuts = False
    pygame.mixer.init() 
    # Sounds from https://www.youtube.com/watch?v=AShdfcWla6M
    # https://www.youtube.com/watch?v=wMGMJ7tw5ew
    # https://www.youtube.com/watch?v=x4CTvpffT8Y
    # https://www.youtube.com/watch?v=_4MvHGw62CI
    # https://www.youtube.com/watch?v=M7pV7J9I8Sc

    # Weapon sprites from https://www.spriters-resource.com/pc_computer/doomdoomii/sheet/4111/
    # Zombie sprite from https://i.pinimg.com/originals/2a/99/a8/2a99a878e17b7527ea1f72b7730c6be9.gif
    # Perk icons from https://forum.plutonium.pw/assets/uploads/files/1626545022323-perks.png
    # Pack a Punch sprites edited from https://www.spriters-resource.com/pc_computer/doomdoomii/sheet/4111/
    # Splash Screen from https://i.ytimg.com/vi/KH6VObZQuAU/maxresdefault.jpg
    app.shotgunSprite = app.loadImage('./images/shotgun.png')
    app.shotgunSprite = app.scaleImage(app.shotgunSprite,2.5)
    app.reloadSprite = app.loadImage('./images/reloading.png')
    app.reloadSprite = app.scaleImage(app.reloadSprite,2.5)
    app.muzzleBlastSprite = app.loadImage('./images/muzzleBlast.png')
    app.muzzleBlastSprite = app.scaleImage(app.muzzleBlastSprite,2.5)
    app.splashScreenImage = app.loadImage('./images/splashScreen.jpeg')

    app.zombieSprite = app.loadImage('./images/zombie.png')
    app.deadZombieSprite = app.loadImage('./images/deadZombie.png')
    app.jugIcon = app.loadImage("./images/jug.png")
    app.colaIcon = app.loadImage("./images/cola.png")
    app.staminupIcon = app.loadImage("./images/staminup.png")
    app.quickReviveIcon = app.loadImage("./images/quickRevive.png")
    app.usingPathFinding = False
    app.sound = Sound("./audio/theme.mp3")
    app.sound.start(-1)
    app.holdingButton = False
    app.menu = 0

# Stops sounds from playing when app closed
def gameMode_appStopped(app):
    app.sound.stop()

# Stops sounds from playing when app closed
def splashScreenMode_appStopped(app):
    app.sound.stop()

# Starts a new game after beginning of restarting
def newGame(app):
    app.gameOver = False
    app.sound = Sound("./audio/newGame.mp3")
    app.margin = 0
    app.count = 0
    app.lastTime = time.time()
    app.fps = 0
    app.timer = 0
    app.map =   [[1,1,1,1,1,1,1,1,1,1,1],
                [1,0,0,0,0,0,0,0,0,0,1],
                [1,0,1,1,0,0,0,1,1,0,1],
                [1,0,1,0,0,0,0,0,1,0,1],
                [1,0,1,0,0,0,0,0,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,0,0,0,0,0,0,0,1],
                [1,0,0,1,1,0,1,1,0,0,1],
                [1,0,1,1,0,0,0,1,1,0,1],
                [1,0,0,0,0,0,0,0,0,0,1],
                [1,1,1,1,1,1,1,1,1,1,1]]
    app.rows = len(app.map)
    app.cols = len(app.map[0])
    app.wallColor = "#4d2323"
    app.darkWallColor = "#381313"
    app.skyColor = "darkslategrey"
    app.floorColor = "grey34"
    app.randomPerks = False
    if app.randomPerks == True:
        for item in ["red","green","orange","turquoise","magenta"]:
            while True:
                row = random.randint(2,app.rows-2) 
                col = random.randint(2,app.cols-2)
                if app.map[row][col] == 1:
                    if (row,col) == (0,0) or (row,col) == (app.rows-1,app.cols-1) or (row,col) == (app.rows-1,0) or (row,col) == (0,app.cols-1):
                        continue
                    else:
                        app.map[row][col] = item
                        break
    else:
        app.map[2][2] = "red"
        app.map[8][2] = "green"           
        app.map[2][8] = "orange"
        app.map[8][8] = "turquoise"
        app.map[0][5] = "magenta"         
    app.cellSize = int(app.width/7/app.cols)
    app.playerX, app.playerY = (4*app.cellSize)+app.cellSize*3/2, app.cellSize*3/2
    app.maxHealth = 100
    app.playerHealth = 100
    app.lines = []  
    app.rays = int((app.width-app.height)/8)
    app.pressedKeys = set()
    app.playerDir = 3*pi/2
    app.directionKeys = {"Left","Right","Up","Down","w","a","s","d","q","e"}
    app.playerSize = app.cellSize/1.5
    app.playerHeight = 25
    app.mapSize = app.cellSize*app.rows
    raycast(app)
    app.changeDir = 0
    app.step = app.cellSize/4
    app.timerDelay = 20
    app.movementSpeed = 1.5
    app.rotationSpeed = 0.02
    app.shootingRange = 100
    app.damage = 25
    app.muzzleFlashing = 0
    app.clip = 2
    app.maxClip = 2
    app.reloading = 0
    app.reloadSpeed = 1.12
    app.maxAmmo = 35
    app.tempAmmo = 35
    app.canBuyPerk = None
    app.canPaP = False
    app.papPrice = 5000
    app.pap = False
    app.perks = []
    app.score = 0
    app.jugPrice = 2500
    app.colaPrice = 3000
    app.staminupPrice = 2000
    app.quickRevivePrice = 1500
    app.round = 1
    app.path = []

    app.zombieHealth = 25
    app.zombieSpeed = 0.3
    app.zombieDamage = 2
    app.zombieReach = 10
    app.zombies = []

    
    newRound(app,1)
    app.sound.start()
    
    app.aliveZombies = len(app.zombies)
    app.finalList = []

    app.shotgunSprite = app.loadImage('./images/shotgun.png')
    app.shotgunSprite = app.scaleImage(app.shotgunSprite,2.5)
    app.reloadSprite = app.loadImage('./images/reloading.png')
    app.reloadSprite = app.scaleImage(app.reloadSprite,2.5)
    app.muzzleBlastSprite = app.loadImage('./images/muzzleBlast.png')
    app.muzzleBlastSprite = app.scaleImage(app.muzzleBlastSprite,2.5)
##########################################
# Splash Screen Mode
##########################################

# Draws splash screen menu
def splashScreenMode_redrawAll(app, canvas):
    font = 'Helvetica 90 bold'
    canvas.create_image(app.width/2,app.height/2, image = ImageTk.PhotoImage(app.splashScreenImage))
    canvas.create_text(app.width/2, app.height/6+1, text='Zomb112',
                       font=font, fill='ivory2')
    canvas.create_text(app.width/2, app.height/6, text='Zomb112',
                       font=font, fill='dark red')

    
    canvas.create_text(app.width/2, app.height/6+60, text=f'by Brady Wales',
                       font='Helvetica 20 italic', fill='light grey')

    if app.menu == 0: 
        canvas.create_rectangle(app.width/2-70,app.height*.55-20,app.width/2+70,app.height*.55+20,fill="dark red")  
        if app.holdingButton == False:
            canvas.create_text(app.width/2,app.height*.55,text="New Game",font = 'Helvetica 20', fill ='ivory2')
        else:
            canvas.create_text(app.width/2,app.height*.55,text="New Game",font = 'Helvetica 20', fill ='ivory4')
    else:
        canvas.create_rectangle(app.width/4,app.height/2.5,app.width*3/4,app.height*3/4,fill="ivory2")
        canvas.create_text(app.width/2,app.height/2,fill = "dark red", text = "Would you like to play with basic or advanced ai pathfinding? \n Basic runs faster and provides a smoother experience but zombies can get stuck, \n Advanced limits number of zombies and may cause performance issues.",justify = CENTER, font = 'Helvetica 13')
        
        canvas.create_rectangle(app.width/4+20,app.height/1.7,app.width/4+20+app.width/6,app.height/1.7+50,fill="dark red")
        canvas.create_rectangle(app.width*3/4-20,app.height/1.7,app.width*3/4-20-app.width/6,app.height/1.7+50,fill="dark red")

        if app.holdingButton == 1:
            canvas.create_text(app.width/4+20+app.width/12,app.height/1.7+25,text="Basic",fill ="ivory4",font = "helvetica 17")
        else:
            canvas.create_text(app.width/4+20+app.width/12,app.height/1.7+25,text="Basic",fill ="ivory2",font = "helvetica 17")
        if app.holdingButton == 2:
            canvas.create_text(app.width*3/4-20-app.width/12,app.height/1.7+25,text="Advanced",fill ="ivory4",font = "helvetica 17")
        else:
            canvas.create_text(app.width*3/4-20-app.width/12,app.height/1.7+25,text="Advanced",fill ="ivory2",font = "helvetica 17")

# Checks whether player pressed button
def splashScreenMode_mousePressed(app, event):
    if app.menu == 0:
        if (app.width/2-70 < event. x < app.width/2+70) and (app.height*.55-20 < event.y < app.height*.55+20):
            app.holdingButton = True
    
    elif (app.width/4+20 < event.x < app.width/4+20+app.width/6) and (app.height/1.7 < event.y < app.height/1.7+50):
        app.holdingButton = 1
    elif (app.width*3/4-20 > event.x > app.width*3/4-20-app.width/6) and (app.height/1.7 < event.y < app.height/1.7+50):
        app.holdingButton = 2
    
# Checks whether player released button
def splashScreenMode_mouseReleased(app,event):
    if app.menu == 0:
        if (event.x > app.width/2-70 and event. x < app.width/2+70) and (event.y > app.height*.55-20 and event.y < app.height*.55+20) and app.holdingButton: 
            app.menu+=1
            app.holdingButton = 0
        else: 
            app.holdingButton = False

    elif (app.width/4+20+app.width/12 < event.x < app.width/4+20+app.width/6) and (app.height/1.7 < event.y < app.height/1.7+50) and app.holdingButton == 1:
        app.usingPathFinding = False
        newGame(app)
        app.mode = 'gameMode'
    elif (app.width*3/4-20 > event.x > app.width*3/4-20-app.width/6) and (app.height/1.7 < event.y < app.height/1.7+50) and app.holdingButton == 2:
        app.usingPathFinding = True
        newGame(app)
        app.mode = 'gameMode'
    else: app.holdingButton = 0

def splashScreenMode_keyPressed(app,event):
    if event.key == "x":
        app.debugShortcuts = True
    



##########################################
# Game Mode
##########################################

# Timer fired, calulates shooting, reloading, player and zombie movement, raycasting, if player can buy perks
def gameMode_timerFired(app):
    if not app.gameOver:
        #print("1")
        if app.playerDir < 0:
            app.playerDir = app.playerDir+2*pi
        elif app.playerDir > 2*pi:
            app.playerDir = app.playerDir-2*pi
        #elif almostEqual(app.playerDir,0) or almostEqual(app.playerDir,2*pi):
        #    app.playerdir = 0
        app.lines = []
        if app.muzzleFlashing > 0:
            app.muzzleFlashing -= 0.1
        if app.muzzleFlashing < 0:
            app.muzzleFlashing = 0
            if app.sound.path == 'shotgun.mp3' or app.sound.path == 'packapunch.mp3':
                app.sound.stop()
        if app.reloading > 0:
            if app.clip == 0:
                app.reloading -= 0.05*app.reloadSpeed
            else:
                app.reloading -= 0.1*app.reloadSpeed
            if app.reloading <= 0:
                if app.tempAmmo < app.maxClip:
                        app.clip+=app.tempAmmo
                        app.tempAmmo = 0
                else:
                    app.tempAmmo -= (app.maxClip-app.clip)
                    app.clip = app.maxClip
                app.reloading = 0
        #print("2")
        if not almostEqual(app.changeDir, 0):
            app.playerDir += app.changeDir
            app.changeDir = 0
        #print("3")
        raycast(app)

        #print("4")
        if "Up" in app.pressedKeys or "w" in app.pressedKeys:
            dX = app.movementSpeed*math.cos(app.playerDir)
            dY = -app.movementSpeed*math.sin(app.playerDir)
            if almostEqual(dX,0):
                dX = 0
            if almostEqual(dY,0):
                dY = 0
            if isValidMove(app,dX,dY,"player"):
                app.playerX += dX
                app.playerY += dY



        if "Down" in app.pressedKeys or "s" in app.pressedKeys:
            dX = -app.movementSpeed*math.cos(app.playerDir)*3/4
            dY = app.movementSpeed*math.sin(app.playerDir)*3/4
            if almostEqual(dX,0):
                dX = 0
            if almostEqual(dY,0):
                dY = 0
            if isValidMove(app,dX,dY,"player"):
                app.playerX += dX
                app.playerY += dY

        if "Right" in app.pressedKeys or "e" in app.pressedKeys:
            app.playerDir -=  app.rotationSpeed*pi/32
            if app.rotationSpeed < 0.7:
                app.rotationSpeed += 0.07
            
        if "d" in app.pressedKeys:
            dX = app.movementSpeed*math.cos(app.playerDir-pi/2)*3/4
            dY = -app.movementSpeed*math.sin(app.playerDir-pi/2)*3/4
            if almostEqual(dX,0):
                dX = 0
            if almostEqual(dY,0):
                dY = 0
            if isValidMove(app,dX,dY,"player"):
                app.playerX += dX
                app.playerY += dY


        if "Left" in app.pressedKeys or "q" in app.pressedKeys:
            app.playerDir += app.rotationSpeed*pi/32
            if app.rotationSpeed < 0.7:
                app.rotationSpeed += 0.07

        if "a" in app.pressedKeys:
            dX = app.movementSpeed*math.cos(app.playerDir+pi/2)*3/4
            dY = -app.movementSpeed*math.sin(app.playerDir+pi/2)*3/4
            if almostEqual(dX,0):
                dX = 0
            if almostEqual(dY,0):
                dY = 0
            if isValidMove(app,dX,dY,"player"):
                app.playerX += dX
                app.playerY += dY

        #print("5")
        app.count+=1
        app.timer = time.time()-app.lastTime
        if app.timer > 1:
            app.lastTime = time.time()
            app.fps = app.count
            app.count = 0
        #print(6)

        for zombie in app.zombies:
            #zombie.getAngles(app)
            if zombie.isAlive:
                if zombie.distToPlayer>app.zombieReach:
                    moveZombie(app,zombie)
                    if not zombie.offscreen:
                        zombie.resize(app)
                else:
                    takeDamage(app)
            elif zombie.offscreen or zombie.distToPlayer < app.zombieReach:
                app.zombies.remove(zombie)
            else: zombie.resize(app)
            zombie.getAngles(app)
            if zombie.distToPlayer>5: 
                zombie.checkIfVisible(app)
                zombie.checkIfCanSeePlayer(app)
        app.zombies.sort(key=lambda x: x.distToPlayer, reverse = True)


        if app.aliveZombies == 0:
            app.round+=1
            if app.zombieSpeed < 0.75:
                app.zombieSpeed *= 1.15
            if app.zombieDamage < 3:
                app.zombieDamage+=1
            newZombies = int(math.log(app.round,2.17)*3+2)
            if app.usingPathFinding:
                if newZombies > 4:
                    newZombies = 4
            elif newZombies > 6:
                newZombies = 6
            newRound(app,newZombies)
            app.score += 200
            if not (app.sound.isPlaying() and app.sound.path == "./audio/newGame.mp3"):
                app.sound.stop()
                app.sound = Sound("./audio/newRound.mp3")
                app.sound.start()

        # Returns [finalX,finalY,finalDist,finalColor,r,h]
        if app.lines[int(app.rays/2)][3] != app.wallColor and app.lines[int(app.rays/2)][3] != app.darkWallColor and app.lines[int(app.rays/2)][2] < app.cellSize:
            if app.lines[int(app.rays/2)][3] == "red" or app.lines[int(app.rays/2)][3] == "dark red":
                app.canBuyPerk = "Juggernog"
            elif app.lines[int(app.rays/2)][3] == "green" or app.lines[int(app.rays/2)][3] == "dark green":
                app.canBuyPerk = "Speed Cola"
            elif app.lines[int(app.rays/2)][3] == "orange" or app.lines[int(app.rays/2)][3] == "dark orange":
                app.canBuyPerk = "Stamin-Up"
            elif app.lines[int(app.rays/2)][3] == "turquoise" or app.lines[int(app.rays/2)][3] == "dark turquoise":
                app.canBuyPerk = "Quick Revive"
            else:
                if app.pap == False:
                    app.canPaP = True
            if app.canBuyPerk in app.perks:
                    app.canBuyPerk = None
        else:
            app.canBuyPerk = None
            app.canPaP = False
        app.finalList = createSortedList(app)

    
# Function to move zombie as timer is fired
def moveZombie(app,zombie):
    inStartingWall = 0
    if int(int(zombie.y)//app.cellSize) == 0:
        zombie.angleToPlayer = 3*pi/2
        inStartingWall = 1
    elif int(int(zombie.y)//app.cellSize) == app.rows-1:
        zombie.angleToPlayer = pi/2
        inStartingWall = 1
    elif int(int(zombie.x)//app.cellSize) == 0:
        zombie.angleToPlayer = 0
        inStartingWall = 1
    elif int(int(zombie.x)//app.cellSize) == app.cols-1:
        zombie.angleToPlayer = pi
        inStartingWall = 1
        
    dX = app.zombieSpeed*math.cos(zombie.angleToPlayer)
    dY = -app.zombieSpeed*math.sin(zombie.angleToPlayer)
    
    if inStartingWall:
        zombie.x += dX
        zombie.y += dY
    
    elif app.usingPathFinding:
        if zombie.canSeePlayer:
            zombie.x += dX
            zombie.y += dY
            zombie.path = []
        else:
            pathfindZombieToPlayer(app,zombie)
            zombie.moveTowardsNextEntryAlongPath(app)
    else: 
            if isValidMove(app,dX,dY,zombie):
                zombie.x += dX
                zombie.y += dY
                return
            else: 
                if app.playerX >= zombie.x:
                    if isValidMove(app,app.zombieSpeed,0,zombie):
                        zombie.x += app.zombieSpeed
                    elif isValidMove(app,-app.zombieSpeed,0,zombie):
                        zombie.x -= app.zombieSpeed
                else:
                    if isValidMove(app,-app.zombieSpeed,0,zombie):
                        zombie.x -= app.zombieSpeed
                    elif isValidMove(app,app.zombieSpeed,0,zombie):
                        zombie.x += app.zombieSpeed

                if app.playerY >= zombie.y:
                    if isValidMove(app,0,app.zombieSpeed,zombie):
                        zombie.y += app.zombieSpeed
                        
                    elif isValidMove(app,0,-app.zombieSpeed,zombie):
                        zombie.y -= app.zombieSpeed
                        
                else:
                    if isValidMove(app,0,-app.zombieSpeed,zombie):
                        zombie.y -= app.zombieSpeed
                        
                    elif isValidMove(app,0,app.zombieSpeed,zombie):
                        zombie.y += app.zombieSpeed
                        
        

# When zombie reaches player, player takes damage
def takeDamage(app):
    app.playerHealth -= app.zombieDamage
    if app.playerHealth <= 0:
        app.playerHealth = 0
        app.gameOver = True
        app.sound.stop()
        app.sound = Sound("./audio/gameOver.mp3")
        app.sound.start()

# Main function to generate path to player, inspired by 112 maze solver https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#mazeSolving
def pathfindZombieToPlayer(app,zombie):
    gridRow = int(int(zombie.y)//app.cellSize)
    gridCol = int(int(zombie.x)//app.cellSize)
    playerRow = int(int(app.playerY)//app.cellSize)
    playerCol =int(int(app.playerX)//app.cellSize)
    visited = []
    dx = gridCol- playerCol
    dy = gridRow-playerRow
    orderedDirs = orderList(dx,dy)
    otherDirs = [orderedDirs[2],orderedDirs[3],orderedDirs[0],orderedDirs[1]]
    newPath = solve(app,gridRow,gridCol,playerRow,playerCol,visited,orderedDirs)
    otherPath = solve(app,gridRow,gridCol,playerRow,playerCol,visited,otherDirs)
    if otherPath != False:
        if len(newPath) < len(otherPath):
            newPath = otherPath
    if zombie.path == []:
        zombie.path = newPath
    else:
        zombie.path = newPath

# Helper for pathfinding, decides which directions to try based off distance to player
def orderList(dx,dy):
    orderedList = [(0,0),(0,0),(0,0),(0,0)]
    if dy > 0:
        firstY = (-1,0)
    else: firstY = (1,0)
    if dx > 0:
        firstX = (0,-1)
    else: firstX = (0,1)

    secondY = (firstY[0]*-1,0)
    secondX = (0,firstX[1]*-1)

    if dx == 0:
        orderedList = [firstY,firstX,secondY,secondX]
    elif dy == 0:
        orderedList = [firstX,firstY,secondX,secondY]
    elif abs(dx)>abs(dy):
        orderedList = [firstY,firstX,secondY,secondX]
    else:
        orderedList = [firstX,firstY,secondX,secondY]
    
    return orderedList

# Inspired by 112 maze solving algorithm https://www.cs.cmu.edu/~112/notes/notes-recursion-part2.html#mazeSolving
# Recursive function to try to find path to player
def solve(app,row,col,playerRow,playerCol,visited,orderedDirs):
    # base cases
    if (row,col) in visited: return False
    visited.append((row,col))
    if (row,col)==(playerRow,playerCol): return visited
    # recursive case
    if row != playerRow and col != playerCol:
        orderedDirs = [orderedDirs[1],orderedDirs[0],orderedDirs[3],orderedDirs[2]]
    for drow,dcol in orderedDirs:
        drow = int(drow)
        dcol = int(dcol)
        if app.map[row+drow][col+dcol] == 0:
            if solve(app,row+drow,col+dcol,playerRow,playerCol,visited,orderedDirs): return visited
    visited.pop(-1)
    return False

# Returns whether player or zombie will run into wall
def isValidMove(app,dX,dY,playerOrZombie):
    if playerOrZombie == "player":
        x = app.playerX
        y = app.playerY
    else:
        x = playerOrZombie.x
        y = playerOrZombie.y
    gridRow = int(int(y)//app.cellSize)
    gridCol = int(int(x)//app.cellSize)
    xDir = 0
    yDir = 0
    checkCol = 0
    checkRow = 0


    if dX < 0:
        if int(((x)-(app.playerSize/2))%int((app.cellSize))) < -dX:
            xDir = -1
        if int(((x)-(app.playerSize/2)))%int((app.cellSize)) > int(((x))%int((app.cellSize))):
            checkCol = -1
    elif int(((x)+(app.playerSize/2))%int((app.cellSize))) >= app.cellSize-dX:
        xDir = +1
        if int(((x)+(app.playerSize/2)))%int((app.cellSize)) < int(((x))%int((app.cellSize))):
            checkCol = +1

    if dY < 0:
        if int(((y)-(app.playerSize/2))%int((app.cellSize))) < -dY:
            yDir = -1
        if int(((y)-(app.playerSize/2)))%int((app.cellSize)) > int(((y))%int((app.cellSize))):
            checkRow = -1
    elif int(((y)+(app.playerSize/2))%int((app.cellSize))) >= app.cellSize-dY:
        yDir = +1
        if int(((y)+(app.playerSize/2)))%int((app.cellSize)) < int(((y))%int((app.cellSize))):
            checkRow = +1
    

    cellsWithin = (getCellsWithin(app,x,y))
    if playerOrZombie == "player":
        for cell in cellsWithin:
            if app.map[gridRow+cell[0]][gridCol+cell[1]] != 0:
                if cell[0] < 0 and dY < 0:
                    return False
                elif cell[0] > 0 and dY > 0:
                    return False
                if cell[1] < 0 and dX < 0:
                    return False
                elif cell[1] > 0 and dX > 0:
                    return False
            else:
                continue
               
        
    if app.map[gridRow+checkRow+yDir][gridCol+checkCol+xDir] != 0:
        return False
    else:
        return True

# Used for collsion, returns each cell character is within
def getCellsWithin(app,x,y):
    cellsTouching = []
    overLeftEdge = x%app.cellSize < app.playerSize/2
    overRightEdge = x%app.cellSize > app.cellSize-app.playerSize/2
    overTop = y%app.cellSize < app.playerSize/2
    overBottom = y%app.cellSize > app.cellSize-app.playerSize/2
    if overLeftEdge:
        cellsTouching.append((0,-1))
        if overTop:
            cellsTouching.append((-1,-1))
        if overBottom:
            cellsTouching.append((+1,-1))
    elif overRightEdge:
        cellsTouching.append((0,+1))
        if overTop:
            cellsTouching.append((-1,+1))
        if overBottom:
            cellsTouching.append((+1,+1))
    if overTop:
        cellsTouching.append((-1,0))
    if overBottom:
        cellsTouching.append((+1,0))
    return(cellsTouching)

# Keypressed to start new game, shoot, reload, and buy perks/pack a punch
def gameMode_keyPressed(app, event):
    if app.gameOver:
        if event.key == "r":
            newGame(app)
    else:
        if app.debugShortcuts:
            if event.key == "x":
                app.usingPathFinding = not app.usingPathFinding
            if event.key == "p":
                app.score += 20000
        if event.key in app.directionKeys:   app.pressedKeys.add(event.key)
        if event.key == "Space" and app.muzzleFlashing <= 0 and app.clip > 0:
            if app.reloading == 0:
                for zombie in app.zombies:
                    if zombie.isAlive:
                        if zombie.isVisible:
                            if app.pap == False:
                                if not (app.sound.isPlaying() and (app.sound.path == "./audio/newGame.mp3" or app.sound.path == "./audio/newRound.mp3")):
                                    if app.sound.isPlaying(): app.sound.stop()
                                    app.sound = Sound("./audio/shotGun.mp3")
                                    app.sound.start()
                                hitrange = 40/app.width*app.rays
                            else: 
                                hitrange = 60/app.width*app.rays
                                if not (app.sound.isPlaying() and (app.sound.path == "./audio/newGame.mp3" or app.sound.path == "./audio/newRound.mp3")):
                                    if app.sound.isPlaying(): app.sound.stop()
                                    app.sound = Sound("./audio/packapunch.mp3")
                                    app.sound.start()
                            if abs(zombie.getOffsetAngle(app)) < math.radians(hitrange):
                                if zombie.distToPlayer < app.shootingRange:
                                    zombie.health -= app.damage
                                    if zombie.health <= 0:
                                        zombie.isAlive = 0
                                        zombie.resize(app)
                                        app.aliveZombies -=1
                                        app.score = app.score + 200
                app.clip -=1
                app.muzzleFlashing = 1
        
        # Reload
        if event.key == "r":
            if app.clip != app.maxClip and app.tempAmmo != 0 and app.muzzleFlashing == 0:
                app.reloading = 1
        
        # Buy perks
        if event.key == "f":
            if app.canBuyPerk != None:
                if app.canBuyPerk == "Juggernog":
                    price = app.jugPrice
                elif app.canBuyPerk == "Speed Cola":
                    price = app.colaPrice
                elif app.canBuyPerk == "Stamin-Up":
                    price = app.staminupPrice
                elif app.canBuyPerk == "Quick Revive":
                    price = app.quickRevivePrice
                if app.score >= price:
                    app.score -= price
                    if app.canBuyPerk == "Juggernog":
                        ratio = app.maxHealth/app.playerHealth
                        app.maxHealth = 250
                        app.playerHealth = app.maxHealth/ratio
                    elif app.canBuyPerk == "Speed Cola":
                        app.reloadSpeed *= 2
                    elif app.canBuyPerk == "Stamin-Up":
                        app.movementSpeed *= 1.5
                        app.rotationSpeed *= 1.25
                    elif app.canBuyPerk == "Quick Revive":
                        app.playerHealth = app.maxHealth
                    app.perks.append(app.canBuyPerk)

            # Pack a punch
            if app.canPaP:
                if app.score >= app.papPrice:
                    app.shotgunSprite = app.loadImage('./images/papShotgun.png')
                    app.shotgunSprite = app.scaleImage(app.shotgunSprite,2.5)
                    app.reloadSprite = app.loadImage('./images/papReload.png')
                    app.reloadSprite = app.scaleImage(app.reloadSprite,2.5)
                    app.muzzleBlastSprite = app.loadImage('./images/papMuzzleBlast.png')
                    app.muzzleBlastSprite = app.scaleImage(app.muzzleBlastSprite,2.5)
                    app.score -= app.papPrice
                    app.pap = True
                    app.clip = 4
                    app.maxClip = 4
                    app.maxAmmo *= 3
                    app.reloadSpeed *= 1.25
                    app.tempAmmo = app.maxAmmo
 
        
        


# Key released function, works so that player movement is smooth
def gameMode_keyReleased(app,event):
    #print(app.key)
    if event.key in app.pressedKeys: 
        app.pressedKeys.remove(event.key)
        if event.key == "q" or event.key == "e" or event.key == "Left" or event.key == "Right":
            app.rotationSpeed = 0.35

# Makes sure player doesnt change size
def splashScreenMode_sizeChanged(app):
    app.setSize(1000,482)

# Makes sure player doesnt change size
def gameMode_sizeChanged(app):
    app.setSize(1000,482)

    
# Spawns a new zombie far from player
def spawnZombie(app):
    while True:
        side = random.randint(0,3)
        if side < 2: # If spawning at top or bottom
            x = side*(app.cols-1)
            xOffset = 0
            y = random.randint(1,app.rows-2)
            yOffset = app.cellSize*3/4*((-1)**side)
        else: # If spawning at left or right
            x = random.randint(1,app.cols-2)
            xOffset = app.cellSize*3/4*((-1)**side)
            y = (side-2)*(app.rows-1)
            yOffset = 0
        
        xCoord = x*app.cellSize+app.cellSize/2+xOffset
        yCoord = y*app.cellSize+app.cellSize/2+yOffset
        if math.sqrt((xCoord-app.playerX)**2+(yCoord-app.playerY)**2) < app.cellSize*3:
            continue
        else:
            newZombie = Zombie(app,x*app.cellSize+app.cellSize/2,y*app.cellSize+app.cellSize/2)
            app.zombies.append(newZombie)
            break





# Returns list of zombies and rays sorted by distance to render overlap
def createSortedList(app):
    app.zombies.sort(key=lambda x: x.distToPlayer, reverse = True)
    zombieList = app.zombies
    rayList = sorted(app.lines, key= lambda row: row[2], reverse = True)
    zombieCount = 0
    rayCount = 0
    newList = []
    while (zombieCount < len(zombieList)) or (rayCount < len(rayList)):
        if zombieCount == len(zombieList):
            newList.extend(rayList[rayCount:])
            break
        elif rayCount == len(rayList):
            newList.extend(zombieList[zombieCount:])
            break
        if rayList[rayCount][2] > zombieList[zombieCount].distToPlayer:
            newList.append(rayList[rayCount])
            rayCount += 1
        else:
            newList.append(zombieList[zombieCount])
            zombieCount += 1
    return(newList)


# Math inspired from https://www.youtube.com/watch?v=eOCQfxRQ2pY
# Returns [finalX,finalY,finalDist,finalColor,r,h]
# Main raycasting function, finds closest horizontal and vertical line and whichever is closer is used as the wall distance
def raycast(app):
    for r in range(app.rays):
        x, y = app.playerX, app.playerY
        theta = app.playerDir + math.radians(r-app.rays/2)
        if theta > 2*pi:
            theta %= 2*pi
        if theta < 0:
            theta += 2*pi
        if almostEqual(theta, 0) or almostEqual(theta, 2*pi):
            theta = 0
            hdx, hdy = 0, 0
            vdx, vdy = app.cellSize - x%app.cellSize, 0
            hxOffset, hyOffset = 0, 0
            vxOffset, vyOffset = 1, 0
        elif almostEqual(theta, pi/2):
            theta = pi/2
            hdx, hdy = 0, -y%app.cellSize
            vdx, vdy = 0, 0
            hxOffset, hyOffset = 0, -1
            vxOffset, vyOffset = 0, 0

        elif almostEqual(theta, pi):
            theta = pi
            hdx, hdy = 0, 0
            vdx, vdy = -(x%app.cellSize), 0
            hxOffset, hyOffset = 0, 0
            vxOffset, vyOffset = -1, 0

        elif almostEqual(theta, 3*pi/2):
            theta = 3*pi/2
            hdx, hdy = 0, -(app.cellSize-y%app.cellSize)
            vdx, vdy = 0, 0
            hxOffset, hyOffset = 0, 1
            vxOffset, vyOffset = 0, 0
        else:
            ## find first intersect with horizontal line
            if theta < pi: # looking negative y
                hdy = app.cellSize - y%app.cellSize
                hdx = hdy/math.tan(theta)
                hyOffset = -1
                vyOffset = -abs(math.tan(theta))

            else: # looking positive y
                hdy = -(app.cellSize-y%app.cellSize)
                hdx = hdy/math.tan(theta)
                hyOffset = 1
                vyOffset = abs(math.tan(theta))

            ## find first intersect with vertical line
            if theta > 3*pi/2 or theta < pi/2: # looking positive x
                vdx = app.cellSize - x%app.cellSize
                vdy = vdx*math.tan(theta)
                
                hxOffset = abs(1/math.tan(theta))
                vxOffset = 1
            else: # looking negative x
                vdx = -(x%app.cellSize)
                vdy = vdx*math.tan(theta)

                hxOffset = -abs(1/math.tan(theta))
                vxOffset = -1

        app.offsets = [hxOffset,hyOffset,vxOffset,vyOffset]
        hdist = (hdx**2+hdy**2)**(1/2)
        vdist = (vdx**2+vdy**2)**(1/2)
        count = 0
        
        foundH = False
        foundV = False
        if theta != pi and theta != pi*2 and theta != 0:
            while True:
                # Check Horizontal Line
                # Find intersect with horizontal line:
                temphX = x+hdx+(count*hxOffset)
                temphY = y-hdy+(count*hyOffset)
                if theta == 0 or theta == pi or theta == 2*pi:
                    break
                if not (temphX > app.cellSize*app.cols or temphX < 0 or 
                        temphY > app.cellSize*app.rows or temphY < 0):
                    cell = getCellFromPixels(app,temphY+hyOffset,temphX)
                    if cell[0] > app.rows or cell[1]>app.cols:
                        break
                    if app.map[cell[0]][cell[1]] != 0:
                        finalhX, finalhY = temphX, temphY
                        finalhColor = app.map[cell[0]][cell[1]]
                        finalhCount = count
                        foundH = True
                        break
                else:
                    break
                count+=1

        count = 0
        if theta != pi/2 and theta != 3*pi/2:
            while True:                
                # Find intersect with vertical line:
                tempvX = x+vdx+(count*vxOffset)
                tempvY = y-vdy+(count*vyOffset)
                if theta == pi/2 or theta == pi/2:
                    break
                if not (tempvX > app.cellSize*app.cols or tempvX < 0 or 
                        tempvY > app.cellSize*app.rows or tempvY < 0):
                    cell = getCellFromPixels(app,tempvY,tempvX+vxOffset)
                    if cell[0] > app.rows or cell[1]>app.cols:
                        break
                    elif app.map[cell[0]][cell[1]] != 0:
                        finalvX, finalvY = tempvX, tempvY
                        finalvColor = app.map[cell[0]][cell[1]]
                        finalvCount = count
                        foundV = True
                        break
                else:
                    break
                count+=1

        if foundV and foundH:
            hdist = ((x-finalhX)**2+(y-finalhY)**2)**(1/2)
            vdist = ((x-finalvX)**2+(y-finalvY)**2)**(1/2)
            if hdist < vdist:
                foundV = False
            else:
                foundH = False

        if foundV:
            finalX = finalvX
            finalY = finalvY
            finalDist = ((x-finalvX)**2+(y-finalvY)**2)**(1/2)
            finalColor = finalvColor
            if finalColor == 1:
                finalColor = app.wallColor
            


        elif foundH:
            finalX = finalhX
            finalY = finalhY
            finalDist = ((x-finalhX)**2+(y-finalhY)**2)**(1/2)
            finalColor = finalhColor
            if finalColor == 1:
                finalColor = app.darkWallColor
            else:
                finalColor = "dark " + finalColor

        deltaX = abs(finalX-x)
        deltaY = abs(finalY-y)
        h = abs(deltaX*math.cos(app.playerDir)+deltaY*math.sin(app.playerDir))

        ca = app.playerDir - theta
        if ca < 0: ca += 2*pi
        elif ca > 2*pi: ca -= 2*pi
        h=finalDist*math.cos(ca)

        app.lines.append([finalX,finalY,finalDist,finalColor,r,h])

# Used when needing to figure out which cell a point is in
def getCellFromPixels(app,x,y):
    return(int(x//app.cellSize),int(y//app.cellSize))

# Draw map function
def drawMap(app,canvas):
    for row in range(app.rows):
        for col in range(app.cols):
                drawCell(app,canvas,row,col)
    drawPlayer(app,canvas)
    for zombie in app.zombies:
        if zombie.isAlive:
            fillColor = "red"
        else: fillColor= "dark grey"

        # Uncomment to see zombie path
        #if zombie.path != None:
        #    for item in zombie.path:
        #        canvas.create_oval(item[1]*app.cellSize,item[0]*app.cellSize,item[1]*app.cellSize+app.cellSize,item[0]*app.cellSize+app.cellSize,fill='green')
        canvas.create_oval(zombie.x-app.playerSize/2,zombie.y-app.playerSize/2,zombie.x+app.playerSize/2,zombie.y+app.playerSize/2,fill=fillColor)
    canvas.create_line(app.playerX,app.playerY,app.lines[0][0],app.lines[0][1],fill = "black") #Final
    canvas.create_line(app.playerX,app.playerY,app.lines[-1][0],app.lines[-1][1],fill = "black") #Final
    

# Draws cell in map
def drawCell(app,canvas,row,col):
    if app.map[row][col]==1:
        color = app.wallColor
    elif app.map[row][col] != 0:
        color = app.map[row][col]
    else: 
        color = app.floorColor
    x = int(app.cellSize*col)
    y = int(app.cellSize*row)
    canvas.create_rectangle(x,y,x+app.cellSize,y+app.cellSize,
                            fill = color, width = 1)


# Draws floor and sky behind walls
def drawFloorandSky(app,canvas):
    skyColor = app.skyColor
    floorColor = app.floorColor
    canvas.create_rectangle(0,app.height/2+app.playerHeight,app.width,app.height,fill=floorColor,outline=floorColor)
    canvas.create_rectangle(0,0,app.width,app.height/2+app.playerHeight,fill=skyColor,outline=skyColor)

# Draws player circle on map
def drawPlayer(app,canvas):
    canvas.create_oval(app.playerX-app.playerSize/2,app.playerY-app.playerSize/2,app.playerX+app.playerSize/2,app.playerY+app.playerSize/2,fill="blue")

# Draws a single piece of the wall
def drawRay(app,canvas,ray):
    color = ray[3]
    canvas.create_line(app.width-(ray[4]*(app.width)/app.rays), 
                        (app.height/2)-(3000/ray[5])+app.playerHeight,
                        app.width-(ray[4]*(app.width)/app.rays), 
                        app.height/2+(3000/ray[5])+app.playerHeight, 
                        fill=color, 
                        width=(app.width)/app.rays+1)

# Draws rays and zombies in order from furthest to closest
def drawRaysAndZombies(app,canvas):
    for item in app.finalList:
        if type(item) == Zombie:
            drawZombie(app,canvas,item)
        elif type(item) == list:
            drawRay(app,canvas,item)

# Draws zombie sprite
def drawZombie(app,canvas,zombie):
    if zombie.isAlive == 0 and zombie.distToPlayer < 4:
        return
    else:
        offsetAngle = zombie.getOffsetAngle(app)
        if -app.rays/2 < offsetAngle < app.rays/2:
            offsetX = app.width*offsetAngle
            offsetY = 0
            if offsetX > 1:
                sprite = zombie.sprite.transpose(Image.FLIP_LEFT_RIGHT)
            else: sprite = zombie.sprite
            canvas.create_image(app.width/2+offsetX,app.height/2+offsetY+app.playerHeight*2,image=ImageTk.PhotoImage(sprite))

# Draws player health bar
def drawHealthBar(app,canvas):
    canvas.create_rectangle(20,425,170,435,fill = "grey")
    canvas.create_rectangle(20,425,20+150*(app.playerHealth/app.maxHealth),435,fill = "white")

# Draws perk icons
def drawPerks(app,canvas):
    index = 0
    for item in app.perks:
        if item == "Juggernog":
            icon = app.jugIcon
        elif item == "Speed Cola":
            icon = app.colaIcon
        elif item == "Stamin-Up":
            icon = app.staminupIcon
        elif item == "Quick Revive":
            icon = app.quickReviveIcon
        canvas.create_image(215+index*50,430,image=ImageTk.PhotoImage(icon))
        index+=1

# Draws gun
def drawGun(app,canvas):
    if app.pap: muzzleOffset = 10
    else: muzzleOffset = 0
    if app.reloading != 0:
        canvas.create_image(app.width/2,app.height-80,image=ImageTk.PhotoImage(app.reloadSprite))
    else:
        canvas.create_image(app.width/2-5,app.height-72,image=ImageTk.PhotoImage(app.shotgunSprite))
        if app.muzzleFlashing > 0:
            canvas.create_image(app.width/2-muzzleOffset/2,app.height-130-(muzzleOffset)*.4,image=ImageTk.PhotoImage(app.muzzleBlastSprite))
        if app.clip == 0:
            canvas.create_text(app.width/2,app.height/2+80,text = "[r]",fill = "yellow", font = "Helvetica 20")

# Redraw all for the game
def drawHud(app,canvas):
    # Draws crosshairs
    canvas.create_rectangle(app.width/2 -2,app.height/2*1.1-2+app.playerHeight,app.width/2+2,app.height/2*1.1+2+app.playerHeight,fill = "white")
    if app.pap == False:
        canvas.create_oval(app.width/2-20,app.height/2*1.1-20+app.playerHeight,app.width/2+20,app.height/2*1.1+20+app.playerHeight,fill = None, outline = 'white')
    else:
        canvas.create_oval(app.width/2-30,app.height/2*1.1-30+app.playerHeight,app.width/2+30,app.height/2*1.1+30+app.playerHeight,fill = None, outline = 'white')

    # Draws round number
    canvas.create_text(25+1,app.height-25+1,text=f"{app.round}",fill ='gray26', font='Helvetica 30 bold')
    canvas.create_text(25,app.height-25,text=f"{app.round}",fill ='dark red', font='Helvetica 30 bold')

    # Draws ammo count
    canvas.create_text(app.width-50+1,app.height-25+1,text=f"{app.clip}/{app.tempAmmo}", fill = "black", font='Helvetica 30')
    canvas.create_text(app.width-50,app.height-25,text=f"{app.clip}/{app.tempAmmo}", fill = "dark green", font='Helvetica 30')

    # Draws score
    if app.score == 0:
        canvas.create_text(40+2,410+2,text="000", fill = 'orange4', font='Helvetica 25',justify = RIGHT)
        canvas.create_text(40,410,text="000", fill = 'gold', font='Helvetica 25',justify = RIGHT)
    else:
        canvas.create_text(40+(10*(int(math.log(app.score,10))-2))+2,410+2,text=app.score, fill = 'orange4', font='Helvetica 25',justify = RIGHT)
        canvas.create_text(40+(10*(int(math.log(app.score,10))-2)),410,text=app.score, fill = 'gold', font='Helvetica 25',justify = RIGHT)
    
    drawHealthBar(app,canvas)
    drawPerks(app,canvas)

    # Draws border around screen when player hurt
    if app.playerHealth < app.maxHealth:
        borderWidth = 5/((app.playerHealth+1)/100)
        if borderWidth > 10:
            borderWidth = 10
        canvas.create_rectangle(5,5,app.width-5,app.height-5,fill=None,outline='crimson',width=borderWidth)

def drawTextPopup(app,canvas):
    # Draws text when looking at perk
    if app.canBuyPerk != None and app.canBuyPerk not in app.perks:
        if app.canBuyPerk == "Juggernog":
            price = app.jugPrice
            desc = '(Increases Health)'
        elif app.canBuyPerk == "Speed Cola":
            price = app.colaPrice
            desc = '(Increases Reload Speed)'
        elif app.canBuyPerk == "Stamin-Up":
            price = app.staminupPrice
            desc = '(Increases Movement Speed)'
        elif app.canBuyPerk == "Quick Revive":
            price = app.quickRevivePrice
            desc = '(Heals after each round)'
        if price > app.score:
            text = f"{app.canBuyPerk} requires {price} points"
        else: text =f"Would you like to buy {app.canBuyPerk}?\n{desc}\n{price}. Press [f] to Purchase"
        canvas.create_text(app.width/2,app.height/2, text = text, fill = "white",justify=CENTER)

    # Draws text when looking at pack a punch
    if app.canPaP == True:
        price = app.papPrice
        desc = '(Improves Weapon)'
        if price > app.score:
            text = f"Pack-A-Punch requires {price} points"
        else: text =f"Would you like to Pack-A-Punch?\n{desc}\n{price}. Press [f] to Purchase"
        canvas.create_text(app.width/2,app.height/2, text = text, fill = "white",justify=CENTER, font = "bold")

def drawGameOverScreen(app,canvas):
    canvas.create_text(app.width/2, app.height/6+1, text='Game Over',
                       font='Helvetica 90 bold', fill='ivory2')
    canvas.create_text(app.width/2, app.height/6, text='Game Over',
                    font='Helvetica 90 bold', fill='dark red')
    if app.round == 1:
        text = f"You survived 1 round"
    else:
        text = f"You survived {app.round} rounds"
    canvas.create_text(app.width/2, app.height/6+61, text=text,
                    font='Helvetica 35 italic', fill='gold4')
    canvas.create_text(app.width/2, app.height/6+60, text=text,
                    font='Helvetica 35 italic', fill='gold2')
    canvas.create_text(app.width/2,app.height/6+88, text = '[r] to restart', font = 'Helvetica 20', fill = "white")

def gameMode_redrawAll(app,canvas):
    drawFloorandSky(app,canvas)
    drawRaysAndZombies(app,canvas)
    drawGun(app,canvas)
    drawHud(app,canvas)
    drawMap(app,canvas)
    drawTextPopup(app,canvas)
    if app.gameOver:
        drawGameOverScreen(app,canvas)

w = 1000
h = 482
runApp(width=w,height=h)

    
