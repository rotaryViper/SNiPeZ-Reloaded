# Created: 22/6/2022
# Last editted: 22/6/2022
# Developer highscore in endless classic: 10355
'''
Optimisations since v0.1
Corrected enemy commenting.
Removed unncessary function calls in bullet movement.
Removed arguments from class initiation.
'''
import pygame,sys,os,random,time

# Path to this folder
path=os.path.dirname(os.path.realpath(__file__))

# Initialise text module first
pygame.font.init()

# Initiate audio
pygame.mixer.pre_init(44100, 16, 2, 4096)

# Initialize pygame
pygame.init()

# Constants
FPS = 60
clock = pygame.time.Clock()

# Comment out events that are required
# Blocks unnecesary events to improve performance
pygame.event.set_blocked([
    #pygame.QUIT,
    pygame.ACTIVEEVENT,
    pygame.KEYDOWN,
    pygame.KEYUP,
    pygame.MOUSEMOTION,
    #pygame.MOUSEBUTTONDOWN,
    pygame.MOUSEBUTTONUP,
    pygame.JOYAXISMOTION,
    pygame.JOYBALLMOTION,
    pygame.JOYHATMOTION,
    pygame.JOYBUTTONDOWN,
    pygame.JOYBUTTONUP,
    pygame.VIDEORESIZE,
    pygame.VIDEOEXPOSE,
    pygame.USEREVENT
])

# Create screen
screen = pygame.display.set_mode(flags=pygame.FULLSCREEN,vsync=0)

# Screen dimensions
screenW, screenH = screen.get_width(), screen.get_height()

# Default fonts are bound to the height of the screen
# If the screen is 1080p in height, the font size will be 30
fontSize = screenH//36
comicSans = pygame.font.SysFont('comicsansms', fontSize)

# Preload images
bulletImg = pygame.Surface.convert_alpha(pygame.image.load(f'{path}/Bullet.png'))
enemyImg = pygame.Surface.convert(pygame.image.load(f'{path}/EnemyStandard.png'))
introImg = pygame.Surface.convert(pygame.image.load(f'{path}/Intro.png'))
logoImg = pygame.Surface.convert(pygame.image.load(f'{path}/Logo.png'))
playerImg = pygame.Surface.convert_alpha(pygame.image.load(f'{path}/Player.png'))

# Game title and icon
pygame.display.set_caption('SNiPeZ')
pygame.display.set_icon(logoImg)

##Start## Classes
class Bullet(pygame.sprite.Sprite):
    __slots__ = 'img', 'rect', 'initPos', 'direction'

    def __init__(self, img, initPos, vel, mousePos):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)
        
        self.img = img
        self.rect = img.get_rect()
        self.rect.move_ip(initPos)
        self.direction = pygame.math.Vector2(mousePos[0]-self.rect.centerx,mousePos[1]-self.rect.centery)
        self.direction.scale_to_length(vel)

    def update(self, enemyGroup):
        # Move bullet
        self.rect = self.rect.move(self.direction)
        
        # Render bullet
        screen.blit(self.img, self.rect)

        # If bullet collides with enemy, destroy enemy and give player a point
        if pygame.sprite.spritecollide(self, enemyGroup, True):
            points = 60
            enemyKillCounter = 1

        else:
            points = 0
            enemyKillCounter = 0

        # If bullet goes out of game border, destroy bullet
        if self.rect.right < 0 or self.rect.bottom < 0 or self.rect.top > screenH or self.rect.left > screenW:
            self.kill()

        return points, enemyKillCounter

class EnemyStandard(pygame.sprite.Sprite):
    __slots__ = 'img', 'rect', 'vel'

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
            # Give enemy it's correct direction in relation to the player mouse
            bulletMove=pygame.math.Vector2(int(player.rect.x-self.rect.x),int(player.rect.y-self.rect.y))

            # Limit enemy speed to vel
            bulletMove.scale_to_length(self.vel)

            # Move enemy
            self.rect = self.rect.move(bulletMove)

            # Render enemy
            screen.blit(self.img, self.rect)

        except:
            pass

    def initPos(self):
        # Pick which wall to use
        wallFactor = random.random()

        # Top wall
        if wallFactor > 0.75:
            return(random.randint(-self.rect.width,screenW),-self.rect.height)
        # Left wall
        elif wallFactor > 0.5:
            return(-self.rect.width,random.randint(-self.rect.height,screenH))
        # Bottom wall
        elif wallFactor > 0.25:
            return(random.randint(-self.rect.width,screenW),screenH)
        # Right wall
        else:
            return(screenW,random.randint(-self.rect.height,screenH))

class Player(pygame.sprite.Sprite):
    __slots__ = 'img', 'rect', 'vel', 'health'

    def __init__(self, img, vel, health):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)
        self.img = img
        self.rect = img.get_rect()
        self.rect.move_ip((screenW/2)-(self.rect.width/2),(screenH/2)-(self.rect.height/2))
        self.vel = vel
        self.health = health

    def update(self, key, enemyGroup):
        ## Movement
        up = key[pygame.K_w] or key[pygame.K_UP]
        left = key[pygame.K_a] or key[pygame.K_LEFT]
        down = key[pygame.K_s] or key[pygame.K_DOWN]
        right = key[pygame.K_d] or key[pygame.K_RIGHT]

        playerMove = pygame.math.Vector2(0,0)
        # Move player in that direction if it is within the game borders
        if up == True and self.rect.top > 0:
            playerMove[1] += -self.vel
        if left == True and self.rect.left > 0:
            playerMove[0] += -self.vel
        if down == True and self.rect.bottom < screenH:
            playerMove[1] += self.vel
        if right == True and self.rect.right < screenW:
            playerMove[0] += self.vel

        # Limit bullet speed to bullet.vel
        try:playerMove.scale_to_length(self.vel)
        except:pass

        # Move player
        self.rect = self.rect.move(playerMove)

        # Render player
        screen.blit(self.img, self.rect)

        ## Losing health
        # If player contacts enemy, enemies dies and player loses 1 heart
        if pygame.sprite.spritecollide(self, enemyGroup, True):
            self.health -= 1
##End## Classes

##Start## Utility Functions
# Move between stages better
def startNew(foo):
    return foo

# Introduction
def intro():
    screen.fill('black')
    introMove=[41,41]
    introRect=introImg.get_rect()
    introRect.move_ip(0,0)
    while True:
        if pygame.MOUSEBUTTONDOWN in [event.type for event in pygame.event.get()]:
            return startNew(mainMenu())

        if introRect.left<0 or introRect.right>screenW:
            introMove[0]=-introMove[0]

        if introRect.top<0 or introRect.bottom>screenH:
            introMove[1]=-introMove[1]

        if introRect.right>=screenW and introRect.bottom>=screenH:
            pass
        else:
            introRect=introRect.move(introMove[0],introMove[1])
            screen.blit(introImg,introRect)

        # Title #
        font=pygame.font.SysFont('Noto Sans',200) # Font, size
        text=font.render('SNiPeZ',True,'black') # Text, antialiasing, colour
        screen.blit(text,(screenW/4,screenH/4)) # Location

        # Subtitle #
        font=pygame.font.SysFont('Noto Sans',50) # Font, size
        text=font.render('The action shooter',True,'black') # Text, antialiasing, colour
        screen.blit(text,(screenW/4,3*(screenH/4))) # Location

        # Click any button to continue #
        font=pygame.font.SysFont('Noto Sans',50) # Font, size
        text=font.render('Click to continue',True,'black') # Text, antialiasing, colour
        screen.blit(text,(2*screenW/4,5*(screenH/6))) # Location

        pygame.display.flip()
        clock.tick(FPS*4)

# Main menu
def mainMenu():
    # Clean screen
    screen.fill('black')
    # Blit logo
    screen.blit(logoImg, logoImg.get_rect())
    # Title
    titleFont = pygame.font.SysFont('comicsansms', screenH//4)
    screen.blit(titleFont.render(f'SNiPeZ', True, 'white'),
        (screenW/4,0)
    )

    #Start# Options
    # How to play
    screen.blit(
        comicSans.render(f'[1] How To Play', True, 'white'),
        ((screenW/4),3*(screenH/8))
    )
    # Endless classic mode
    screen.blit(
        comicSans.render(f'[2] Enter Endless Classic Mode', True, 'white'),
        ((screenW/4),4*(screenH/8))
    )
    # Endless hard mode
    screen.blit(
        comicSans.render(f'[3] Enter Endless Hard Mode', True, 'white'),
        ((screenW/4),5*(screenH/8))
    )
    # Endless gamer mode
    screen.blit(
        comicSans.render(f'[4] Enter Endless Gamer Mode', True, 'white'),
        ((screenW/4),6*(screenH/8))
    )
    # Exit
    screen.blit(
        comicSans.render(f'[0] Exit Game', True, 'white'), 
        ((screenW/4),7*(screenH/8))
    )
    #End# Options

    # Main loop
    while True:
        # Game breaks when this line is not included for some reason
        pygame.event.get()
        # Get keys pressed
        key = pygame.key.get_pressed()
        # Exit game
        if key[pygame.K_0]: sys.exit()
        if key[pygame.K_1]: return startNew(howToPlay())
        if key[pygame.K_2]: return startNew(endless(2))
        if key[pygame.K_3]: return startNew(endless(3))
        if key[pygame.K_4]: return startNew(endless(4))

        pygame.display.flip()
        # Run at set FPS
        clock.tick(FPS//4)

# How to play
def howToPlay():
    # Clean screen
    screen.fill('black')
    # Blit exit condition
    txt = comicSans.render(f'Press esc to return to main menu', True, 'white')
    screen.blit(
        txt, 
        ((screenW/2)-(txt.get_width()/2),7*(screenH/8))
    )

    # Blit player
    playerRect = playerImg.get_rect()
    playerRect.centerx = screenW/2
    playerRect.centery = screenH/2
    screen.blit(playerImg,playerRect)

    # Blit enemy
    enemyRect = enemyImg.get_rect()
    enemyRect.centerx = screenW-enemyRect.width
    enemyRect.centery = screenH/2
    screen.blit(enemyImg,enemyRect)

    # Blit bullet
    bulletRect = bulletImg.get_rect()
    bulletRect.centerx = screenW/2+12*bulletRect.width
    bulletRect.centery = screenH/2
    screen.blit(bulletImg,bulletRect)

    # Blit controls
    screen.blit(
        comicSans.render('Controls', True, 'white'), 
        (1.5*(screenW/20),7*(screenH/10))
    )

    screen.blit(
        comicSans.render('W', True, 'white'), 
        (2*(screenW/20),8*(screenH/10))
    )
    screen.blit(
        comicSans.render('A', True, 'white'), 
        (screenW/20,9*(screenH/10))
    )
    screen.blit(
        comicSans.render('S', True, 'white'), 
        (2*(screenW/20),9*(screenH/10))
    )
    screen.blit(
        comicSans.render('D', True, 'white'), 
        (3*(screenW/20),9*(screenH/10))
    )

    # Blit goal
    screen.blit(
        comicSans.render('Goal:', True, 'white'), 
        (fontSize,fontSize)
    )
    screen.blit(
        comicSans.render('1. Get the highest points possible.', True, 'white'), 
        (fontSize,2*fontSize)
    )
    screen.blit(
        comicSans.render('2. Click to fire bullets. If bullet connects with enemy, enemy dies and you score points.', True, 'white'), 
        (fontSize,3*fontSize)
    )
    screen.blit(
        comicSans.render('3. The longer you live, the more points you gain.', True, 'white'), 
        (fontSize,4*fontSize)
    )
    screen.blit(
        comicSans.render('4. Bullets cost points, so fire them conservatively.', True, 'white'), 
        (fontSize,5*fontSize)
    )
    screen.blit(
        comicSans.render('5. Do not let enemy touch you, or you lose health.', True, 'white'), 
        (fontSize,6*fontSize)
    )

    # Main loop
    while True:
        # Game breaks when this line is not included for some reason
        pygame.event.get()
        # Get keys pressed
        key = pygame.key.get_pressed()
        # Exit how to play
        if key[pygame.K_ESCAPE]:
            startNew(mainMenu())

        pygame.display.flip()
        # Run at set FPS
        clock.tick(FPS//4)


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

    #End# Game values
    while True:
        #Start# Things that are checked in every frame
        # Keys pressed
        key = pygame.key.get_pressed()
        # Get mouse position in every frame
        mousePos = pygame.mouse.get_pos()
        # Game duration
        currentTime = round(time.time()-startTime,2)
        # Enemy speed modifer
        enemySpdMod = currentTime/10
        # Is gun fired
        fired = False
        #End# Things that are checked in every frame

        # Events should use list comprehension
        events = [event.type for event in pygame.event.get()]
        if key[pygame.K_ESCAPE]: return startNew(mainMenu())

        # Restart game
        if key[pygame.K_r]:
            player.health = 0

        # Secret win
        if enemySpawnCounter == 10000:
            # Print lose message
            font=pygame.font.SysFont('Noto Sans',fontSize*7) # Font, size
            text=font.render('Secret Win!',True,'white') # Text, antialiasing, colour
            screen.blit(text,((screenW/2)-(text.get_width()/2),0)) # Location
            
            player.health = 0

        #enemySpawnCounter = 9999 # Debugging

        # If player is still alive
        if player.health > 0:

            # Clean screen with black
            screen.fill(('black'))
            # Bullets
            # Check if gun was fired
            if pygame.MOUSEBUTTONDOWN in events or key[pygame.K_SPACE]:
                fired = True
                bulletGroup.add(Bullet(bulletImg, (player.rect.centerx,player.rect.centery), 16, mousePos))

            # Update bullets
            for bullet in bulletGroup.sprites():
                addPoints, addEnemyKillCounter = bullet.update(activeEnemyGroup)
                points += addPoints
                enemyKillCounter += addEnemyKillCounter

            # Enemies
            if key[pygame.K_e] or enemySpawnCounter % 60 == 0:
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

            # Print mouse cursor location
            screen.blit(
                comicSans.render(str(mousePos), True, ('white')),
                (0,0)
            )

            # Print FPS
            screen.blit(
                comicSans.render(f'FPS: {round(clock.get_fps())}', True, 'white'),
                (screenW-(7*fontSize),0)
            )

            # Print points
            screen.blit(
                comicSans.render(f'Points: {points}', True, 'white'),
                (screenW-(7*fontSize),screenH-(3*fontSize))
            )

            # Print health
            screen.blit(
                comicSans.render(f'Health: {player.health}', True, 'pink'),
                (screenW-(7*fontSize),screenH-(2*fontSize))
            )

            # Print time
            screen.blit(
                comicSans.render(f'Time: {currentTime}', True, 'white'),
                (screenW-(7*fontSize),2*fontSize)
            )

        # If your health becomes 0
        if player.health <= 0:
            # Print lose message
            txt = comicSans.render('You died. Click r to play again. Click esc to exit.', True, 'purple')
            screen.blit(txt, ((screenW/2)-(txt.get_width()/2),(screenH/2)-txt.get_height()))

            # Print extra stats; enemies kill; bullets fired
            # Enemies killed
            txt = comicSans.render(f'Enemies killed: {enemyKillCounter}', True, 'purple')
            screen.blit(txt, ((screenW/2)-(txt.get_width()/2),(screenH/2)+txt.get_height()))
            # Bullets fired
            txt = comicSans.render(f'Bullets fired: {bulletsFired}', True, 'purple')
            screen.blit(txt, ((screenW/2)-(txt.get_width()/2),(screenH/2)+(2*txt.get_height())))

            if key[pygame.K_r]:
                return startNew(endless(spawnRate))

        pygame.display.flip()
        # Run at set FPS
        clock.tick(FPS)

# Exitting functions with return is the correct method of terminating functions, so they don't spit errors back at me
intro()