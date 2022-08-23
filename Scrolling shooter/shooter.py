import pygame, sys, os
import random, pickle, button
from pygame import mixer

mixer.init()
pygame.init()
# Clases

class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks() # Es un timestamp estatico y solo agarra el tiempo cuando activamos determinada accion
        self.char_type = char_type

        ## Loops for creating the list of images to generate animation
        # Load all images for animation
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            # Reset temp list of images
            temp_list = []
            # Count number of files in the folder
            num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))
            for i in range(num_of_frames):
                img = pygame.image.load(f"img/{self.char_type}/{animation}/{i}.png").convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # A estos les pongo self antes para que sea unico para cada intancia que se cree del soldado
        self.image = self.animation_list[self.action][self.frame_index]
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True # Assume the player is in air until it lands on something
        self.flip = False
        self.rect = img.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

        #Create ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0, 150, 20)
        self.idling = False
        self.idling_counter = 0

    def move(self, moving_left, moving_right):
        ## Reset movement variables
        screen_scroll = 0
        # dx y dy (cambio en el movimiento)
        # Ponemos dx y dy para que sea mas preciso el movimineto prediciendo el movimiento usando estas variables
        dx = 0
        dy = 0

        # Assing movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Jump
        if self.jump and self.in_air == False:
            self.vel_y = -11
            self.jump = False
            self.in_air = True

        # Apply gravity
        self.vel_y += GRAVITY
        # Limit the gravity
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        ### Check for collision
        for tile in world.obstacle_list:
            # Check for collision in the x direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0 # Stop x movement and getting through blocks
                # If the ai has hit a wall, make it turn around
                if self.char_type == "enemy":
                    self.direction *= - 1
                    self.move_counter = 0
            # Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # Check if below the groung (jumping)
                if self.vel_y < 0: # Player is moving up
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if above the ground (falling)
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        # Check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # Check for collsion with exit
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        
        # Check if fallen off the map
        if self.rect.top > SCREEN_HEIGHT:
            self.health = 0

        # Check if going off the edges of the screen
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0 # Stop movement

        # Update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        # Update scroll based on player's position
        if self.char_type == "player":
            if (self.rect.right > SCREEN_WIDTH - SCROLL_TRESH and bg_scroll < (world.level_lenght * TILE_SIZE) - SCREEN_WIDTH) or (self.rect.left < SCROLL_TRESH and bg_scroll > abs(dx)):
                # Cuando el jugador entra en el limite de la pantalla de scrolleo, se debe de quedar quieto mientras que
                # todo su alrededor se mueve para dar la ilusion de que recorre el mapa
                self.rect.x -= dx # The player is moved back
                screen_scroll = -dx 
            
        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            bullet = Bullet(self.rect.centerx + (self.rect.size[0] * 0.75 * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            self.ammo -= 1 # Reduce ammo
            shot_fx.play()

    def ai(self):
        
        if self.alive and player.alive:
            random_number = random.randint(1,200)
            if self.idling == False and random_number == 1:
                self.update_action(0) # 0: idling
                self.idling = True
                self.idling_counter = 50
            # Check if the ai is near the player
            if self.vision.colliderect(player.rect):
                # Stop running and face the playert
                self.update_action(0)
                #Shoot
                self.shoot()
            else:
                if self.idling ==  False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left,ai_moving_right)
                    self.update_action(1) # 1: run
                    self.move_counter += 1
                    #Update au vusion rect as the enemy moves
                    self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen, RED, self.vision)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # Scroll
        self.rect.x += screen_scroll

    def update_animation(self):
        # Timer to change the images of animation_list as a sequence
        # update animation
        ANIMATION_COOLDOWN = 100 # control the speed of the animation
        CURRENT_TIME = pygame.time.get_ticks() # Va a chequearse constantemente

        # Update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]

        # Check if enough time has passed since last update 
        if CURRENT_TIME - self.update_time > ANIMATION_COOLDOWN:
            # Increase the next index of the animation_list to pass to the other image
            self.update_time = pygame.time.get_ticks() # Resets the timer
            self.frame_index += 1
    
        # If the animation has run out the reset back to the start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def update(self):
        self.update_animation()
        self.check_alive()
        # Decrease the cooldown for shooting
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def update_action(self, new_action):
        # Check if the new action is different to the prevoius one
        if new_action != self.action:
            self.action = new_action 
            # Reset the animation back to the start
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        # Hago uso de los atributos anteriormente creados para darle vuelta a la imagen dependiendo de al direccion a la que se dirige el soldado
        screen.blit(pygame.transform.flip(self.image,self.flip, False),self.rect)

class World:
    def __init__(self):
        self.obstacle_list = [] # Dirt blocks to check collision

    def process_data(self, data):
        self.level_lenght = len(data[0])
        # Iteraten through each value in level data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15: # Create a player
                        player = Soldier("player", x * TILE_SIZE, y * TILE_SIZE, 1.65, 5, 20, 10)
                        health_bar = HealthBar(10, 10, player.health, player.health)
                    elif tile == 16: # Create enemies
                        enemy = Soldier("enemy", x * TILE_SIZE, y * TILE_SIZE, 1.65, 2 , 20, 0)
                        enemy_group.add(enemy)
                    elif tile == 17: # Create ammo box
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18: # Create Grenade box
                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19: # Create Health box
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20: # Create Exit
                        exit = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit)

        return player, health_bar

    def draw(self):
        
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1]) # tile[0]: img - tile[1]: Rect

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect(center = (x,y))
        self.direction = direction

    def update(self):
        # Move the bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        
        # Check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # Check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # Check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if player.alive:
                    enemy.health -= 25
                    self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self,x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = -11 
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect(center = (x,y))
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):

        self.vel_y += GRAVITY
        dx = self.speed * self.direction
        dy = self.vel_y

        # Check for collision with level
        for tile in world.obstacle_list:
            # Collision with walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.speed * self.direction
            # Check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                # Check if below the groung (thrown up)
                if self.vel_y < 0: # Player is moving up
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # Check if above the ground (falling)
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        
        # Update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # Countdown timer
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)

            # Do damage to anyone nearby
            
            # Check distance between greneade and other objects; create a damage radius when the grenade explodes
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2: # Distance between de player and grenade
                player.health -= 50
            
            # Iterate the enemy group
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2: # Distance between de player and grenade
                    enemy.health -= 50

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x, y, scale):
        super().__init__()
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f"img/explosion/exp{num}.png").convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect(center = (x,y))
        self.counter = 0 # Cooldown for the animation

    def update(self):
        # Scroll
        self.rect.x += screen_scroll
        EXPLOSION_SPEED = 4
        # update explosion animation
        self.counter += 1
        
        if self.counter >= EXPLOSION_SPEED:
            self.counter = 0
            self.frame_index += 1
            
            # If the animation is complete, delete the explosion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
      
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect(midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())))
    
    def update(self):
        # Scroll
        self.rect.x += screen_scroll
        # Check if the player has picked up the box
        if pygame.sprite.collide_rect(self, player):
            # Check what kind of box it was
            if self.item_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 15
            elif self.item_type == "Grenade":
                player.grenades += 3

            # Delete the item box
            self.kill()

class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # Update with new health
        self.health = health
        # Calculate health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0
        
    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1: # Whole Screeen fade
            pygame.draw.rect(screen, self.color, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.color, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
            pygame.draw.rect(screen, self.color, (0, SCREEN_HEIGHT // 2 + self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
        if self.direction == 2: # Vertical screen fade down
            pygame.draw.rect(screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete = True
        
        return fade_complete

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Shooter")

# Game Variables
run = True
FPS = 60
clock = pygame.time.Clock()
SCROLL_TRESH = 200 # Distance the player can get to edge of the screen before it starts to scroll
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False # Act as a trigger bewteen the menu and game states
MAX_LEVELS = 2
start_intro = False # Every time I set the start intro to True, is going to run the fade

# Define Colors
BG = (144,201,120)
RED = (255,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLACK = (0,0,0)
PINK = (235, 65, 54)

# Define Font
font = pygame.font.SysFont("Futura", 30)

# Sprite Groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# Define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False # Trigger para que cuando mantenga aplastado la tecla de lanzar granadas no se sigan lanzando

### Load music and sounds
# pygame.mixer.music.load("audio/audio_music2.mp3")
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1, 0.0, 5000) # .play(# of loops, delay, fade in)

jump_fx = pygame.mixer.Sound("audio/audio_jump.wav")
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound("audio/audio_shot.wav")
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound("audio/audio_grenade.wav")
grenade_fx.set_volume(0.05)

### Load Images
# Background
pine1_img =  pygame.image.load("img/Background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("img/Background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("img/Background/mountain.png").convert_alpha()
sky_img = pygame.image.load("img/Background/sky_cloud.png").convert_alpha()
# Button Images
start_img = pygame.image.load("img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("img/restart_btn.png").convert_alpha()
# Store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"img/Tile/{x}.png")
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)
# Bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
# Grenade
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
# Pickup Boxes
heal_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()

item_boxes = {
    "Health" : heal_box_img,
    "Ammo" : ammo_box_img,
    "Grenade" : grenade_box_img
}

# Create empty tile list
world_data = []
# Load level data
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# Load in level data and create world
picke_in = open(f"level{level}_data", "rb")
world_data = pickle.load(picke_in)

world = World()
player, health_bar = world.process_data(world_data)

# Create Screen Fades
death_fade = ScreenFade(2, PINK, 4)
intro_fade = ScreenFade(1, BLACK, 4)

# Create Buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 -150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_img, 2)

## Funciones

# Draw Background
def draw_bg():
    screen.fill(BG)
    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6 , SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))

# Draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Function to reset level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    # Create empty tile list
    data = []
    # Load level data
    for row in range(ROWS):
        r = [-1] * COLS
        data.append(r)

    return data

# Game main Loop

while run:

    if start_game == False:
        # Main Menu
        # 1. Draw Menu
        screen.fill(BG)
        # 2. Add buttons
        if start_button.draw(screen): # (Being Clicked)
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            pygame.quit()
            sys.exit()

    else:
        # Update background
        draw_bg()
        # Draw World Map
        world.draw()
        
        # Show player health
        health_bar.draw(player.health)
        # Show Ammo
        draw_text("AMMO: ", font, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        # Show Grenades
        draw_text("GRENADES: ", font, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))

        player.draw()
        player.update()

        for enemy in enemy_group:
            enemy.ai()
            enemy.draw()
            enemy.update()
        

        #Update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        # Show Intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0

        # Update player actions
        if player.alive:
            # Shoot bullets
            if shoot:
                player.shoot()
            # Throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (player.rect.size[0] * 0.5 * player.direction), player.rect.top, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True # Lockeo el trigger de lanzar granadas
                player.grenades -= 1 # Reduce number of grenades

            if player.in_air:
                player.update_action(2) # 2: Jump
            elif moving_left or moving_right:
                player.update_action(1) # 1: run
            else:
                player.update_action(0) # 0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # Check if player has completed the level
            if level_complete:
                start_intro = True # Every time I set this variables to True, it runs the intro
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    # Load in level data and create world
                    picke_in = open(f"level{level}_data", "rb")
                    world_data = pickle.load(picke_in)

                    world = World()
                    player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    # Load in level data and create world
                    picke_in = open(f"level{level}_data", "rb")
                    world_data = pickle.load(picke_in)

                    world = World()
                    player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Keybaord presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_e and player.alive:
                shoot = True
            if event.key == pygame.K_q and player.alive:
                grenade = True
            
        # Keyboard button releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_e and player.alive:
                shoot = False
            if event.key == pygame.K_q and player.alive:
                grenade = False
                grenade_thrown =  False # Cuando suelto la tecla, se desactiva el lock del trigger de lanzar granadas
        
    pygame.display.update()
    clock.tick(FPS)
    