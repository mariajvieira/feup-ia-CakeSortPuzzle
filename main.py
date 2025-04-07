import pygame
import sys
from src.controllers.game_controller import GameController
from src.views.menu_view import MenuView


def main():
    pygame.init()
    pygame.display.set_caption("Cake Sorting Puzzle")
    
    info = pygame.display.Info()
    screen_width = info.current_w
    screen_height = info.current_h
    screen = pygame.display.set_mode((screen_width, screen_height),pygame.FULLSCREEN)
    
    game_controller = GameController(screen)
    
    menu_view = MenuView(screen, game_controller)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_controller.is_in_game():
                game_controller.handle_event(event)
            else:
                menu_view.handle_event(event)
        
        if game_controller.is_in_game():
            game_controller.update()
            game_controller.render()
        else:
            menu_view.render()
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()