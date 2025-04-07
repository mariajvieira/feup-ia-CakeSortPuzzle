import pygame
import time 
from src.models.game_state import GameState
from src.views.game_view import GameView
from src.algorithms.search_algorithms import get_algorithm


class GameController:
    def __init__(self, screen):
        self.screen = screen
        self.game_state = None
        self.game_view = None
        self.in_game = False
        self.selected_plate = -1
        self.algorithm = 'bfs'
        self.solution_path = None
        self.auto_solve = False
        self.auto_solve_step = 0
        self.auto_solve_timer = 0
        self.solution_time = 0

    def start_game(self, level=1, algorithm='bfs', game_mode='ai', board_rows=2, board_cols=2, plate_count=6):
        self.game_state = GameState(level, board_rows=board_rows, board_cols=board_cols, plate_count=plate_count)
        self.game_view = GameView(self.screen, self.game_state, self)
        self.in_game = True
        self.selected_plate = -1
        self.algorithm = algorithm
        self.solution_path = None
        self.auto_solve = False
        self.auto_solve_step = 0
        self.solution_time = 0
        self.game_mode = game_mode

        if game_mode == 'ai':
            self.auto_solve_timer = 60
            self.start_solving = True

    def start_game_with_state(self, game_state, algorithm='bfs', game_mode='ai'):
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
        self.in_game = False
        self.game_state = None
        self.game_view = None

    def is_in_game(self):
        return self.in_game

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.end_game()
            elif event.key == pygame.K_s:
                self.solve_game()
            elif event.key == pygame.K_a:
                self.toggle_auto_solve()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                self._handle_mouse_click(event.pos)

    def _handle_mouse_click(self, pos):

        if self.game_state.game_over:
            return

        if self.game_mode == 'ai':
            if not self.auto_solve and not self.solution_path:
                self.solve_game()
                self.toggle_auto_solve()
            return

        plate_index = self.game_view.get_plate_at_pos(pos)
        if plate_index != -1:
            self.selected_plate = plate_index
            return

        if self.selected_plate != -1:
            board_pos = self.game_view.get_board_pos_at_pos(pos)
            if board_pos is not None:
                x, y = board_pos
                previous_score = self.game_state.score

                success, animation_info = self.game_state.place_plate(x, y, self.selected_plate)
                if success:
                    self.selected_plate = -1

                    for movement in animation_info.get('slice_movements', []):
                        source_x, source_y, target_x, target_y, slice_type, count = movement
                        for _ in range(count):
                            self.game_view.add_slice_movement_animation(source_x, source_y, target_x, target_y, slice_type)

                    for _ in range(animation_info.get('completed_cakes', 0)):
                        for cake_x, cake_y in animation_info.get('cake_positions', [(x, y)]):
                            self.game_view.add_cake_complete_animation(cake_x, cake_y)

    def update(self):
        if self.game_mode == 'ai' and hasattr(self, 'start_solving') and self.start_solving:
            self.auto_solve_timer -= 1
            if self.auto_solve_timer <= 0:
                self.solve_game()
                self.toggle_auto_solve()
                self.start_solving = False

        if self.auto_solve and self.solution_path and not self.game_state.game_over:
            self.auto_solve_timer += 1
            if self.auto_solve_timer >= 30:
                self.auto_solve_timer = 0
                self._execute_solution_step()

    def render(self):
        if self.game_view:
            self.game_view.render(self.selected_plate)

    def solve_game(self):
        if self.game_state and not self.game_state.game_over:
            algorithm_func = get_algorithm(self.algorithm)
            if algorithm_func:
                start_time = time.time()

                success, path = algorithm_func(self.game_state.clone())

                end_time = time.time()
                self.solution_time = end_time - start_time

                print(f"Algoritmo {self.algorithm} - Sucesso: {success}, Tamanho da solução: {len(path) if path else 0}")

                if success and path:
                    self.solution_path = path
                    self._log_algorithm_result(success, len(path))
                    return True
        return False

    def _log_algorithm_result(self, success, path_length):
        import json
        import os
        from datetime import datetime
        import tracemalloc

        results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(results_dir, exist_ok=True)

        heuristic_name = "N/A"
        if self.algorithm in ["greedy", "astar", "wastar"]:
            heuristic_name = "combined_custom"

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

        json_file = os.path.join(results_dir, "algorithm_results.json")

        if os.path.exists(json_file):
            with open(json_file, "r") as file:
                data = json.load(file)
        else:
            data = []

        data.append(result)

        with open(json_file, "w") as file:
            json.dump(data, file, indent=4)

        self._save_detailed_report(result, results_dir)

        if success and self.solution_path:
            self._save_solution_path(self.solution_path, results_dir)

    def _save_detailed_report(self, result, results_dir):
        import os
        from datetime import datetime

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

            file.write(f"Tamanho do Tabuleiro: {result['board_size']}\n\n")

            file.write("RESULTADOS:\n")
            file.write(f"- Sucesso: {'Sim' if result['success'] else 'Não'}\n")

            if result['success']:
                file.write(f"- Comprimento do Caminho: {result['path_length']} movimentos\n")
                file.write(f"- Estados Gerados: {result['states_generated']}\n")

            file.write(f"- Tempo de Execução: {result['execution_time']:.6f} segundos\n\n")

            file.write("ESTATÍSTICAS DO JOGO:\n")
            file.write(f"- Total de bolos concluídos: {self.game_state.score}\n")
            file.write(f"- Pratos Utilizados: {self.game_state.avl_plates.plates_used}/{self.game_state.avl_plates.total_plate_limit}\n")
            file.write(f"- Tabuleiro Final: {self.game_state.board.count_occupied_cells()}/{self.game_state.board.rows * self.game_state.board.cols} células\n\n")

            file.write("==========================================\n")
            file.write("Fim do Relatório\n")

    def _save_solution_path(self, solution_path, results_dir):
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
        if not self.solution_path:
            if self.solve_game():
                self.auto_solve = True
                self.auto_solve_step = 0
        else:
            self.auto_solve = not self.auto_solve
            if self.auto_solve:
                self.auto_solve_step = 0
    
    def _execute_solution_step(self):
        if not self.solution_path or self.auto_solve_step >= len(self.solution_path):
            self.auto_solve = False
            return
            
        action = self.solution_path[self.auto_solve_step]
        x, y, plate_index = action
        
        if plate_index >= len(self.game_state.avl_plates.visible_plates):
            print(f"Esperando prato {plate_index}, mas só temos {len(self.game_state.avl_plates.visible_plates)} disponíveis")
            return
        
        self.selected_plate = plate_index
        success, animation_info = self.game_state.place_plate(x, y, plate_index)
        
        if success:
            print(f"Passo {self.auto_solve_step+1}/{len(self.solution_path)}: Prato {plate_index} colocado em ({x},{y})")
            self.auto_solve_step += 1
        else:
            print(f"Falha ao colocar prato {plate_index} em ({x},{y})")
            self.selected_plate = -1
        
        if self.auto_solve_step >= len(self.solution_path):
            self.auto_solve = False
    
    def set_algorithm(self, algorithm):
        self.algorithm = algorithm
        self.solution_path = None  
        self.auto_solve = False