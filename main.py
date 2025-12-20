import pygame
pygame.init()
pygame.font.init()
pygame.display.set_caption("The Binding of Python")
screen = pygame.display.set_mode([1280, 720])
menu_font = pygame.font.SysFont('Arial', 30);
scene = 0
running = True
pygame.time.Clock().tick(60)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if scene == 0:
        
        screen.fill((255, 255, 255))
        start_button = menu_font.render("Start", True, (0, 0, 0))

        screen.blit(start_button, (10, 10))

        quit_button = menu_font.render("Quit", True, (0, 0, 0))
        screen.blit(quit_button, (10, 50))
    pygame.display.flip()
pygame.quit()
