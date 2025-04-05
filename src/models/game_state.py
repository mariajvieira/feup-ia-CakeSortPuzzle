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
    
    def __init__(self, level=1):
        """Inicializa um novo estado de jogo.
        
        Args:
            level (int): Nível inicial do jogo.
        """
        self.level = level
        self.score = 0
        self.moves = 0
        self.game_over = False
        self.win = False
        
        # Define o tamanho do tabuleiro com base no nível
        board_size = self._get_board_size(level)
        
        # Inicializa o tabuleiro e os pratos disponíveis
        self.board = Board(board_size[0], board_size[1])
        self.avl_plates = AvailablePlates(level)
        
        # Define a pontuação alvo com base no nível
        self.target_score = self._get_target_score(level)
    
    def _get_board_size(self, level):
        """Retorna o tamanho do tabuleiro com base no nível.
        
        Args:
            level (int): Nível do jogo.
            
        Returns:
            tuple: Tupla contendo (linhas, colunas) do tabuleiro.
        """
        # Tamanhos de tabuleiro para diferentes níveis
        sizes = {
            1: (4, 4),  # Nível 1: 4x4
            2: (4, 5),  # Nível 2: 4x5
            3: (5, 5),  # Nível 3: 5x5
            4: (5, 6),  # Nível 4: 5x6
            5: (6, 6)   # Nível 5: 6x6
        }
        
        # Retorna o tamanho correspondente ao nível ou o maior tamanho disponível
        return sizes.get(level, sizes[max(sizes.keys())])
    
    def _get_target_score(self, level):
        """Retorna a pontuação alvo com base no nível.
        
        Args:
            level (int): Nível do jogo.
            
        Returns:
            int: Pontuação alvo para o nível.
        """
        # Pontuações alvo para diferentes níveis
        targets = {
            1: 3,   # Nível 1: 3 bolos
            2: 5,   # Nível 2: 5 bolos
            3: 7,   # Nível 3: 7 bolos
            4: 10,  # Nível 4: 10 bolos
            5: 15   # Nível 5: 15 bolos
        }
        
        # Retorna a pontuação alvo correspondente ao nível ou a maior pontuação disponível
        return targets.get(level, targets[max(targets.keys())])
    
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
                
                # Verifica se o jogador atingiu a pontuação alvo
                if self.score >= self.target_score:
                    self.win = True
                    self.game_over = True
            
            # Verifica se o tabuleiro está cheio (condição de derrota)
            if self.board.is_full() and not self.win:
                self.game_over = True
                self.win = False
            
            # Verifica se ainda há movimentos válidos
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
        new_state = GameState(self.level)
        new_state.score = self.score
        new_state.moves = self.moves
        new_state.game_over = self.game_over
        new_state.win = self.win
        new_state.target_score = self.target_score
        new_state.board = self.board.clone()
        new_state.avl_plates = self.avl_plates.clone()
        
        return new_state