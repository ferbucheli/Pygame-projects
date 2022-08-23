### Sprites:
# Una clase que combina una superficie (imagen), un rect object y otras caracteristicas como animaciones y sonidos en un solo objeto

### Drawing in pygame:
# Display surface object es lo pantalla / ventana principal que se muestra a a hora de ejectar el juego
# No puedes mover imagenes por si solas; para moverlas hay que poner un rect object alrededor de ellas
# Basicamente la sprite class combina un surface object y un rect object en 1 solo objeto
# Puedo agregar sonidos, animaciones y comportamientos en una misma clase
# Sprite object: una representacion de un objeto real en el videojuego
# Un sprite puede ser el jugador principal

### Groups
# podemos agregar sprite a grupos y de ahi agregar funciones, updates o dibujar en 1 sola todos los sprites incluidos en el grupo
# Sirve mucho cuando tenemos muchos sprites creados y queremos dibujar enn el display surface esos sprites

import pygame, sys, random

# class Crosshair(pygame.sprite.Sprite):
#     def __init__(self,width,height,pos_x,pos_y,color):
#         super().__init__()
#         ## Creamos la imagen en blanco
#         self.image = pygame.Surface((width,height)) # Con esto creamos una superficie en blanco
#         ## Rellenamos la imagen con un color
#         self.image.fill(color)
#         ## Dibujamos un rect object alrededor de la imagen
#         self.rect = self.image.get_rect()
#         ## Colocamos el rect en la posicion indicada
#         self.rect.center = (pos_x,pos_y)

class Crosshair(pygame.sprite.Sprite):
    def __init__(self,picture_path):
        super().__init__()
        self.image = pygame.image.load(picture_path)
        self.rect = self.image.get_rect()
        # self.gunshot = pygame.mixer.Sound("")
    def shoot(self):
        pygame.sprite.spritecollide(crosshair,target_group,True) # spritecollide(object1, object2, True) mientras este True, cuando el objeto1 colisione con el objeto2, se destruira el objeto2
    def update(self):
        self.rect.center = pygame.mouse.get_pos()

class Target(pygame.sprite.Sprite):
    def __init__(self,picture_path,pos_x,pos_y):
        super().__init__()
        self.image = pygame.image.load(picture_path)
        self.rect = self.image.get_rect()
        self.rect.center = (pos_x,pos_y)    


crosshair = Crosshair("images/crosshair.png")
## Sprites no pueden ser dibujadas individualmente, tienen que ser dibujadas en grupo
# Creamos un grupo
crosshair_group = pygame.sprite.Group()
crosshair_group.add(crosshair)
#

# General Setup
pygame.init()
clock = pygame.time.Clock()

# Game Screen
screen_width = 1200
screen_height = 700
screen = pygame.display.set_mode((screen_width,screen_height))
background = pygame.image.load("images/bg_blue.png")
pygame.mouse.set_visible(False)

# Target

target_group = pygame.sprite.Group()
for target in range(20):
    new_target = Target("images/target.png",random.randrange(0,screen_width),random.randrange(0,screen_height))
    target_group.add(new_target)
          
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            crosshair.shoot()
        
    # Las instrucciones que van arriba son las que se ejecutan primero
    pygame.display.flip()
    
    #Pongo el background image el screen
    screen.fill((255,255,255)) #blit(imagen que queremos poner,(tupla con coordenadas x y y))
    target_group.draw(screen)
    # Dibujamos el grupo de crosshair
    crosshair_group.draw(screen) # .draw(indicarle en que superficie quiero que dibuje)
    crosshair_group.update()
    clock.tick(60)