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