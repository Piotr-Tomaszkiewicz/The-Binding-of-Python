import pygame
pygame.init()
pygame.font.init()
pygame.display.set_caption("The Binding of Python")
screen = pygame.display.set_mode([1280, 720])
scene = 0
running = True
pygame.time.Clock().tick(60)
def draw_button(button_color, button_rect, button_text, font, text_color):
    pygame.draw.rect(screen, button_color, button_rect, border_radius=10)
    

    pygame.draw.rect(screen, (0, 100, 0), button_rect, 3, border_radius=10)
    

    text_surf = font.render(button_text, True, text_color)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if scene == 0:
        menu_font = pygame.font.SysFont('Arial', 30);
        screen.fill((255, 255, 255))
        start_button = menu_font.render("Start", True, (0, 0, 0))

        screen.blit(start_button, (10, 10))

        quit_button = menu_font.render("Quit", True, (0, 0, 0))
        screen.blit(quit_button, (10, 50))
    pygame.display.flip()
pygame.quit()
