import pygame, sys, boton, csv, pickle

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

pygame.init()

# Game Window
screen_width = 800
screen_height = 640
lower_margin = 100
side_margin = 300

screen = pygame.display.set_mode((screen_width + side_margin, screen_height + lower_margin))
pygame.display.set_caption("Level Editor")

# Define game variables
ROWS = 16
COLUMNS = 150
TILE_SIZE = screen_height // ROWS
scroll_left = False
scroll_right = False
level = 0
TILE_TYPES = 21
scroll = 0
scroll_speed = 1
FPS = 60
clock = pygame.time.Clock()
current_tile = 0

# Load Images
pine1_img = pygame.image.load("images/Background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("images/Background/pine2.png").convert_alpha()
sky_img = pygame.image.load("images/Background/sky_cloud.png").convert_alpha()
mountain_img = pygame.image.load("images/Background/mountain.png").convert_alpha()

# Store tiles in a list
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f"tile/{x}.png")
    img = pygame.transform.scale(img,(TILE_SIZE, TILE_SIZE))
    img_list.append(img)

save_image = pygame.image.load("tile/save_btn.png").convert_alpha()
load_image = pygame.image.load("tile/load_btn.png").convert_alpha()

# Define Colors
GREEN = (144,201,120)
WHITE = (255,255,255)
RED = (200,25,25)

# Define Font
font = pygame.font.SysFont("Futura",30)

# Create empty tile list
# world_data = []
# for row in range(ROWS):
#     r = [-1] * COLUMNS # Lista que contiene 150 -1s
#     world_data.append(r)

world_data = [[-1 for x in range(151)] for x in range(ROWS)]

# Create Ground
for tile in range(0, COLUMNS):
    world_data[ROWS -1][tile] = 0 # Cambio toda la ultima fila por puros 0

### Functions
## Cada vez que uso screen.blit(), tengo que ir agregando -scroll en las coordenadas para que se genere la ilusion de que se esta moviendo
## Asi cada imagen que pongamos en el la screen tiene le ilusion de que se esta moviendo

#Load backgrounds
def draw_bg():
    screen.fill(GREEN)
    width = sky_img.get_width()
    # Imagenes pegadas una detras de otra en una secuencia
    for x in range(4):
        screen.blit(sky_img,((x * width) -scroll * 0.5, 0))
        screen.blit(mountain_img,((x * width) -scroll * 0.6, screen_height - mountain_img.get_height() - 300))
        screen.blit(pine1_img,((x * width) -scroll * 0.7, screen_height - pine1_img.get_height() - 150))
        screen.blit(pine2_img,((x * width) -scroll * 0.8, screen_height - pine2_img.get_height()))

# Draw grid
def draw_grid():
    # Vertical lines
    for c in range(COLUMNS + 1):
        pygame.draw.line(screen, WHITE, (c * TILE_SIZE -scroll, 0), (c * TILE_SIZE - scroll, screen_height)) # line(surface, color, start_pos, end_pos, width) -> Rect
    # Horizontal Lines
    for c in range(ROWS + 1):
        pygame.draw.line(screen, WHITE, (0, c * TILE_SIZE), (screen_width, c * TILE_SIZE))

# Draw the world tiles
def draw_world():
    
    for y, row in enumerate(world_data):
        for x, tile in enumerate(row):
            if tile >= 0:
                screen.blit(img_list[tile], (x * TILE_SIZE -scroll, y * TILE_SIZE))

# Outputting text
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x,y))

# Create Buttons
save_button = Button(screen_width // 2, screen_height + lower_margin - 50, save_image)
load_button = Button(screen_width // 2 + 200, screen_height + lower_margin - 50, load_image)

# Make a button list
button_list = []
button_col = 0 
button_row = 0
for i in range(len(img_list)):
    tile_button = Button(screen_width + (75 * button_col) + 50, 75 * button_row + 50, img_list[i])
    button_list.append(tile_button)
    button_col += 1
    if button_col == 3:
        button_row += 1
        button_col = 0


run = True

while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                scroll_left = True
            if event.key == pygame.K_RIGHT:
                scroll_right = True
            if event.key == pygame.K_UP:
                level += 1
            if event.key == pygame.K_DOWN and level > 0:
                level -= 1
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 5
            

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                scroll_left = False
            if event.key == pygame.K_RIGHT:
                scroll_right = False
            if event.key == pygame.K_RSHIFT:
                scroll_speed = 1

    draw_bg()
    draw_grid()
    draw_world()

    # TEXT
    draw_text(f"Level: {level}", font, WHITE, 10, screen_height + lower_margin - 90)
    draw_text("Press UP or DOWN to change level", font, WHITE, 10, screen_height + lower_margin - 60)

    # Save and load data
    if save_button.draw():
        ### Save level data
        ## CSV METHOD
        # with open(f"level{level}_data.csv","w", newline = "") as csvfile:
        #     writer = csv.writer(csvfile, delimiter = ",")
        #     for row in world_data:
        #         writer.writerow(row)

        ## Using the pickle module
        pickle_out = open(f"level{level}_data", "wb")
        pickle.dump(world_data, pickle_out)
        pickle_out.close()
    
    if load_button.draw():
        ### Load Level Data
        # Reset scroll back to star of level
        scroll = 0
        world_data = 0
        ## CSV METHOD
        # with open(f"level{level}_data.csv", newline = "") as csvfile:
        #     reader = csv.reader(csvfile, delimiter = ",")
        #     for x,row in enumerate(reader):
        #         for y, tile in enumerate(row):
        #             world_data[x][y] = int(tile)
        
        ## Using the pickel module
        picke_in = open(f"level{level}_data", "rb")
        world_data = pickle.load(picke_in)


    # Draw tile panel and tiles
    pygame.draw.rect(screen, GREEN, (screen_width,0, side_margin, screen_height))

    # Choose a tile
    button_count = 0
    for count,i in enumerate(button_list):
        if i.draw():
            current_tile = count

    # Higlight selected tile
    pygame.draw.rect(screen, RED, button_list[current_tile].rect, 3)

    # Scroll the map
    if scroll_left and scroll > 0:
        scroll -= 5 * scroll_speed
        if scroll < 0:
            scroll = 0
    if scroll_right and scroll < (COLUMNS * TILE_SIZE) -screen_width:
        scroll += 5 * scroll_speed

    # Add new tiles to the screen
    # 1. Get mouse position
    pos = pygame.mouse.get_pos()
    # 2. Convert to grid positions
    x = (pos[0] + scroll) // TILE_SIZE
    y = pos[1] // TILE_SIZE

    # Check that the coordinates are whithin the tile area
    if pos[0] < screen_width and pos[1] < screen_height:
        #Update tile value
        if pygame.mouse.get_pressed()[0] == 1:
            if world_data[y][x] != current_tile:
                world_data[y][x] = current_tile
        if pygame.mouse.get_pressed()[2] == 1:
            world_data[y][x] = -1


    pygame.display.update()
    clock.tick(FPS)