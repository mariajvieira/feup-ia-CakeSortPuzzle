#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe GameController - Responsável por gerenciar a lógica do jogo e a interação
entre o modelo e a visualização.
"""

import pygame
from src.models.game_state import GameState
from src.views.game_view import GameView
from src.algorithms.search_algorithms import get_algorithm


class GameController:
    """Controlador principal do jogo.
    
    Attributes:
        screen (pygame.Surface): Superfície de renderização do jogo.
        game_state (GameState): Estado atual do jogo.
        game_view (GameView): Visualização do jogo.
        in_game (bool): Indica se o jogo está em execução.
        selected_plate (int): Índice do prato selecionado.
        algorithm (str): Algoritmo de busca selecionado.
        solution_path (list): Caminho da solução encontrado pelo algoritmo.
        auto_solve (bool): Indica se o modo de solução automática está ativado.
        auto_solve_step (int): Passo atual na solução automática.
    """
    
    def __init__(self, screen):
        """Inicializa o controlador do jogo.
        
        Args:
            screen (pygame.Surface): Superfície de renderização do jogo.
        """
        self.screen = screen
        self.game_state = None
        self.game_view = None
        self.in_game = False
        self.selected_plate = -1
        self.algorithm = 'bfs'  # Algoritmo padrão
        self.solution_path = None
        self.auto_solve = False
        self.auto_solve_step = 0
        self.auto_solve_timer = 0
    
    def start_game(self, level=1, algorithm='bfs', game_mode='ai'):
        """Inicia um novo jogo.
        
        Args:
            level (int): Nível do jogo.
            algorithm (str): Algoritmo de busca a ser utilizado.
            game_mode (str): Modo de jogo ('ai' ou 'human').
        """
        self.game_state = GameState(level)
        self.game_view = GameView(self.screen, self.game_state)
        self.in_game = True
        self.selected_plate = -1
        self.algorithm = algorithm
        self.solution_path = None
        self.auto_solve = False
        self.auto_solve_step = 0
        self.game_mode = game_mode
        
        # Se estiver no modo AI, iniciar a solução automática
        if game_mode == 'ai':
            # Adicionar pequeno atraso antes de resolver para permitir que o jogo seja renderizado
            self.auto_solve_timer = 60  # Aproximadamente 1 segundo em 60 FPS
            # Definir um flag para indicar que devemos resolver após o atraso
            self.start_solving = True
    
    def end_game(self):
        """Encerra o jogo atual e retorna ao menu."""
        self.in_game = False
        self.game_state = None
        self.game_view = None
    
    def is_in_game(self):
        """Verifica se o jogo está em execução.
        
        Returns:
            bool: True se o jogo está em execução, False caso contrário.
        """
        return self.in_game
    
    def handle_event(self, event):
        """Trata os eventos do jogo.
        
        Args:
            event (pygame.event.Event): Evento a ser tratado.
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.end_game()
            elif event.key == pygame.K_s:
                self.solve_game()
            elif event.key == pygame.K_a:
                self.toggle_auto_solve()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo do mouse
                self._handle_mouse_click(event.pos)
    
    def _handle_mouse_click(self, pos):
        """Trata os cliques do mouse.
        
        Args:
            pos (tuple): Posição (x, y) do clique.
        """
        # Verifica se o jogo acabou
        if self.game_state.game_over:
            return
        
        # No modo AI, não permitir interação manual com o tabuleiro
        if self.game_mode == 'ai':
            # Opcionalmente, iniciar a solução automática se ainda não estiver ativa
            if not self.auto_solve and not self.solution_path:
                self.solve_game()
                self.toggle_auto_solve()
            return
        
        # Código existente para modo humano
        # Verifica se clicou em um prato disponível
        plate_index = self.game_view.get_plate_at_pos(pos)
        if plate_index != -1:
            self.selected_plate = plate_index
            return
        
        # Verifica se clicou no tabuleiro e tem um prato selecionado
        if self.selected_plate != -1:
            board_pos = self.game_view.get_board_pos_at_pos(pos)
            if board_pos is not None:
                x, y = board_pos
                # Guarda o estado anterior para verificar se houve bolos completos
                previous_score = self.game_state.score
                
                # Tenta colocar o prato no tabuleiro
                success, animation_info = self.game_state.place_plate(x, y, self.selected_plate)
                if success:
                    self.selected_plate = -1
                    
                    # Processa as animações de movimento de fatias
                    for movement in animation_info.get('slice_movements', []):
                        source_x, source_y, target_x, target_y, slice_type, count = movement
                        # Cria uma animação para cada fatia movida
                        for _ in range(count):
                            self.game_view.add_slice_movement_animation(source_x, source_y, target_x, target_y, slice_type)
                    
                    # Adiciona animações para bolos completos
                    for _ in range(animation_info.get('completed_cakes', 0)):
                        for cake_x, cake_y in animation_info.get('cake_positions', [(x, y)]):
                            self.game_view.add_cake_complete_animation(cake_x, cake_y)
    
    def update(self):
        """Atualiza o estado do jogo."""
        # Se estiver no modo AI e precisar iniciar a solução após o atraso
        if self.game_mode == 'ai' and hasattr(self, 'start_solving') and self.start_solving:
            self.auto_solve_timer -= 1
            if self.auto_solve_timer <= 0:
                self.solve_game()
                self.toggle_auto_solve()
                self.start_solving = False
                
        # Código existente para auto-solving    
        if self.auto_solve and self.solution_path and not self.game_state.game_over:
            # Atualiza o temporizador para a solução automática
            self.auto_solve_timer += 1
            if self.auto_solve_timer >= 30:  # Executa um passo a cada 30 frames (0.5 segundos)
                self.auto_solve_timer = 0
                self._execute_solution_step()
    
    def render(self):
        """Renderiza o jogo na tela."""
        if self.game_view:
            self.game_view.render(self.selected_plate)
    
    def solve_game(self):
        """Resolve o jogo usando o algoritmo selecionado."""
        if self.game_state and not self.game_state.game_over:
            # Obtém a função do algoritmo
            algorithm_func = get_algorithm(self.algorithm)
            if algorithm_func:
                # Executa o algoritmo
                success, path = algorithm_func(self.game_state.clone())
                if success:
                    self.solution_path = path
                    return True
        return False
    
    def toggle_auto_solve(self):
        """Ativa/desativa a solução automática."""
        if not self.solution_path:
            if self.solve_game():
                self.auto_solve = True
                self.auto_solve_step = 0
        else:
            self.auto_solve = not self.auto_solve
            if self.auto_solve:
                self.auto_solve_step = 0
    
    def _execute_solution_step(self):
        """Executa um passo da solução automática."""
        if self.auto_solve_step < len(self.solution_path):
            # Obtém a ação do caminho da solução
            action = self.solution_path[self.auto_solve_step]
            x, y, plate_index = action
            
            # No novo sistema, plate_index deve estar dentro dos pratos visíveis disponíveis
            # Se não houver pratos visíveis suficientes, espere até o próximo passo
            if plate_index >= len(self.game_state.avl_plates.visible_plates):
                # Aguarde até que haja pratos suficientes
                return
            
            # Executa a ação
            self.selected_plate = plate_index
            self.game_state.place_plate(x, y, plate_index)
            self.selected_plate = -1
            
            # Avança para o próximo passo
            self.auto_solve_step += 1
        else:
            # Chegou ao fim da solução
            self.auto_solve = False
    
    def set_algorithm(self, algorithm):
        """Define o algoritmo de busca a ser utilizado.
        
        Args:
            algorithm (str): Nome do algoritmo ('bfs', 'dfs', 'ids', 'ucs').
        """
        self.algorithm = algorithm
        self.solution_path = None  # Limpa a solução anterior
        self.auto_solve = False