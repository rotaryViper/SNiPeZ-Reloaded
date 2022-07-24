# Created: 22/6/2022
# Last editted: 24/7/2022
# Developer highscore in endless classic: 14001
'''
Optimisations since v0.1
Corrected enemy commenting.
Removed unncessary function calls in bullet movement.
Removed arguments from class initiation.
Removed initPos from bullet slots
Recursion issue, so I will attempt to fix it
Open a new background daemon thread to play audio
Load all music as Sound because music can't fadeout very well
Open site when area is clicked

##### FIRST GAME BREAKING BUG ####
Velocity may be 0
'''
import pygame,sys,os,random,threading,webbrowser,time

# Gamemode, to fix recurison issue
gameMode = 'mainMenu()'

#START# Constants
# Path to this folder
PATH=os.path.dirname(os.path.realpath(__file__))

# Initialise text module first
pygame.font.init()

# Initiate audio
pygame.mixer.pre_init(44100, 32, 1, 4096)
#44100
# Initialize pygame
pygame.init()

# Constants
FPS = 60
CLOCK = pygame.time.Clock()

# Create screen
SCREEN = pygame.display.set_mode(flags=pygame.FULLSCREEN,vsync=0)

# Screen dimensions
SCREENW, SCREENH = SCREEN.get_width(), SCREEN.get_height()

# Default fonts are bound to the height of the screen
# If the screen is 1080p in height, the font size will be 30
FONTSIZE = SCREENH//36
COMICSANS = pygame.font.SysFont('COMICSANSms', FONTSIZE)
TITLEFONT = pygame.font.SysFont('COMICSANSms', SCREENH//4)

# Preload images
bulletImg = pygame.Surface.convert_alpha(pygame.image.load(f'{PATH}\\Img\\Bullet.png'))
enemyImg = pygame.Surface.convert(pygame.image.load(f'{PATH}\\Img\\EnemyStandard.png'))
introImg = pygame.Surface.convert(pygame.image.load(f'{PATH}\\Img\\Intro.png'))
logoImg = pygame.Surface.convert(pygame.image.load(f'{PATH}\\Img\\Logo.png'))
playerImg = pygame.Surface.convert_alpha(pygame.image.load(f'{PATH}\\Img\\Player.png'))

# Game title and icon
pygame.display.set_caption('SNiPeZ')
pygame.display.set_icon(logoImg)
#END# Constants

#START# Audio
# Load hit noise
HITNOISE = pygame.mixer.Sound(PATH+'\\Noise\\HitNoise.wav')
# Initial hit noise volume
INITHITNOISEVOL = 0.97
HITNOISE.set_volume(INITHITNOISEVOL)
# Initial music volume
INITMUSICVOL = 0.6
# Running game music
def gameMusic(vol):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(vol)
    # Get directory of all music
    songs = os.listdir(PATH+f"\\Music (Ogg)")
    # Shuffle order of songs
    random.shuffle(songs)
    # Song counter
    songCount = 0
    # Song length
    songLen = 0
    while True:
        # If no music is playing, then play music
        if pygame.mixer.music.get_busy() == False:

            # Load song
            songDir = PATH+f'\\Music (Ogg)\\{songs[songCount]}'
            pygame.mixer.music.load(songDir)

            # Play song, and fade in for 3 seconds
            pygame.mixer.music.play(fade_ms=3000)

            # Find length of song, by converting it into a Sound object
            songSound = pygame.mixer.Sound(songDir)
            songLen = songSound.get_length()

            # Move song counter
            songCount += 1
            songCount = songCount % len(songs)

        # If song is about to end, fade the song out. get_pos() is in milliseconds so must be converted to seconds
        if songLen - (pygame.mixer.music.get_pos()/1000) <= 3:
            # Fade out song for 3 seconds
            pygame.mixer.music.fadeout(3000)

        # Sleep to not drain extra cpu resources
        time.sleep(1)

# Run game audio in the background
# Comma is very important in arguments
audioThread = threading.Thread(target=gameMusic, args=(INITMUSICVOL,),daemon = True, name='Music')
audioThread.start()
#END# Audio

##Start## Classes
class Bullet(pygame.sprite.Sprite):
    __slots__ = '_Sprite__g', 'img', 'rect', 'vector'

    def __init__(self, img, initPos, vel, mousePos):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)
        
        self.img = img
        self.rect = img.get_rect()
        self.rect.move_ip(initPos)
        self.vector = pygame.math.Vector2(mousePos[0]-self.rect.centerx,mousePos[1]-self.rect.centery)
        self.vector.scale_to_length(vel)

    def update(self, enemyGroup):
        # Move bullet
        self.rect = self.rect.move(self.vector)
        
        # Render bullet
        SCREEN.blit(self.img, self.rect)

        # If bullet collides with enemy, destroy enemy and give player a point
        if pygame.sprite.spritecollide(self, enemyGroup, True):
            points = 60
            enemyKillCounter = 1

        else:
            points = 0
            enemyKillCounter = 0

        # If bullet goes out of game border, destroy bullet
        if self.rect.right < 0 or self.rect.bottom < 0 or self.rect.top > SCREENH or self.rect.left > SCREENW:
            self.kill()

        return points, enemyKillCounter

class EnemyStandard(pygame.sprite.Sprite):
    __slots__ = '_Sprite__g', 'img', 'rect', 'vel'

    def __init__(self, img):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)

        self.img = img
        self.rect = img.get_rect()
        self.rect.move_ip(self.initPos())
    
    def update(self, player):
        # Using a trusty try/except statement to ignore errors
        try:
            ## Movement
            # Give enemy it's correct vector in relation to the player mouse
            bulletMove=pygame.math.Vector2(int(player.rect.x-self.rect.x),int(player.rect.y-self.rect.y))

            # Limit enemy speed to vel
            bulletMove.scale_to_length(self.vel)

            # Move enemy
            self.rect = self.rect.move(bulletMove)

            # Render enemy
            SCREEN.blit(self.img, self.rect)

        except:
            pass

    def initPos(self):
        # Pick which wall to use
        wallFactor = random.random()

        # Top wall
        if wallFactor > 0.75:
            return(random.randint(-self.rect.width,SCREENW),-self.rect.height)
        # Left wall
        elif wallFactor > 0.5:
            return(-self.rect.width,random.randint(-self.rect.height,SCREENH))
        # Bottom wall
        elif wallFactor > 0.25:
            return(random.randint(-self.rect.width,SCREENW),SCREENH)
        # Right wall
        else:
            return(SCREENW,random.randint(-self.rect.height,SCREENH))

class Player(pygame.sprite.Sprite):
    __slots__ = '_Sprite__g', 'img', 'rect', 'vel', 'health'

    def __init__(self, img, vel, health):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)
        self.img = img
        self.rect = img.get_rect()
        self.rect.move_ip((SCREENW/2)-(self.rect.width/2),(SCREENH/2)-(self.rect.height/2))
        self.vel = vel
        self.health = health

    def update(self, key, enemyGroup):
        ## Movement
        up = key[pygame.K_w] or key[pygame.K_UP]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]

        playerMove = pygame.math.Vector2(0,0)
        # Move player in that vector if it is within the game borders
        if up == True and self.rect.top > 0:
            playerMove[1] += -self.vel
        if left == True and self.rect.left > 0:
            playerMove[0] += -self.vel
        if down == True and self.rect.bottom < SCREENH:
            playerMove[1] += self.vel
        if right == True and self.rect.right < SCREENW:
            playerMove[0] += self.vel

        # Limit bullet speed to bullet.vel
        try:playerMove.scale_to_length(self.vel)
        except:pass

        # Move player
        self.rect = self.rect.move(playerMove)

        # Render player
        SCREEN.blit(self.img, self.rect)

        ## Losing health
        # If player contacts enemy, enemies dies and player loses 1 heart
        if pygame.sprite.spritecollide(self, enemyGroup, True):
            self.health -= 1

class SettingSlider(pygame.sprite.Sprite):
    __slots__ = '_Sprite__g', 'bigRect', 'smallRect', 'initPos', 'value'
    # bigRect will follow:
    # initPos[0], initPos[1], FONTSIZE*10, FONTSIZE
    # smallRect will follow:
    # initPos[0]+(FONTSIZE//2), (initPos[1]//2)-(FONTSIZE//8), (FONTSIZE*10)-(FONTSIZE), FONTSIZE//4

    def __init__(self, initPos, value):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)

        self.initPos = initPos

        self.bigRect = pygame.Rect(initPos[0], initPos[1], FONTSIZE*10, FONTSIZE)
        self.smallRect = pygame.Rect(initPos[0]+(value*self.bigRect.width), initPos[1], FONTSIZE//2, FONTSIZE)

        # The important part of a slider, getting its value. This is a float between 0-1.0
        self.value = value

    def update(self, mousePos, mouseClick):
        # If mouse is hovering over big rect, and mouse is clicked, move slider
        if pygame.Rect.collidepoint(self.bigRect, mousePos[0], mousePos[1]) and any(mouseClick) == True:
            self.smallRect.centerx = mousePos[0]

        # Calculate value
        self.value = 1-((self.bigRect.right-self.smallRect.centerx)/self.bigRect.width)

        # Draw sliders
        pygame.draw.rect(SCREEN, 'gray', self.bigRect, border_radius=FONTSIZE//3)
        pygame.draw.rect(SCREEN, 'white', self.smallRect, border_radius=FONTSIZE//3)

        # Value as text
        SCREEN.blit(
        COMICSANS.render(f'{round(self.value,2)}', True, 'white'),
        (self.bigRect.right+FONTSIZE,self.bigRect.y-(FONTSIZE/4))
        )

        # Return value
        return self.value
##End## Classes

##Start## Utility Functions
# I guess this solution works? This fixes problem where players may open links without realising. Now they know :)
def openLink(link):
    pygame.display.set_mode(flags=pygame.HIDDEN,vsync=0)
    webbrowser.open_new(link)
    pygame.display.set_mode(flags=pygame.SHOWN,vsync=0)

# Applies to all game modes
def initFrame():
    events = [event.type for event in pygame.event.get()]
    key = pygame.key.get_pressed()
    mouseClick = pygame.mouse.get_pressed()
    mousePos = pygame.mouse.get_pos()
    # Global exit function
    if key[pygame.K_0] == True: sys.exit()

    return events, key, mouseClick, mousePos
##END## Utility Functions

# Introduction
def intro():
    SCREEN.fill('black')
    introMove=[41,41]
    introRect=introImg.get_rect()
    introRect.move_ip(0,0)
    while True:
        # Initiate frame
        events, key, mouseClick, mousePos = initFrame()
        # If any mouse button is clicked, exit intro
        if (any(mouseClick) or any(key)) == True:
            break

        if introRect.left<0 or introRect.right>SCREENW:
            introMove[0]=-introMove[0]

        if introRect.top<0 or introRect.bottom>SCREENH:
            introMove[1]=-introMove[1]

        if introRect.right>=SCREENW and introRect.bottom>=SCREENH:
            pass
        else:
            introRect=introRect.move(introMove[0],introMove[1])
            SCREEN.blit(introImg,introRect)

        # Title #
        font=pygame.font.SysFont('Noto Sans',200) # Font, size
        text=font.render('SNiPeZ',True,'black') # Text, antialiasing, colour
        SCREEN.blit(text,(SCREENW/4,SCREENH/4)) # Location

        # Subtitle #
        font=pygame.font.SysFont('Noto Sans',50) # Font, size
        text=font.render('The action shooter',True,'black') # Text, antialiasing, colour
        SCREEN.blit(text,(SCREENW/4,3*(SCREENH/4))) # Location

        # Click any button to continue #
        font=pygame.font.SysFont('Noto Sans',50) # Font, size
        text=font.render('Click to continue',True,'black') # Text, antialiasing, colour
        SCREEN.blit(text,(2*SCREENW/4,5*(SCREENH/6))) # Location

        pygame.display.flip()
        CLOCK.tick(FPS*4)

## Attempt to refactor all gameMode functions
# Credits
def credits():
    # Title
    SCREEN.blit(TITLEFONT.render(f'Credits', True, 'white'),
        (SCREENW/4,0)
    )
    # Blit logo
    logoRect = logoImg.get_rect()
    SCREEN.blit(logoImg, logoRect)
    # Blit exit condition
    txt = COMICSANS.render(f'Press [esc] to return to main menu', True, 'white')
    SCREEN.blit(
        txt,
        ((SCREENW/2)-(txt.get_width()/2),7*(SCREENH/8))
    )

    # Print beta tester
    SCREEN.blit(
        COMICSANS.render(f'Beta tester: twitch.tv/suavereeee', True, 'white'),
        ((SCREENW/2)-(txt.get_width()/2),5*(SCREENH/8))
    )
    # Print music tester
    SCREEN.blit(
        COMICSANS.render(f'Music artist: Lukas', True, 'white'),
        ((SCREENW/2)-(txt.get_width()/2),4*(SCREENH/8))
    )
    # Print creator
    SCREEN.blit(
        COMICSANS.render(f'Made by: github.com/rotaryviper', True, 'white'),
        ((SCREENW/2)-(txt.get_width()/2),3*(SCREENH/8))
    )

    # Main loop
    while True:
        # Initiate frame
        events, key, mouseClick, mousePos = initFrame()
        # Exit how to play
        if key[pygame.K_ESCAPE]:
            return 'mainMenu()'

        # If game logo is clicked, open the github
        if pygame.Rect.collidepoint(logoRect, mousePos[0], mousePos[1]) == True and any(mouseClick) == True:
            openLink('https://github.com/rotaryViper/SNiPeZ-Reloaded')
            return 'credits()'

        # My github
        if (mousePos[1] > 3*(SCREENH/8)  and mousePos[1] < (3*(SCREENH/8)+FONTSIZE) and any(mouseClick)) == True:
            openLink('https://www.github.com/rotaryViper')
            return 'credits()'

        # Beta tester
        if (mousePos[1] > 5*(SCREENH/8)  and mousePos[1] < (5*(SCREENH/8)+FONTSIZE) and any(mouseClick)) == True:
            openLink('https://www.twitch.tv/suavereeee')
            return 'credits()'

        pygame.display.flip()
        # Run at set FPS
        CLOCK.tick(FPS//4)

# Settings
def settings():
    # Create new subsurface
    subScreen = pygame.Surface((SCREENW,SCREENH))
    # Blit logo
    logoRect = logoImg.get_rect()
    subScreen.blit(logoImg, logoRect)
    # Title
    subScreen.blit(TITLEFONT.render(f'Settings', True, 'white'),
        (SCREENW/4,0)
    )
    #Start# Options
    # Music volume
    subScreen.blit(
        COMICSANS.render(f'Music Volume', True, 'white'),
        ((SCREENW/4),3*(SCREENH/8))
    )
    # Fire noise volume
    subScreen.blit(
        COMICSANS.render(f'Fire Noise Volume', True, 'white'),
        ((SCREENW/4),4*(SCREENH/8))
    )
    # Endless hard mode
    SCREEN.blit(
        COMICSANS.render(f'[3] Enter Endless Hard Mode', True, 'white'),
        ((SCREENW/4),5*(SCREENH/8))
    )
    # Endless gamer mode
    SCREEN.blit(
        COMICSANS.render(f'[4] Enter Endless Gamer Mode', True, 'white'),
        ((SCREENW/4),6*(SCREENH/8))
    )
    # Exit settings
    subScreen.blit(
        COMICSANS.render(f'[esc] Exit Settings', True, 'white'), 
        ((SCREENW/4),7*(SCREENH/8))
    )

    # Set music value to 0.7 otherwise its too loud
    musicSlider = SettingSlider(((SCREENW/4),3*(SCREENH/8)+(1.5*FONTSIZE)), INITMUSICVOL)
    # Set hit noise value to 0.9 as default
    hitNoiseSlider = SettingSlider(((SCREENW/4),4*(SCREENH/8)+(1.5*FONTSIZE)), INITHITNOISEVOL)
    #End# Options

    # Main loop
    while True:
        # Initiate frame
        events, key, mouseClick, mousePos = initFrame()
        # Exit how to play
        if key[pygame.K_ESCAPE]:
            return 'mainMenu()'

        # Render everything static
        SCREEN.blit(subScreen,(0,0))

        # Set volume as the slider value
        pygame.mixer.music.set_volume(musicSlider.update(mousePos, mouseClick))
        # Set volume as the slider value
        HITNOISE.set_volume(hitNoiseSlider.update(mousePos, mouseClick))

        # If game logo is clicked, open the github
        if pygame.Rect.collidepoint(logoRect, mousePos[0], mousePos[1]) == True and any(mouseClick) == True:
            openLink('https://github.com/rotaryViper/SNiPeZ-Reloaded')
            return 'mainMenu()'

        pygame.display.flip()
        # Run at set FPS
        CLOCK.tick(FPS//4)

# Main menu
def mainMenu():
    # Blit logo
    logoRect = logoImg.get_rect()
    SCREEN.blit(logoImg, logoRect)
    # Title
    SCREEN.blit(TITLEFONT.render(f'SNiPeZ', True, 'white'),
        (SCREENW/4,0)
    )

    #Start# Options
    # How to play
    SCREEN.blit(
        COMICSANS.render(f'[1] How To Play', True, 'white'),
        ((SCREENW/4),3*(SCREENH/8))
    )
    # Endless classic mode
    SCREEN.blit(
        COMICSANS.render(f'[2] Enter Endless Classic Mode', True, 'white'),
        ((SCREENW/4),4*(SCREENH/8))
    )
    # Endless hard mode
    SCREEN.blit(
        COMICSANS.render(f'[3] Enter Endless Hard Mode', True, 'white'),
        ((SCREENW/4),5*(SCREENH/8))
    )
    # Endless gamer mode
    SCREEN.blit(
        COMICSANS.render(f'[4] Enter Endless Gamer Mode', True, 'white'),
        ((SCREENW/4),6*(SCREENH/8))
    )
    # Exit
    SCREEN.blit(
        COMICSANS.render(f'[0] Exit Game', True, 'white'), 
        ((SCREENW/4),7*(SCREENH/8))
    )
    # Settings
    SCREEN.blit(
        COMICSANS.render(f'[a] Settings', True, 'white'), 
        (2*(SCREENW/4),3*(SCREENH/8))
    )
    # Credits
    SCREEN.blit(
        COMICSANS.render(f'[c] Credits', True, 'white'), 
        (2*(SCREENW/4),4*(SCREENH/8))
    )
    #End# Options

    # Main loop
    while True:
        # Initiate frame
        events, key, mouseClick, mousePos = initFrame()

        if key[pygame.K_1] or key[pygame.K_KP1]:
            return 'howToPlay()'
        if key[pygame.K_2] or key[pygame.K_KP2]:
            return 'endless(2)'
        if key[pygame.K_3] or key[pygame.K_KP3]:
            return 'endless(3)'
        if key[pygame.K_4] or key[pygame.K_KP4]: 
            return 'endless(4)'
        if key[pygame.K_a]:
            return 'settings()'
        if key[pygame.K_c]:
            return 'credits()'

        # If game logo is clicked, open the github
        if pygame.Rect.collidepoint(logoRect, mousePos[0], mousePos[1]) == True and any(mouseClick) == True:
            openLink('https://github.com/rotaryViper/SNiPeZ-Reloaded')
            return 'mainMenu()'

        pygame.display.flip()
        # Run at set FPS
        CLOCK.tick(FPS//4)

# How to play
def howToPlay():
    # Blit exit condition
    txt = COMICSANS.render(f'Press [esc] to return to main menu', True, 'white')
    SCREEN.blit(
        txt,
        ((SCREENW/2)-(txt.get_width()/2),7*(SCREENH/8))
    )

    # Blit player
    playerRect = playerImg.get_rect()
    playerRect.centerx = SCREENW/2
    playerRect.centery = SCREENH/2
    SCREEN.blit(playerImg,playerRect)

    # Blit enemy
    enemyRect = enemyImg.get_rect()
    enemyRect.centerx = SCREENW-enemyRect.width
    enemyRect.centery = SCREENH/2
    SCREEN.blit(enemyImg,enemyRect)

    # Blit bullet
    bulletRect = bulletImg.get_rect()
    bulletRect.centerx = SCREENW/2+12*bulletRect.width
    bulletRect.centery = SCREENH/2
    SCREEN.blit(bulletImg,bulletRect)

    # Blit controls
    SCREEN.blit(
        COMICSANS.render('Controls', True, 'white'), 
        (1.5*(SCREENW/20),7*(SCREENH/10))
    )

    SCREEN.blit(
        COMICSANS.render('W', True, 'white'), 
        (2*(SCREENW/20),8*(SCREENH/10))
    )
    SCREEN.blit(
        COMICSANS.render('A', True, 'white'), 
        (SCREENW/20,9*(SCREENH/10))
    )
    SCREEN.blit(
        COMICSANS.render('S', True, 'white'), 
        (2*(SCREENW/20),9*(SCREENH/10))
    )
    SCREEN.blit(
        COMICSANS.render('D', True, 'white'), 
        (3*(SCREENW/20),9*(SCREENH/10))
    )

    # Blit goal
    SCREEN.blit(
        COMICSANS.render('Goal:', True, 'white'), 
        (FONTSIZE,FONTSIZE)
    )
    SCREEN.blit(
        COMICSANS.render('1. Get the highest points possible.', True, 'white'), 
        (FONTSIZE,2*FONTSIZE)
    )
    SCREEN.blit(
        COMICSANS.render('2. Click to fire bullets. If bullet connects with enemy, enemy dies and you score points.', True, 'white'), 
        (FONTSIZE,3*FONTSIZE)
    )
    SCREEN.blit(
        COMICSANS.render('3. The longer you live, the more points you gain.', True, 'white'), 
        (FONTSIZE,4*FONTSIZE)
    )
    SCREEN.blit(
        COMICSANS.render('4. Bullets cost points, so fire them conservatively.', True, 'white'), 
        (FONTSIZE,5*FONTSIZE)
    )
    SCREEN.blit(
        COMICSANS.render('5. Do not let enemy touch you, or you lose health.', True, 'white'), 
        (FONTSIZE,6*FONTSIZE)
    )

    # Main loop
    while True:
        # Initiate frame
        events, key, mouseClick, mousePos = initFrame()
        # Exit how to play
        if key[pygame.K_ESCAPE]:
            return 'mainMenu()'

        pygame.display.flip()
        # Run at set FPS
        CLOCK.tick(FPS//4)


# Endless Mode
def endless(spawnRate):
    #Start# Game values
    # Initiate entity lists
    bulletGroup = pygame.sprite.Group()
    # If anyone reaches 10000, they are cheating; png is 80 pixels tall and wide
    dormantEnemyGroup = (EnemyStandard(enemyImg) for i in range(10000))
    activeEnemyGroup = pygame.sprite.Group()

    # Enemy and player spawning
    enemySpawnCounter = 0
    # Initiate player
    player = Player(playerImg, 10, 5)

    # Game counter
    startTime = time.time()

    # Player points
    points = 0
    enemyKillCounter = 0
    bulletsFired = 0

    # Pause boolean
    paused = False

    #End# Game values
    while True:
        # Initiate frame
        events, key, mouseClick, mousePos = initFrame()
        # Game duration
        currentTime = round(time.time()-startTime,2)
        # Enemy speed modifer
        enemySpdMod = currentTime/10
        # Is gun fired
        fired = False
        #End# Things that are checked in every frame

        # Enter paused state if esc is clicked
        if key[pygame.K_ESCAPE]: paused = True

        # Restart game
        if key[pygame.K_r]:
            player.health = 0

        # Secret win
        if enemySpawnCounter == 10000:
            # Print lose message
            font=pygame.font.SysFont('Noto Sans',FONTSIZE*7) # Font, size
            text=font.render('Secret Win!',True,'white') # Text, antialiasing, colour
            SCREEN.blit(text,((SCREENW/2)-(text.get_width()/2),0)) # Location
            
            player.health = 0

        #enemySpawnCounter = 9999 # Debugging

        # If player is still alive, and game is unpaused
        if player.health > 0 and paused == False:

            # Clean screen with black
            SCREEN.fill(('black'))
            # Bullets
            # Check if gun was fired  (spacebar or mouse clicked)
            if pygame.MOUSEBUTTONDOWN in events or key[pygame.K_SPACE]:
                fired = True
                bulletGroup.add(Bullet(bulletImg, (player.rect.centerx,player.rect.centery), 16, mousePos))

            # Update bullets
            for bullet in bulletGroup.sprites():
                addPoints, addEnemyKillCounter = bullet.update(activeEnemyGroup)
                points += addPoints
                enemyKillCounter += addEnemyKillCounter

            # Enemies
            if enemySpawnCounter % 60 == 0:
                [activeEnemyGroup.add(next(dormantEnemyGroup)) for i in range(spawnRate)]
            enemySpawnCounter += 1

            # Update enemies
            #activeEnemyGroup.update(player)
            for enemy in activeEnemyGroup.sprites():
                enemy.vel = 4 + enemySpdMod
                enemy.update(player)

            # Update player movement
            player.update(key, activeEnemyGroup)

            # Points scoring system
            # Add 60 point per second
            points += 1
            # Lose 30 points for every bullet fired
            if fired == True:
                points -= 30
                bulletsFired += 1
                HITNOISE.play()

            # Print mouse cursor location
            SCREEN.blit(
                COMICSANS.render(str(mousePos), True, ('white')),
                (0,0)
            )

            # Print FPS
            SCREEN.blit(
                COMICSANS.render(f'FPS: {round(CLOCK.get_fps())}', True, 'white'),
                (SCREENW-(7*FONTSIZE),0)
            )
            # Print time
            SCREEN.blit(
                COMICSANS.render(f'Time: {currentTime}', True, 'white'),
                (SCREENW-(7*FONTSIZE),2*FONTSIZE)
            )
            # Print points
            SCREEN.blit(
                COMICSANS.render(f'Points: {points}', True, 'white'),
                (FONTSIZE,SCREENH-(3*FONTSIZE))
            )
            # Print health
            SCREEN.blit(
                COMICSANS.render(f'Health: {player.health}', True, 'pink'),
                (FONTSIZE,SCREENH-(2*FONTSIZE))
            )

        # If your health becomes 0
        if player.health <= 0:
            # Print lose message
            txt = COMICSANS.render('You died. Click r to play again. Click esc to exit.', True, 'purple')
            SCREEN.blit(txt, ((SCREENW/2)-(txt.get_width()/2),(SCREENH/2)-txt.get_height()))

            # Print extra stats; enemies kill; bullets fired
            # Enemies killed
            SCREEN.blit(
                COMICSANS.render(f'Enemies killed: {enemyKillCounter}', True, 'white'),
                (FONTSIZE,SCREENH-(5*FONTSIZE))
            )
            # Bullets fired
            SCREEN.blit(
                COMICSANS.render(f'Bullets fired: {bulletsFired}', True, 'white'),
                (FONTSIZE,SCREENH-(4*FONTSIZE))
            )

            if key[pygame.K_r]:
                return f'endless({spawnRate})'

        if paused == True:
            # Print how to exit
            SCREEN.blit(
                COMICSANS.render(f'[e] Exit to main menu', True, 'white'),
                ((SCREENW/4),3*(SCREENH/8))
            )
            # Print how to restart
            SCREEN.blit(
                COMICSANS.render(f'[r] Restart game', True, 'white'),
                ((SCREENW/4),4*(SCREENH/8))
            )
            # Print how to resume
            SCREEN.blit(
                COMICSANS.render(f'[x] Resume game', True, 'white'),
                ((SCREENW/4),5*(SCREENH/8))
            )

            if key[pygame.K_e]:
                return 'mainMenu()'
            if key[pygame.K_x]:
                paused = False

        pygame.display.flip()
        # Run at set FPS
        CLOCK.tick(FPS)

# Exitting functions with return is the correct method of terminating functions, so they don't spit errors back at me
intro()

# This solves the recursion issue in python
while True:
    # Clean screen
    SCREEN.fill('black')
    # This is bad code but at least it ends the 
    gameMode = eval(gameMode)