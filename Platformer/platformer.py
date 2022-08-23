import pygame, sys
from pygame.locals import *
from pygame import mixer
import random
import pickle
from os import path

# Classes

class World:
    def __init__(self,data):
        
        self.tile_list = []

        # Load images
        dirt_img = pygame.image.load("images/dirt.png")
        grass_img = pygame.image.load("images/grass.png")


        row_count = 0
        # Columns are the x location of each object in the tile map
        # Rows are the y location of each object in the tile map
        for row in data:
            col_count = 0

            for tile in row:
                
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size,tile_size))
                    img_rect = img.get_rect() # Coge el tamaño de la imagen y crea un rect object en base a eso
                    # Coloco las coordenadas en las que van cada imagen
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img,img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size,tile_size))
                    img_rect = img.get_rect() # Coge el tamaño de la imagen y crea un rect object en base a eso
                    # Coloco las coordenadas en las que van cada imagen
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img,img_rect)
                    self.tile_list.append(tile)

                if tile == 3:
                    blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
                    blob_group.add(blob)

                if tile == 4:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
                    platform_group.add(platform)

                if tile == 5:
                    platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
                    platform_group.add(platform)
                
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count *  tile_size + (tile_size // 2))
                    lava_group.add(lava)

                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size // 2), row_count *  tile_size + (tile_size // 2))
                    coin_group.add(coin)

                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
                    exit_group.add(exit)

                col_count += 1
            row_count += 1
    
    def draw(self):
        for tile in self.tile_list:
            # Colocamos cada imagen de tierra con sus coordenadas correspondientes
            screen.blit(tile[0],tile[1]) # blit(surface,rect)
            # pygame.draw.rect(screen,(255,255,255),tile[1],2)

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False
        
    def draw(self):
        action = False
        # Get mouse position
        pos = pygame.mouse.get_pos()
        
        # Check mouse over and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False: # pygame.mpuse.get_pressed()[0] - el numero que estoy accediendo cambia dependiendo del boton del mouse que quuiero verificar que este aplastado
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
    
        # Draw Button
        screen.blit(self.image,self.rect)

        return action
 
class Player:
    def __init__(self,x,y):

        self.reset(x,y)

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 10 # Cuantas veces tiene que iterar el incremento del atributo self.counter para que se cambie cada imagen de la animacion
        col_thresh = 20 # Distancia en pixeles para determinar si es que esta encima o debajo de un moving platform

        # Voy a entrar a un If statement que detereminas si me puedo mover si esque estoy vivo, o muerto por lava o enemigos
        if game_over == 0:
            # Get key presses
            key = pygame.key.get_pressed()

            if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False: # No puede saltar si es que esta en el aire
                jump_fx.play()
                self.vel_y = -15
                self.jumped = True
            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_a]:
                dx -= 5
                self.flip = True
                self.direction = -1
                self.counter += 2 # Quiero que el counter aumente (para generar la animacion), mientras el usario presione las teclas para caminar
            if key[pygame.K_d]:
                dx += 5
                self.flip = False
                self.direction = 1
                self.counter += 2
            # Mientras las teclas de caminar no esten presionadas, quiero que la animacion se resetee
            if key[pygame.K_a] == False and key[pygame.K_d] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index] # Cambia de imagen en cada iteracion
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Handle Animation
            # self.counter += 1
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index] # Cambia de imagen en cada iteracion
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # Add gravity
            # Si vel_y es positiva es que el jugador esta cayendo pero si es negativa es que el juagador esta saltando
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Check for collision with grass and dirt blocks
            self.in_air = True
            for tile in world.tile_list:

                # Check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx,self.rect.y, self.width, self.height):
                    dx = 0

                # Check for collision in y direction with the player
                # Crea un rectangulo imaginario para chequear la colision antes de que ocurran el moviemiento
                # Crea ese rectangulo imaginario para prevenir que el jugador quede dentro del bloque o pase a traves de ellos
                # Prevee el movimiento del jugador en el y axis   
                if tile[1].colliderect(self.rect.x,self.rect.y + dy, self.width, self.height):
                    # Check if below the ground (jumping)
                    if self.vel_y < 0:
                        # Resta
                        dy = tile[1].bottom - self.rect.top # Bottom of the tile and top of the player (rect)
                        self.vel_y = 0
                    # Check if above the ground (falling)
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        # Trigger the in air variable because in this section the player is standing in top of a block
                        self.in_air = False # (Landin in top of something)

            # Check for collision with enemies
            if pygame.sprite.spritecollide(self,blob_group,False): # Voy a indicar que cuando tenga una colision con la instancia del objeto de clase Player, se reinicie el juego
                game_over = -1
                game_over_fx.play()
            
            # Check for collision with lava
            if pygame.sprite.spritecollide(self,lava_group,False): # Voy a indicar que cuando tenga una colision con la instancia del objeto de clase Player, se reinicie el juego
                game_over = -1
                game_over_fx.play()
            
            # Check for collision with lava
            if pygame.sprite.spritecollide(self,exit_group,False): # Voy a indicar que cuando tenga una colision con la instancia del objeto de clase Player, se reinicie el juego
                game_over = 1

            # Check for collision with platforms
            for platform in platform_group:
                # Collision in the x direction
                if platform.rect.colliderect(self.rect.x + dx,self.rect.y, self.width, self.height):
                    dx = 0
                
                # Collision in y direction
                if platform.rect.colliderect(self.rect.x,self.rect.y + dy, self.width, self.height):
                    ## El parametro que se usa para determinar si es que esta abajo o arriba de una plataforma es col_tresh;
                    ## Si es que la distancia entre el top del rect imaginario y la plataforma es muy pequeña, entonces es que esta abajo
                    # Check if below the platform
                    if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
                        self.vel_y = 0 # Si se choca la cabeza con algo, su velocidad debe parar
                        dy = platform.rect.bottom - self.rect.top
                    
                    # Check if above platform
                    elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
                        dy = 0
                        self.rect.bottom = platform.rect.top - 1
                        self.in_air = False

                    # Move sideways with platform
                    if platform.move_x != 0: # Chequea que la plataforma sea de las que se mueve en el eje x
                        self.rect.x += platform.move_direction


            # Update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text("GAME OVER", font, blue, (screen_width // 2) - 200, screen_height // 2)

            # The ghost floats
            if self.rect.y > 200:
                self.rect.y -= 5

        # Draw player on screen
        screen.blit(self.image, self.rect)
        
        # Tengo que retornar la variable game_over para que asi se guarde la modificacion que ocurrio en ese method en la variable global
        return game_over

    # Metodo para que se resetee el jugador a su estado de inicio de juego
    def reset(self,x,y):
        # Player walking animation
        self.images_right = [] # Contain all the animation sprites
        self.images_left = []
        self.index = 0 # Track the index of the images list
        self.counter = 0 # Control the speed the animation runs (Slow down the animation)

        for num in range(1,5):
            img_right = pygame.image.load(f"images/guy{num}.png")
            img_right = pygame.transform.scale(img_right,(40,80))
            img_left = pygame.transform.flip(img_right, True, False) # Volteo para el lado izquiero la imagen para que se vea que esta mirando al lado izquierdo
            self.images_right.append(img_right)
            self.images_left.append(img_left)

        self.image = self.images_right[self.index] # Escoge las imagenes
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0 # Determina si estoy saltando o cayendo: positiva (cayendo por accion gravedad) o  negativam (saltando)
        self.jumped = False
        self.flip = False
        self.direction = 0 # Direccion del personaje
        self.dead_image = pygame.image.load("images/ghost.png")
        self.in_air = True # Variable that function as a trigger to keep track when the player is in air

class Enemy(pygame.sprite.Sprite):
    # Sprite class ya viene con un update y un draw method
    def __init__(self, x ,y):
        super().__init__()
        self.image = pygame.image.load("images/blob.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img = pygame.image.load("images/lava.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img = pygame.image.load("images/exit.png")
        self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super().__init__()
        img = pygame.image.load("images/coin.png")
        self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y,move_x,move_y):
        super().__init__()
        img = pygame.image.load("images/platform.png")
        self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter = 0
        self.move_direction = 1
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        
        self.rect.x += self.move_direction * self.move_x
        self.rect.y += self.move_direction * self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()
clock = pygame.time.Clock()

# Screen
screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Platformer")

# Define Font
font_score = pygame.font.SysFont("Bauhaus 93",30)
font = pygame.font.SysFont("Bauhaus 93", 70)
# Define Colors
white = (255,255,255)
blue = (0,0,255)

# Define game variables
tile_size = 50
game_over = 0
main_menu = True # Trigger if the state of the game is in the main menu
level = 0
max_levels = 7
score = 0

# Load Images
sun_img = pygame.image.load("images/sun.png")
bg_img = pygame.image.load("images/sky.png")
restart_img = pygame.image.load("images/restart_btn.png")
star_img = pygame.image.load("images/start_btn.png")
exit_img = pygame.image.load("images/exit_btn.png")

# Load sounds
pygame.mixer.music.load("images/music.wav")
pygame.mixer.music.play(-1,0.0,5000)
coin_fx = pygame.mixer.Sound("images/coin.wav")
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound("images/jump.wav")
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound("images/game_over.wav")
game_over_fx.set_volume(0.5)

## Funciones:

# Drawing the grid on screen
def draw_grid():
    for line in range(0,20):
        pygame.draw.line(screen,(255, 255, 255), (0, line * tile_size), (screen_width, line * tile_size))
        pygame.draw.line(screen,(255, 255, 255), (line * tile_size, 0 ), (line * tile_size, screen_height))

# Reset level
def reset_level(level):
    player.reset(100,screen_height - 130)
    # Clearing groups to wipe the items from the previous levels
    blob_group.empty()
    lava_group.empty()
    exit_group.empty()
    platform_group.empty()
    if path.exists(f"level{level}_data"): # Chequea si la ruta a la que estoy accediendo existe
        pickle_in = open(f"level{level}_data","rb")
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world

# Draw text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))



# World data
# world_data = [
# [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
# [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1], 
# [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1], 
# [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
# [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1], 
# [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
# [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
# [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1], 
# [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1], 
# [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
# [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
# [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
# ]



# Creo una lista de listas compuestas por numeros

# world_data = [[ 0 for x in range(20)] for x in range(20)]


player = Player(100, screen_height - 130)
blob_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()

# Create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

# Load level data and create world
if path.exists(f"level{level}_data"): # Chequea si la ruta a la que estoy accediendo existe
    pickle_in = open(f"level{level}_data","rb")
    world_data = pickle.load(pickle_in)
world = World(world_data)

# Create Buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2, restart_img)
start_button = Button(screen_width // 2 - 200, screen_height // 2, star_img)
exit_button = Button(screen_width // 2 + 100, screen_height // 2, exit_img)

FPS = 60
run = True

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.blit(bg_img, (0,0))
    screen.blit(sun_img,(100,100))

    # Logic of the game:
    # Separates the main menu from the actual game
    if main_menu:
        if exit_button.draw():
            pygame.quit()
            sys.exit()
        if start_button.draw():
            main_menu = False
    else:
        world.draw()

        if game_over == 0:
            blob_group.update()
            platform_group.update()

            # Update Score
            # Check if a coin is being colleted
            if pygame.sprite.spritecollide(player, coin_group, True): # When the collision occurs, the coin eliminates
                score += 1
                coin_fx.play()
            draw_text("X " +  str(score), font_score, white, tile_size - 10, 10 )
        
        blob_group.draw(screen)   
        game_over = player.update(game_over) # Tengo que guardar el resultado de este method para que se actualice globalmente las modificaciones

        # If player has died
        if game_over == -1:
            if restart_button.draw():
                # reset level
                world_data = [] # Clear the already existing data and prepare to load new data
                world = reset_level(level) # Reload the same level
                game_over = 0
                score = 0

        # If player completed the level
        if game_over == 1:
            # reset game and go to next lvl
            level += 1
            if level <= max_levels:
                # reset level
                world_data = [] # Clear the already existing data and prepare to load new data
                world = reset_level(level) # Load the new level
                game_over = 0
            else:
                draw_text("YOU WIN", font, blue, (screen_width // 2) - 140, screen_height // 2)
                if restart_button.draw():
                    # Cuando terminamos todos los niveles, hay una opcion para volver a emepezar
                    level = 1
                    world_data = [] # Clear the already existing data and prepare to load new data
                    world = reset_level(level) # Load the new level
                    game_over = 0
                    score = 0

        lava_group.draw(screen)
        platform_group.draw(screen)
        exit_group.draw(screen)
        coin_group.draw(screen)
        # draw_grid()

    pygame.display.update()
    clock.tick(FPS)