#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe GameState - Responsável por gerenciar o estado do jogo.
"""

from src.models.board import Board
from src.models.avl_plates import AvailablePlates


class GameState:
    """Classe que representa o estado atual do jogo.
    
    Attributes:
        level (int): Nível atual do jogo.
        score (int): Pontuação atual do jogador.
        target_score (int): Pontuação alvo para completar o nível.
        board (Board): Tabuleiro do jogo.
        avl_plates (AvailablePlates): Pratos disponíveis para colocação.
        moves (int): Número de movimentos realizados.
        game_over (bool): Indica se o jogo acabou.
        win (bool): Indica se o jogador venceu.
    """
    
    def __init__(self, level=1, board_rows=None, board_cols=None, plate_count=None):
        """Inicializa um novo estado de jogo.
        
        Args:
            level (int): Nível inicial do jogo.
            board_rows (int, optional): Número de linhas do tabuleiro. Se None, usa o padrão do nível.
            board_cols (int, optional): Número de colunas do tabuleiro. Se None, usa o padrão do nível.
            plate_count (int, optional): Quantidade de bolos disponíveis. Se None, usa o padrão do nível.
        """
        self.level = level
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.win = False
        
        # Define o tamanho do tabuleiro com base no nível ou nos parâmetros fornecidos
        if board_rows is None or board_cols is None:
            board_size = self._get_board_size(level)
            board_rows = board_rows or board_size[0]
            board_cols = board_cols or board_size[1]
        
        # Inicializa o tabuleiro com o tamanho especificado
        self.board = Board(board_rows, board_cols)
        
        # Inicializa os pratos disponíveis com a quantidade especificada
        self.avl_plates = AvailablePlates(level, plate_count)
        
        # Não há pontuação alvo, apenas pontuação acumulada pelos bolos completados
        self.target_score = None  # Removemos o conceito de pontuação alvo
    
    def _get_board_size(self, level):
        """Retorna o tamanho do tabuleiro com base no nível.
        
        Args:
            level (int): Nível do jogo.
            
        Returns:
            tuple: Tupla contendo (linhas, colunas) do tabuleiro.
        """
        # Tamanhos de tabuleiro para diferentes níveis (reduzidos)
        sizes = {
            1: (2, 2),  # Nível 1: 3x3 (era 4x4)
            2: (3, 4),  # Nível 2: 3x4 (era 4x5)
            3: (4, 4),  # Nível 3: 4x4 (era 5x5)
            4: (4, 5),  # Nível 4: 4x5 (era 5x6)
            5: (5, 5)   # Nível 5: 5x5 (era 6x6)
        }
        
        # Retorna o tamanho correspondente ao nível ou o maior tamanho disponível
        return sizes.get(level, sizes[max(sizes.keys())])
    
    def place_plate(self, x, y, plate_index):
        """Coloca um prato no tabuleiro na posição especificada.
        
        Args:
            x (int): Coordenada x no tabuleiro.
            y (int): Coordenada y no tabuleiro.
            plate_index (int): Índice do prato disponível a ser colocado.
            
        Returns:
            tuple: (bool, dict) - True se o prato foi colocado com sucesso e informações sobre as animações.
        """
        # Verifica se a posição está vazia
        if not self.board.is_empty(x, y):
            return False, {}
        
        # Obtém o prato dos disponíveis
        plate = self.avl_plates.get_plate(plate_index)
        if plate is None:
            return False, {}
        
        # Coloca o prato no tabuleiro
        success = self.board.place_plate(x, y, plate)
        if success:
            # Remove o prato dos disponíveis
            self.avl_plates.remove_plate(plate_index)
            
            # Incrementa o número de movimentos
            self.moves += 1
            
            # Informações para animações
            animation_info = {
                'slice_movements': [],
                'completed_cakes': 0,
                'cake_positions': []
            }
            
            # Verifica pratos adjacentes e obtém movimentos de fatias
            slice_movements = self._check_adjacent_plates(x, y)
            animation_info['slice_movements'] = slice_movements
            
            # Verifica se há bolos completos
            completed_cakes = self.board.check_completed_cakes()
            if completed_cakes > 0:
                self.score += completed_cakes
                animation_info['completed_cakes'] = completed_cakes
                animation_info['cake_positions'] = [(x, y)]  # Posição do último prato colocado
            
            # MUDANÇA 1: Verifica condição de vitória - se todos os pratos foram utilizados
            if self.avl_plates.is_exhausted():
                self.win = True
                self.game_over = True
            
            # MUDANÇA 2: Verifica se o tabuleiro está cheio (condição de derrota)
            # mas ainda tem pratos disponíveis para colocar
            if self.board.is_full() and not self.avl_plates.is_exhausted():
                self.game_over = True
                self.win = False
            
            # MUDANÇA 3: Verifica se ainda há movimentos válidos
            if not self.avl_plates.has_plates() and not self.win:
                self.game_over = True
            
            return True, animation_info
        
        return False, {}
    
    def _check_adjacent_plates(self, x, y):
        """Verifica e otimiza os pratos adjacentes.
        
        Args:
            x (int): Coordenada x do prato colocado.
            y (int): Coordenada y do prato colocado.
            
        Returns:
            list: Lista de movimentos de fatias realizados para animação.
        """
        # Obtém as posições adjacentes
        adjacent_positions = [
            (x-1, y), (x+1, y), (x, y-1), (x, y+1)  # Esquerda, Direita, Cima, Baixo
        ]
        
        # Lista para armazenar todos os movimentos de fatias
        all_movements = []
        
        # Verifica cada posição adjacente
        for adj_x, adj_y in adjacent_positions:
            if self.board.is_valid_position(adj_x, adj_y) and not self.board.is_empty(adj_x, adj_y):
                # Otimiza os pratos adjacentes e obtém os movimentos realizados
                _, movements = self.board.optimize_plates(x, y, adj_x, adj_y)
                all_movements.extend(movements)
                
        return all_movements
    
    def get_state_representation(self):
        """Retorna uma representação do estado atual do jogo.
        
        Returns:
            dict: Dicionário contendo a representação do estado.
        """
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
        """Cria uma cópia profunda do estado atual.
        
        Returns:
            GameState: Uma nova instância de GameState com os mesmos valores.
        """
        # Cria um novo estado com os mesmos parâmetros de tabuleiro e quantidade de bolos
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
        """Carrega um estado de jogo a partir de um arquivo de texto.
        
        Args:
            filepath (str): Caminho do arquivo a ser carregado.
            
        Returns:
            GameState: Estado de jogo carregado ou None se falhar.
        """
        try:
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
            if len(lines) < 3:
                print(f"Arquivo inválido: {filepath}")
                return None
                
            # Lê o nível, que deve estar na primeira linha
            level_line = lines[0].strip()
            if level_line.startswith("Level:"):
                level = int(level_line.split(":")[1].strip())
            else:
                level = 1
                
            # Cria um novo estado de jogo com o nível especificado
            state = GameState(level)
            
            # Lê a estrutura do tabuleiro
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
                
            # Lê o tabuleiro
            rows = int((plates_start - board_start - 1) / 2)
            cols = len(lines[board_start].strip().split())
            
            # Recria o tabuleiro com o tamanho correto
            state.board = Board(rows, cols)
            
            # Preenche o tabuleiro
            for r in range(rows):
                plate_line = lines[board_start + r * 2].strip().split()
                for c in range(len(plate_line)):
                    if plate_line[c] != "Empty":
                        # Decodifica o prato a partir da string
                        plate = [int(s) if s != "None" else None for s in plate_line[c].split(',')]
                        state.board.grid[r][c] = plate
            
            # Lê os pratos disponíveis
            avl_plates_str = lines[plates_start].strip().split(';')
            
            # Limpa os pratos disponíveis existentes
            state.avl_plates.visible_plates = []
            state.avl_plates.plates_queue = []
            
            # Adiciona os pratos visíveis (até 3)
            for i, plate_str in enumerate(avl_plates_str[:state.avl_plates.max_plates]):
                if plate_str != "Empty":
                    plate = [int(s) if s != "None" else None for s in plate_str.split(',')]
                    state.avl_plates.visible_plates.append(plate)
            
            # Adiciona o resto dos pratos à fila
            for plate_str in avl_plates_str[state.avl_plates.max_plates:]:
                if plate_str != "Empty":
                    plate = [int(s) if s != "None" else None for s in plate_str.split(',')]
                    state.avl_plates.plates_queue.append(plate)
                    
            # Ajusta o contador de pratos utilizados
            state.avl_plates.plates_used = state.avl_plates.total_plate_limit - (
                len(state.avl_plates.visible_plates) + len(state.avl_plates.plates_queue))
            
            return state
        except Exception as e:
            print(f"Erro ao carregar arquivo: {filepath}")
            print(e)
            return None
    
    def save_to_file(self, filepath):
        """Salva o estado atual do jogo em um arquivo de texto.
        
        Args:
            filepath (str): Caminho do arquivo para salvar.
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário.
        """
        try:
            with open(filepath, 'w') as file:
                # Escreve o nível
                file.write(f"Level: {self.level}\n\n")
                
                # Escreve o tabuleiro
                file.write("Board:\n")
                for r in range(self.board.rows):
                    row_str = []
                    for c in range(self.board.cols):
                        if self.board.is_empty(r, c):
                            row_str.append("Empty")
                        else:
                            # Converte o prato para string
                            plate_str = ','.join(str(s) if s is not None else "None" for s in self.board.grid[r][c])
                            row_str.append(plate_str)
                    file.write(' '.join(row_str) + '\n\n')
                
                # Escreve os pratos disponíveis
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