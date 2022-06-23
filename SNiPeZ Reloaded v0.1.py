# Created: 18/6/2022
# Last editted: 20/6/2022
import pygame,sys,os,random,time

# Path to this folder
path=os.path.dirname(os.path.realpath(__file__))

# Initialise text module first
pygame.font.init()
comicSans = pygame.font.SysFont('Comic Sans MS', 30)

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
screen = pygame.display.set_mode(vsync=0)

# Screen dimensions
screenW, screenH = screen.get_width(), screen.get_height()

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
    __slots__ = 'img', 'rect', 'initPos', 'direction', 'vel', 'enemyGroup'

    def __init__(self, img, initPos, vel, mousePos, enemyGroup):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)
        
        self.img = img
        self.rect = img.get_rect()
        self.rect.move_ip(initPos)
        self.direction = mousePos[0]-self.rect.centerx,mousePos[1]-self.rect.centery
        self.vel = vel
        self.enemyGroup = enemyGroup
    
    def update(self):
        # Using a trusty try/except statement to ignore errors
        try:
            ## Movement
            # Give bullet it's correct velocity in relation to the player mouse
            bulletMove=pygame.math.Vector2(self.direction[0],self.direction[1])

            bulletMove.scale_to_length(self.vel)

            # Move bullet
            self.rect = self.rect.move(bulletMove)
            
            # Render bullet
            screen.blit(self.img, self.rect)


            # If bullet collides with enemy, destroy enemy and give player a point
            if pygame.sprite.spritecollide(self,self.enemyGroup, True):
                global points
                points += 60
            
        except:
            pass

class EnemyStandard(pygame.sprite.Sprite):
    __slots__ = 'img', 'rect', 'vel', 'player'

    def __init__(self, img, vel, player):
        # Construct sprite
        pygame.sprite.Sprite.__init__(self)

        self.img = img
        self.rect = img.get_rect()
        self.rect.move_ip(self.initPos())
        self.vel = vel
        self.player = player

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
    
    def update(self):
        # Using a trusty try/except statement to ignore errors
        try:
            ## Movement
            # Give bullet it's correct velocity in relation to the player mouse
            bulletMove=pygame.math.Vector2(self.player.rect.x-self.rect.x,self.player.rect.y-self.rect.y)

            # Limit bullet speed to bullet.vel
            bulletMove.scale_to_length(self.vel)

            # Move bullet
            self.rect = self.rect.move(bulletMove)

            # Render bullet
            screen.blit(self.img, self.rect)
        except:
            pass

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

# Introduction
def intro():
    screen.fill('black')    
    introMove=[41,41]
    introImg=pygame.image.load(f'{path}/Intro.png')
    introRect=introImg.get_rect()
    introRect.move_ip(0,0)
    while True:
        for event in pygame.event.get():
            if event.type==pygame.MOUSEBUTTONDOWN:
                return

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
        text=font.render('Left click to continue',True,'black') # Text, antialiasing, colour
        screen.blit(text,(2*screenW/4,5*(screenH/6))) # Location

        pygame.display.update()
        clock.tick(FPS*4)

# Main code
def main():
    #Start# Game values
    # Initiate entity lists
    bulletGroup = pygame.sprite.Group()
    enemyGroup = pygame.sprite.Group()

    # Enemy and player spawning
    enemySpawnCounter = 0
    player = Player(playerImg, 10, 5)

    # Game counter
    startTime = time.time()

    # Player points
    points = 0
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
        if key[pygame.K_ESCAPE]: sys.exit()

        # Restart game
        if key[pygame.K_r]:
            player.health = 0

        # If player is still alive
        if player.health > 0:
            # Clean screen with black
            screen.fill(('black'))
            # Bullets
            # Check if gun was fired
            if pygame.MOUSEBUTTONDOWN in events or key[pygame.K_SPACE]:
                fired = True
                bulletGroup.add(Bullet(bulletImg, (player.rect.centerx,player.rect.centery), 16, mousePos, enemyGroup))
            bulletGroup.update()

            # Enemies
            enemySpawnCounter += 1
            enemySpawnCounter %= 60
            if key[pygame.K_e] or enemySpawnCounter == 0:
                enemyGroup.add(EnemyStandard(enemyImg, 4 + enemySpdMod, player))
                enemyGroup.add(EnemyStandard(enemyImg, 4 + enemySpdMod, player))
            enemyGroup.update()

            # Update player movement
            player.update(key, enemyGroup)

            # Points scoring system
            # Add 60 point per second
            points += 1
            # Lose 30 points for every bullet fired
            if fired == True:
                points -= 20

            # Print mouse cursor location
            mousePosTxt = comicSans.render(str(mousePos), False, ('white'))
            screen.blit(mousePosTxt, (0,0))

            # Print FPS
            FPSTxt = comicSans.render(f'FPS: {round(clock.get_fps())}', False, 'white')
            screen.blit(FPSTxt, (screenW-200,0))

            # Print points
            PointsTxt = comicSans.render(f'Points: {points}', False, 'white')
            screen.blit(PointsTxt, (screenW-200,screenH-100))

            # Print health
            HealthTxt = comicSans.render(f'Health: {player.health}', False, 'pink')
            screen.blit(HealthTxt, (screenW-200,screenH-50))

            # Print time
            TimeTxt = comicSans.render(f'Time: {currentTime}', False, 'white')
            screen.blit(TimeTxt, (screenW-200,50))

        # If your health becomes 0
        if player.health <= 0:
            # Print loss message
            PointsTxt = comicSans.render(str('You died. Click r to play again. Click esc to exit.'), False, 'white')
            screen.blit(PointsTxt, ((screenW/2)-(PointsTxt.get_width()/2),(screenH/2)-(PointsTxt.get_height()/2)))
            if key[pygame.K_r]:
                return

        pygame.display.flip()
        # Run at set FPS
        clock.tick(FPS)

# Exitting functions with return is the correct method of terminating functions, so they don't spit errors back at me
intro()
while True:
    main()