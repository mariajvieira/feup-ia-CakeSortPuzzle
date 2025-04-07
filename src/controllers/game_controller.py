#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe GameController - Responsável por gerenciar a lógica do jogo e a interação
entre o modelo e a visualização.
"""

import pygame
import time  # Adicione esta importação no topo do arquivo
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
        solution_time (float): Tempo que o algoritmo levou para encontrar a solução.
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
        self.solution_time = 0  # Tempo que o algoritmo levou para encontrar a solução
    
    def start_game(self, level=1, algorithm='bfs', game_mode='ai', board_rows=3, board_cols=3, plate_count=5):
        """Inicia um novo jogo.
        
        Args:
            level (int): Nível do jogo.
            algorithm (str): Algoritmo de busca a ser utilizado.
            game_mode (str): Modo de jogo ('ai' ou 'human').
            board_rows (int): Número de linhas do tabuleiro.
            board_cols (int): Número de colunas do tabuleiro.
            plate_count (int): Quantidade de bolos disponíveis.
        """
        self.game_state = GameState(level, board_rows=board_rows, board_cols=board_cols, plate_count=plate_count)
        self.game_view = GameView(self.screen, self.game_state, self)  # Passa a referência para o controlador
        self.in_game = True
        self.selected_plate = -1
        self.algorithm = algorithm
        self.solution_path = None
        self.auto_solve = False
        self.auto_solve_step = 0
        self.solution_time = 0  # Reseta o tempo da solução
        self.game_mode = game_mode
        
        # Se estiver no modo AI, iniciar a solução automática
        if game_mode == 'ai':
            # Adicionar pequeno atraso antes de resolver para permitir que o jogo seja renderizado
            self.auto_solve_timer = 60  # Aproximadamente 1 segundo em 60 FPS
            # Definir um flag para indicar que devemos resolver após o atraso
            self.start_solving = True

    def start_game_with_state(self, game_state, algorithm='bfs', game_mode='ai'):
        """Inicia um jogo com um estado pré-carregado.
        
        Args:
            game_state (GameState): Estado do jogo pré-carregado.
            algorithm (str): Algoritmo de busca a ser utilizado.
            game_mode (str): Modo de jogo ('ai' ou 'human').
        """
        self.game_state = game_state
        self.game_view = GameView(self.screen, self.game_state, self)
        self.in_game = True
        self.selected_plate = -1
        self.algorithm = algorithm
        self.solution_path = None
        self.auto_solve = False
        self.auto_solve_step = 0
        self.solution_time = 0
        self.game_mode = game_mode
    
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
        """Resolve o jogo usando o algoritmo selecionado e mede o tempo de execução."""
        if self.game_state and not self.game_state.game_over:
            # Obtém a função do algoritmo
            algorithm_func = get_algorithm(self.algorithm)
            if algorithm_func:
                # Mede o tempo de início
                start_time = time.time()
                
                # Executa o algoritmo
                success, path = algorithm_func(self.game_state.clone())
                
                # Mede o tempo de fim e calcula a duração
                end_time = time.time()
                self.solution_time = end_time - start_time
                
                print(f"Algoritmo {self.algorithm} - Sucesso: {success}, Tamanho da solução: {len(path) if path else 0}")
                
                if success and path:
                    self.solution_path = path
                    # Registra o resultado no arquivo de log
                    self._log_algorithm_result(success, len(path))
                    return True
        return False
    
    def _log_algorithm_result(self, success, path_length):
        """Registra o resultado do algoritmo em arquivos para análise posterior."""
        import json
        import os
        from datetime import datetime
        import tracemalloc
        
        # Diretórios para resultados
        results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(results_dir, exist_ok=True)
        
        # Determina a heurística utilizada
        heuristic_name = "N/A"
        if self.algorithm in ["greedy", "astar", "wastar"]:
            heuristic_name = "combined_custom"
        
        # Dados a serem salvos
        result = {
            "algorithm": self.algorithm,
            "heuristic": heuristic_name,
            "level": self.game_state.level,
            "board_size": f"{self.game_state.board.rows}x{self.game_state.board.cols}",
            "success": success,
            "path_length": path_length if success else 0,
            "states_generated": len(self.solution_path) if success else 0,
            "execution_time": self.solution_time,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 1. Salva no arquivo JSON para análise computacional
        json_file = os.path.join(results_dir, "algorithm_results.json")
        
        if os.path.exists(json_file):
            with open(json_file, "r") as file:
                data = json.load(file)
        else:
            data = []
        
        data.append(result)
        
        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)
        
        # 2. Salva um relatório detalhado em texto para leitura humana
        self._save_detailed_report(result, results_dir)
        
        # 3. Se há uma solução, salva a sequência de movimentos
        if success and self.solution_path:
            self._save_solution_path(self.solution_path, results_dir)

    def _save_detailed_report(self, result, results_dir):
        """Salva um relatório detalhado em texto para leitura humana."""
        import os
        from datetime import datetime
        
        # Cria um nome de arquivo baseado no timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(results_dir, f"report_{result['algorithm']}_{result['level']}_{timestamp}.txt")
        
        with open(report_file, "w") as file:
            file.write("==========================================\n")
            file.write("      RELATÓRIO DE EXECUÇÃO DO ALGORITMO\n")
            file.write("==========================================\n\n")
            
            file.write(f"Data e Hora: {result['timestamp']}\n")
            file.write(f"Algoritmo: {result['algorithm'].upper()}\n")
            
            if result['heuristic'] != "N/A":
                file.write(f"Heurística: {result['heuristic']}\n")
                
            file.write(f"Nível do Jogo: {result['level']}\n")
            file.write(f"Tamanho do Tabuleiro: {result['board_size']}\n\n")
            
            file.write("RESULTADOS:\n")
            file.write(f"- Sucesso: {'Sim' if result['success'] else 'Não'}\n")
            
            if result['success']:
                file.write(f"- Comprimento do Caminho: {result['path_length']} movimentos\n")
                file.write(f"- Estados Gerados: {result['states_generated']}\n")
                
            file.write(f"- Tempo de Execução: {result['execution_time']:.6f} segundos\n\n")
            
            file.write("ESTATÍSTICAS DO JOGO:\n")
            file.write(f"- Pontuação Final: {self.game_state.score}\n")
            file.write(f"- Pratos Utilizados: {self.game_state.avl_plates.plates_used}/{self.game_state.avl_plates.total_plate_limit}\n")
            file.write(f"- Tabuleiro Final: {self.game_state.board.count_occupied_cells()}/{self.game_state.board.rows * self.game_state.board.cols} células\n\n")
            
            file.write("==========================================\n")
            file.write("Fim do Relatório\n")

    def _save_solution_path(self, solution_path, results_dir):
        """Salva a sequência de movimentos da solução em um arquivo de texto."""
        import os
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path_file = os.path.join(results_dir, f"solution_{self.algorithm}_{self.game_state.level}_{timestamp}.txt")
        
        with open(path_file, "w") as file:
            file.write(f"SOLUÇÃO DO ALGORITMO {self.algorithm.upper()} - NÍVEL {self.game_state.level}\n")
            file.write(f"Gerada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write(f"Comprimento do Caminho: {len(solution_path)} movimentos\n\n")
            file.write("SEQUÊNCIA DE MOVIMENTOS:\n")
            
            for i, move in enumerate(solution_path):
                x, y, plate_index = move
                file.write(f"Passo {i+1}: Colocar prato {plate_index} na posição ({x},{y})\n")
    
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
        if not self.solution_path or self.auto_solve_step >= len(self.solution_path):
            # Não há mais passos na solução ou solução vazia
            self.auto_solve = False
            return
            
        # Obtém a ação do caminho da solução
        action = self.solution_path[self.auto_solve_step]
        x, y, plate_index = action
        
        # Verifica se o índice do prato está dentro dos limites
        if plate_index >= len(self.game_state.avl_plates.visible_plates):
            # Debug para entender melhor o problema
            print(f"Esperando prato {plate_index}, mas só temos {len(self.game_state.avl_plates.visible_plates)} disponíveis")
            # Tentaremos novamente no próximo ciclo
            return
        
        # Executa a ação
        self.selected_plate = plate_index
        success, animation_info = self.game_state.place_plate(x, y, plate_index)
        
        if success:
            print(f"Passo {self.auto_solve_step+1}/{len(self.solution_path)}: Prato {plate_index} colocado em ({x},{y})")
            # Resto do código para animações...
            
            # Avança para o próximo passo SOMENTE se a ação foi bem-sucedida
            self.auto_solve_step += 1
        else:
            print(f"Falha ao colocar prato {plate_index} em ({x},{y})")
            self.selected_plate = -1
        
        # Se chegou ao fim da solução, desativa o auto-solve
        if self.auto_solve_step >= len(self.solution_path):
            self.auto_solve = False
    
    def set_algorithm(self, algorithm):
        """Define o algoritmo de busca a ser utilizado.
        
        Args:
            algorithm (str): Nome do algoritmo ('bfs', 'dfs', 'ids', 'ucs').
        """
        self.algorithm = algorithm
        self.solution_path = None  # Limpa a solução anterior
        self.auto_solve = False