import pygame, sys, random
from pygame.math import Vector2

class Fruit:
    def __init__(self):
        # 1. create an x and y position
        # 2. Draw a square (fruit)
        self.x = random.randint(0,cell_number -1)
        self.y = random.randint(0,cell_number -1)
        # Ponemos el valor de x y y en un vector para despues dibujarlo
        self.pos = Vector2(self.x,self.y)

    def draw_fruit(self):
        # 1. create a rectangle
        # 2. Draw the rectangle
        fruit_rect = pygame.Rect(self.pos.x * cell_size,self.pos.y * cell_size,cell_size,cell_size) # crea el rect object -  pygame.Rect(x,y,width,height)
        # pygame.draw.rect(screen,(126,166,140),fruit_rect) # Dibuja el rectangulo en una superficie - pygame.draw.rect(surface,color,rect_object)
        screen.blit(apple,fruit_rect) # screen.blit(superficie (imagen), rect object) -  la imagen que cargamos cuenta como superficie
    def randomize(self):
        # Es el mismo codigo que el anterior para ubicar la fruta en un lugar random
        self.x = random.randint(0,cell_number -1)
        self.y = random.randint(0,cell_number -1)
        self.pos = Vector2(self.x,self.y)

class Snake:
    def  __init__(self):
        # Va a guardar todos los bloques que conforman la snake
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self.direction = Vector2(1,0)
        self.new_block = False

        ## Graficos
        
        # Cabeza
        self.head_up = pygame.image.load("images/head_up.png").convert_alpha()
        self.head_down = pygame.image.load("images/head_down.png").convert_alpha()
        self.head_right = pygame.image.load("images/head_right.png").convert_alpha()
        self.head_left = pygame.image.load("images/head_left.png").convert_alpha()

        # Cola
        self.tail_up = pygame.image.load("images/tail_up.png").convert_alpha()
        self.tail_down = pygame.image.load("images/tail_down.png").convert_alpha()
        self.tail_right = pygame.image.load("images/tail_right.png").convert_alpha()
        self.tail_left = pygame.image.load("images/tail_left.png").convert_alpha()

        # Body
        self.body_vertical = pygame.image.load("images/body_vertical.png").convert_alpha()
        self.body_horizontal = pygame.image.load("images/body_horizontal.png").convert_alpha()

        # Turns
        self.body_tr = pygame.image.load("images/body_tr.png").convert_alpha()
        self.body_tl = pygame.image.load("images/body_tl.png").convert_alpha()
        self.body_br = pygame.image.load("images/body_br.png").convert_alpha()
        self.body_bl = pygame.image.load("images/body_bl.png").convert_alpha()

    def draw_snake(self):
        ## Old Code:
        
        #for block in self.body:
            
            # Create a rect
            # Draw a rect
            # snake_block = pygame.Rect(block.x * cell_size, block.y * cell_size,cell_size,cell_size)
            # pygame.draw.rect(screen,(183,191,122),snake_block)

        ## New Code:
        self.update_head()
        self.update_tail()
        for i,block in enumerate(self.body):
            # 1. Need a rect for positioning
            # 2. Figure out what direction is the head heading

            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos,y_pos,cell_size,cell_size)

            ## Quemamos las variables de la cabeza y la cola para que no de error cuando pognamos graficos al cuerpo de la serpiente

            if i == 0: # Primer elemento de los vectores (cabeza)
                screen.blit(self.head,block_rect)

            elif i == len(self.body) - 1: # Ultimo elemento de los vectores (cola)
                screen.blit(self.tail,block_rect)
            
            # Cuerpo de la serpiente
            else:
                # Obtenemos las relaciones entre el anterior bloque y el siguiente bloque
                previous_block = self.body[i + 1] - block
                next_block = self.body[i - 1] - block
                # Verficamos que tengan la misma coordenada en x o en y
                if previous_block.x == next_block.x:
                    screen.blit(self.body_vertical,block_rect)
                elif previous_block.y == next_block.y:
                    screen.blit(self.body_horizontal,block_rect)
                
                # Chequear las esquinas del cuerpo
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        screen.blit(self.body_tl,block_rect)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        screen.blit(self.body_bl,block_rect)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        screen.blit(self.body_tr,block_rect)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        screen.blit(self.body_br,block_rect)

    def update_head(self):
        # Nos va a dar en que dirrecion esta el bloque que le sigue a la cabeza para asi darle direccion a la imagen
        head_relation = self.body[1] - self.body[0]
        # Este method crea un nuevo atributo para la clase Snake
        if head_relation == Vector2(1,0): self.head = self.head_left 
        if head_relation == Vector2(-1,0): self.head = self.head_right
        if head_relation == Vector2(0,1): self.head = self.head_up
        if head_relation == Vector2(0,-1): self.head = self.head_down

    def update_tail(self):
        # Nos va a dar en que dirrecion esta el bloque despues de la cola para asi darle direccion a la imagen
        tail_relation = self.body[-2] - self.body[-1]
        # Este method crea un nuevo atributo para la clase Snake
        if tail_relation == Vector2(1,0): self.tail = self.tail_left 
        if tail_relation == Vector2(-1,0): self.tail = self.tail_right
        if tail_relation == Vector2(0,1): self.tail = self.tail_up
        if tail_relation == Vector2(0,-1): self.tail = self.tail_down


        

    def move_snake(self):
        # Basicamente lo que hago aqui es que si es que quiero agregar un bloque, no borro el ultimo cuadro (vector) pero agrego 1 nuevo al principio
        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0,body_copy[0] + self.direction)
            self.body = body_copy
            self.new_block = False
        else: # Pero si no se activa el add_block(), solo hago que se mueva normalmente
            body_copy = self.body[:-1]
            body_copy.insert(0,body_copy[0] + self.direction)
            self.body = body_copy
    
    def add_block(self):
        self.new_block = True

    def reset(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]

class Main:
    def __init__(self):
        self.snake = Snake()
        self.fruit = Fruit()
    
    # Update method sirve para chequear constantemente lo que esta pasando en la logica del juego y hacer acciones al respecto
    def update(self):
        self.snake.move_snake()
        self.check_collision()
        self.check_fail()

    def draw_elements(self):
        self.draw_grass()
        self.draw_score()
        self.fruit.draw_fruit()
        self.snake.draw_snake()

    def check_collision(self):
        # Chequea que la cabeza de la serpiente se encuentre en el mismo recuadro que la fruta
        if self.fruit.pos == self.snake.body[0]:
            # Cuando la cabeza de la snake collide con la fruta quiero que:
            #1. La Fruta se reposicione
            #2. Agregar otro bloque a la serpiente
            self.fruit.randomize()
            self.snake.add_block()

            # No queremos que aparezca una fruta en nuestro cuerpo
            for block in self.snake.body[1:]: 
                if block == self.fruit.pos: # Le indicamos que si el bloque esta en la misma posicion que la fruta, ponga la fruta en otro lugar
                    self.fruit.randomize()

    def check_fail(self):
        # 1.  check if snake its outside of the screen
        # 2. Check if the snake hits itself
        if not 0 <= self.snake.body[0].x < cell_number or not 0 <= self.snake.body[0].y < cell_number:
            self.gameover()

        # Chequeamos si la cabeza de la serpiente se ha chocado con cualquier parte del cuerpo
        for block in self.snake.body[1:]: # Cogemos todos los bloques excepto la cabeza
            if block == self.snake.body[0]: # Verificamos que la posicion de esos bloques coincida con la de la cabeza
                self.gameover()

    def gameover(self):
        self.snake.reset()

    def draw_grass(self):
        grass_color = (167,209,61)

        for row in range(cell_number):
            if row % 2 == 0:
                for col in range(cell_number):
                    if col % 2 == 0:
                        grass_rect = pygame.Rect(col * cell_size,row * cell_size,cell_size,cell_size)
                        pygame.draw.rect(screen,grass_color,grass_rect)
            else:
                for col in range(cell_number):
                    if col % 2 != 0:
                        grass_rect = pygame.Rect(col * cell_size,row * cell_size,cell_size,cell_size)
                        pygame.draw.rect(screen,grass_color,grass_rect)

    def draw_score(self):
        score_text = str(len(self.snake.body) - 3)
        score_surface = game_font.render(score_text,True,(56,74,12)) # font.render(text,aa,color)
        score_x = int(cell_size * cell_number - 60)
        score_y = int(cell_size * cell_number - 40)
        score_rect = score_surface.get_rect(center = (score_x,score_y)) # surface.get_rect( center = (x,y)) -  para poner un rectangulo alrededor de una superficie (text surface)
        # center = (x,y) - sirve para poner el centro de un rect en un lugar de coordenadas x y y
        apple_rect = apple.get_rect(midright = (score_rect.left,score_rect.centery))
        bg_rect = pygame.Rect(apple_rect.left,apple_rect.top,apple_rect.width + score_rect.width,apple_rect.height)

        pygame.draw.rect(screen,(167,209,61),bg_rect)
        screen.blit(score_surface,score_rect)
        screen.blit(apple,apple_rect)
        # Draw a frame around the rect
        pygame.draw.rect(screen,(56,74,12),bg_rect,2)


# Creamos un tipo de Grid en la pantalla que se constituye por celdas
cell_size = 40
cell_number = 20
screen = pygame.display.set_mode((cell_number * cell_size,cell_number * cell_size)) # Multiplicamos x el cell size para dar la ilusion que estamos sobre un grid

#Cuando cargamos una imagen va a estar en su propia superficie
apple = pygame.image.load("images/Apple.png").convert_alpha()
# Cambio de tamaño la imagen
apple = pygame.transform.smoothscale(apple,(40,40)) # Le pogno el tamaño en pixels de las celdas del grid imaginario creado


# Game Setup
pygame.init()
clock = pygame.time.Clock()


game_font = pygame.font.Font("freesansbold.ttf", 25) # pygame.font.Font(font, font_size)
# Queremos que un evento se active cada cierto tiempo
SCREEN_UPDATE = pygame.USEREVENT # Creamos un custom event
pygame.time.set_timer(SCREEN_UPDATE,150) # pygame.time.set_timer(evento que queremos que se active, cada cuantos milisegundos)

main_game = Main()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == SCREEN_UPDATE:
            main_game.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if main_game.snake.direction.y != 1:
                    main_game.snake.direction = Vector2(0,-1)
            if event.key == pygame.K_DOWN:
                if main_game.snake.direction.y != -1:
                    main_game.snake.direction = Vector2(0,1)
            if event.key == pygame.K_RIGHT:
                if main_game.snake.direction.x != -1:
                    main_game.snake.direction = Vector2(1,0)
            if event.key == pygame.K_LEFT:
                if main_game.snake.direction.x != 1:
                    main_game.snake.direction = Vector2(-1,0)

    
    screen.fill((175,215,70))
    main_game.draw_elements()
    pygame.display.flip()
    clock.tick(60)