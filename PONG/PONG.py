import pygame, sys, random


## Pasos para crear un juego:
# 1. Definir los objetos (crear las dimensiones, coordenadas del objeto)
# 2. Animar los objetos (le indica a pygame que mueva las coordenadas del objeto cada ciclo en el loop while)
# 3. Dibujar en pantalla los objetos en la superficie

### Defino una funcion de la animacion de la bola antes, para que en el codigo del loop se vea mas limpio
def ball_animation():
    ## Para animar un objeto, es el paso que esta entre: Definir el objeto y dibujar el objeto (modificar las coordenadas del objeto y luego dibujarlo)

    # Para definir la velocidad en la que se va a mover la bola
    # cambio los atributos del objeto bola creado (rect) con: objeto.x y objeto.y e incremento sus coordenadas
    # para darle la sensacion de que se esta moviendo

    # Para arreglar el error de la declaracion de variables locales 
    # Nos daba error porque estabamos tratando de actualizar una variable que todavia no esta inicializada
    global ball_speed_x, ball_speed_y, score_time, player_score, opponent_score
    ball.x += ball_speed_x
    ball.y += ball_speed_y

    # Programo la logica de colisiones de los bordes de la pantalla
    # If statements para cada axis
    # objeto (Rect)
    # Rect.top (coordeandas de la parte de arriba del objeto)
    # Recto.bottom (coordenadas de la parte de abajo del objeto)
    if ball.top <= 0 or ball.bottom >= screen_height:
        ball_speed_y *= -1
    # Rect.right (coordenadas de la parte derecha del objeto)
    # Rect.left (coordenadas de la parte izquierda del objeto)
    if ball.left <= 0:
        pygame.mixer.Sound.play(score_sound)
        player_score += 1
        score_time = pygame.time.get_ticks() # Nos va a dar un entero que indica por cuanto tiempo pygame.init() ha estado corriendo
    if ball.right >= screen_width:
        pygame.mixer.Sound.play(score_sound)
        opponent_score += 1
        score_time = pygame.time.get_ticks()

    ### Colisiones entre objeto Rect
    # rect1.colliderect(rect2) - retorna un dato booleano
    # si colisionan retorna True
    # si no colisionan retorna False

    if ball.colliderect(player) and ball_speed_x > 0:
        pygame.mixer.Sound.play(pong_sound)
        if abs(ball.right - player.left) < 10:
            ball_speed_x *= -1
        elif abs(ball.bottom - player.top) < 10 and ball_speed_y > 0:
            ball_speed_y *= -1
        elif abs(ball.top - player.bottom) < 10 and ball_speed_y < 0:
            ball_speed_y *= -1
    if ball.colliderect(opponent) and ball_speed_x < 0:
        pygame.mixer.Sound.play(pong_sound)
        if abs(ball.left - opponent.right) < 10:
            ball_speed_x *= -1
        elif abs(ball.bottom - opponent.top) < 10 and ball_speed_y > 0:
            ball_speed_y *= -1
        elif abs(ball.top - opponent.bottom) < 10 and ball_speed_y < 0:
            ball_speed_y *= -1


def ball_restart():
    global ball_speed_x, ball_speed_y,score_time

    current_time = pygame.time.get_ticks()
    #Teleport the ball
    ball.center = (screen_width/2,screen_height / 2)
    if current_time - score_time < 700:
        number_three = game_font.render("3",True,light_grey)
        screen.blit(number_three,(screen_width/2 -10,screen_height/2 +20))
    if 700 < current_time - score_time < 1400:
        number_two = game_font.render("2",True,light_grey)
        screen.blit(number_two,(screen_width/2 -10,screen_height/2 +20))
    if 1400 < current_time - score_time < 2100:
        number_one = game_font.render("1",True,light_grey)
        screen.blit(number_one,(screen_width/2 -10,screen_height/2 +20))

    if current_time - score_time < 2100:
        ball_speed_x, ball_speed_y = 0,0
    else:
        # La direccion de la bola se va a multiplicar por 1 o menos 1
        ball_speed_y = 7 * random.choice((1,-1))
        ball_speed_x =  7 * random.choice((1,-1))
        score_time = None
    
    
# General Setup

# Para que no haya delay cuando se reproduzca un sonido
pygame.mixer.pre_init(44100,-16,2,512)
pygame.init() # Para inicializar pygame - es necesario siempre
clock = pygame.time.Clock()


# Setting up the main window of the game

screen_width = 1280
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption("Pong") # Darle un titulo a la ventana

# Game Rectangle
# pygame.Rect(x,y,width,height)
ball = pygame.Rect(screen_width / 2 -15,screen_height / 2 -15,30,30)
player = pygame.Rect(screen_width - 10,screen_height/2 -70,10,120)
opponent = pygame.Rect(10,screen_height/2 -70,10,120)

## Game Variables

# para mover la bola
# defino 2 variables de velocidad en x y y
# Multiplico por 1 o -1 para variar la direccion en donde empieza la bola
ball_speed_x = 7 * random.choice((1,-1))
ball_speed_y = 7 * random.choice((1,-1))

player_speed = 0
opponent_speed = 7

bg_color = pygame.Color("grey12")
light_grey = (200,200,200)

## Text Variables
# 3 pasos:
# 1. Create a font and font size
# 2. Write text on a new surface
# 3. Put the text surface on the main surface

# Creamos variables para alojar el marcador
player_score = 0
opponent_score = 0
# creamos el font
game_font = pygame.font.Font("freesansbold.ttf",32) # ("nombre de la font", size)


# Score Timer
score_time = None

## Sound
pong_sound = pygame.mixer.Sound("images/pong.ogg")
score_sound = pygame.mixer.Sound("images/score.ogg")

# Ingresamos al loop
# El while loop refresca las imagenes (fps) 
while True:

    # Verifica los eventos que el usuario realiza
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                player_speed += 7
                
            if event.key == pygame.K_UP:
                player_speed -= 7
                

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN:
                player_speed -= 7
                
            if event.key == pygame.K_UP:
                player_speed += 7
                

    ## Llamo la funcion que hace mover los objetos
    ball_animation()
    player.y += player_speed

    # Para que el jugador no se salga de los bordes de las pontallas
    if player.top <= 0:
        player.top = 0
    if player.bottom >= screen_height:
        player.bottom = screen_height

    # Oponente (AI)
    # Se va moviendo dependiendo de donde se va dirigiendo la bola
    if opponent.top < ball.y:
        opponent.top += opponent_speed
    if opponent.bottom > ball.y:
        opponent.bottom -= opponent_speed

    if opponent.top <= 0:
        opponent.top = 0
    if opponent.bottom >= screen_height:
        opponent.bottom = screen_height
    
    ### OJO - LOS ELEMENTOS PUESTOS AL PRINCIPIO DEL CODIGO SON LOS QUE VAN AL ULTIMO Y LOS ULTIMOS EN SER DIBUJADOS VAN AL PRINCIPIO

    # Visuals - dibujar los rectangulos
    # Sin rellenar el fondo, no nos va a permitir actualizar la ventana y los elementos, ya que se podra ver el frame anterior
    screen.fill(bg_color)
    # pygame.draw.rect(supercicie donde dibujar, color, rect object)
    pygame.draw.rect(screen,light_grey,player)
    pygame.draw.rect(screen,light_grey,opponent)
    #Dibujar la bola
    pygame.draw.ellipse(screen,light_grey,ball)
    #Linea que separa los dos lados
    pygame.draw.aaline(screen,light_grey,(screen_width/2,0), (screen_width/2,screen_height))

    # Creamos la logica para que se resetee la bola cada vez que metan punto y haya un tiempo de preparacion
    if score_time: # Cualquier valor que tome el score time va a validar el if
        ball_restart()

    # Creamos la superficie donde va a estar el texto
    player_text = game_font.render(f"{player_score}",True,light_grey) # Font_object.render(texto,antialiased,color)
    opponent_text = game_font.render(f"{opponent_score}",True,light_grey)
    # Para colocar una superficie encima de otra
    screen.blit(player_text,(660,470))
    screen.blit(opponent_text,(600,470))
    # Para actualizar la pantalla
    pygame.display.flip() # Toma todo lo que esta antes y plasma una imagen respecto a eso
    clock.tick(60) # Limita los FPS