#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cake Sorting Puzzle - Jogo de puzzle onde o objetivo é organizar fatias de bolo
para formar bolos completos.

Desenvolvido como parte do projeto de Inteligência Artificial.
"""

import pygame
import sys
from src.controllers.game_controller import GameController
from src.views.menu_view import MenuView


def main():
    """Função principal que inicializa o jogo."""
    # Inicializa o pygame
    pygame.init()
    pygame.display.set_caption("Cake Sorting Puzzle")
    
    # Configurações da tela
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    
    # Inicializa o controlador do jogo
    game_controller = GameController(screen)
    
    # Inicializa o menu
    menu_view = MenuView(screen, game_controller)
    
    # Loop principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Passa os eventos para o controlador atual
            if game_controller.is_in_game():
                game_controller.handle_event(event)
            else:
                menu_view.handle_event(event)
        
        # Atualiza e renderiza
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