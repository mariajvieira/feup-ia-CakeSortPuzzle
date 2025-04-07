from src.models.board import Board
from src.models.avl_plates import AvailablePlates


class GameState:
    
    def __init__(self, level=1, board_rows=None, board_cols=None, plate_count=None):
        self.level = level
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.win = False
        
        if board_rows is None or board_cols is None:
            board_size = self._get_board_size(level)
            board_rows = board_rows or board_size[0]
            board_cols = board_cols or board_size[1]
        
        self.board = Board(board_rows, board_cols)
        
        self.avl_plates = AvailablePlates(level, plate_count)
        
        self.target_score = None  
    
    def _get_board_size(self, level):
        sizes = {
            1: (2, 2),  # Nível 1: 3x3 (era 4x4)
            2: (3, 4),  # Nível 2: 3x4 (era 4x5)
            3: (4, 4),  # Nível 3: 4x4 (era 5x5)
            4: (4, 5),  # Nível 4: 4x5 (era 5x6)
            5: (5, 5)   # Nível 5: 5x5 (era 6x6)
        }
        
        return sizes.get(level, sizes[max(sizes.keys())])
    
    def place_plate(self, x, y, plate_index):
        if not self.board.is_empty(x, y):
            return False, {}
        
        plate = self.avl_plates.get_plate(plate_index)
        if plate is None:
            return False, {}
        
        success = self.board.place_plate(x, y, plate)
        if success:
            self.avl_plates.remove_plate(plate_index)
            
            self.moves += 1
            
            animation_info = {
                'slice_movements': [],
                'completed_cakes': 0,
                'cake_positions': []
            }
            
            slice_movements = self._check_adjacent_plates(x, y)
            animation_info['slice_movements'] = slice_movements
            
            completed_cakes = self.board.check_completed_cakes()
            if completed_cakes > 0:
                self.score += completed_cakes
                animation_info['completed_cakes'] = completed_cakes
                animation_info['cake_positions'] = [(x, y)]  
            
            if self.avl_plates.is_exhausted():
                self.win = True
                self.game_over = True
            
            if self.board.is_full() and not self.avl_plates.is_exhausted():
                self.game_over = True
                self.win = False
            
            if not self.avl_plates.has_plates() and not self.win:
                self.game_over = True
            
            return True, animation_info
        
        return False, {}
    
    def _check_adjacent_plates(self, x, y):
        adjacent_positions = [
            (x-1, y), (x+1, y), (x, y-1), (x, y+1)  # Esquerda, Direita, Cima, Baixo
        ]
        
        all_movements = []
        
        for adj_x, adj_y in adjacent_positions:
            if self.board.is_valid_position(adj_x, adj_y) and not self.board.is_empty(adj_x, adj_y):
                _, movements = self.board.optimize_plates(x, y, adj_x, adj_y)
                all_movements.extend(movements)
                
        return all_movements
    
    def get_state_representation(self):
        return {
            'level': self.level,
            'score': self.score,
            'target_score': self.target_score,
            'board': self.board.get_representation(),
            'avl_plates': self.avl_plates.get_representation(),
            'moves': self.moves,
            'game_over': self.game_over,
            'win': self.win
        }
    
    def clone(self):
        new_state = GameState(self.level, board_rows=self.board.rows, board_cols=self.board.cols, plate_count=self.avl_plates.total_plate_limit)
        new_state.score = self.score
        new_state.moves = self.moves
        new_state.game_over = self.game_over
        new_state.win = self.win
        new_state.target_score = self.target_score
        new_state.board = self.board.clone()
        new_state.avl_plates = self.avl_plates.clone()
        
        return new_state
    
    @staticmethod
    def load_from_file(filepath):
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
            if len(lines) < 3:
                print(f"Arquivo inválido: {filepath}")
                return None
                
            level_line = lines[0].strip()
            if level_line.startswith("Level:"):
                level = int(level_line.split(":")[1].strip())
            else:
                level = 1
                
            state = GameState(level)
            
            board_start = -1
            plates_start = -1
            
            for i, line in enumerate(lines):
                if "Board:" in line:
                    board_start = i + 1
                elif "Available Plates:" in line:
                    plates_start = i + 1
                    break
                    
            if board_start == -1 or plates_start == -1:
                print(f"Formato de arquivo inválido: {filepath}")
                return None
                
            rows = int((plates_start - board_start - 1) / 2)
            cols = len(lines[board_start].strip().split())
            
            state.board = Board(rows, cols)
            
            for r in range(rows):
                plate_line = lines[board_start + r * 2].strip().split()
                for c in range(len(plate_line)):
                    if plate_line[c] != "Empty":
                        plate = [int(s) if s != "None" else None for s in plate_line[c].split(',')]
                        state.board.grid[r][c] = plate
            
            avl_plates_str = lines[plates_start].strip().split(';')
            
            state.avl_plates.visible_plates = []
            state.avl_plates.plates_queue = []
            
            for i, plate_str in enumerate(avl_plates_str[:state.avl_plates.max_plates]):
                if plate_str != "Empty":
                    plate = [int(s) if s != "None" else None for s in plate_str.split(',')]
                    state.avl_plates.visible_plates.append(plate)
            
            for plate_str in avl_plates_str[state.avl_plates.max_plates:]:
                if plate_str != "Empty":
                    plate = [int(s) if s != "None" else None for s in plate_str.split(',')]
                    state.avl_plates.plates_queue.append(plate)
                    
            state.avl_plates.plates_used = state.avl_plates.total_plate_limit - (
                len(state.avl_plates.visible_plates) + len(state.avl_plates.plates_queue))
            
            return state
        except Exception as e:
            print(f"Erro ao carregar arquivo: {filepath}")
            print(e)
            return None
    
    def save_to_file(self, filepath):
        try:
            with open(filepath, 'w') as file:
                file.write(f"Level: {self.level}\n\n")
                
                file.write("Board:\n")
                for r in range(self.board.rows):
                    row_str = []
                    for c in range(self.board.cols):
                        if self.board.is_empty(r, c):
                            row_str.append("Empty")
                        else:
                            plate_str = ','.join(str(s) if s is not None else "None" for s in self.board.grid[r][c])
                            row_str.append(plate_str)
                    file.write(' '.join(row_str) + '\n\n')
                
                file.write("Available Plates:\n")
                all_plates = self.avl_plates.visible_plates + self.avl_plates.plates_queue
                
                plates_str = []
                for plate in all_plates:
                    plate_str = ','.join(str(s) if s is not None else "None" for s in plate)
                    plates_str.append(plate_str)
                
                file.write(';'.join(plates_str))
                file.write('\n')
                
            return True
        except Exception as e:
            print(f"Erro ao salvar arquivo: {filepath}")
            print(e)
            return False