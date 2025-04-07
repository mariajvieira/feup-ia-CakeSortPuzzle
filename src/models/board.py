#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe Board - Responsável por gerenciar o tabuleiro do jogo.
"""

import copy


class Board:
    """Classe que representa o tabuleiro do jogo.
    
    O tabuleiro é uma matriz onde cada posição pode conter um prato com fatias de bolo.
    Cada prato é representado por uma lista de até 8 elementos, onde cada elemento
    representa uma fatia de bolo de um determinado tipo.
    
    Attributes:
        rows (int): Número de linhas do tabuleiro.
        cols (int): Número de colunas do tabuleiro.
        grid (list): Matriz que representa o tabuleiro.
    """
    
    def __init__(self, rows, cols):
        """Inicializa um novo tabuleiro vazio.
        
        Args:
            rows (int): Número de linhas do tabuleiro.
            cols (int): Número de colunas do tabuleiro.
        """
        self.rows = rows
        self.cols = cols
        # Inicializa o tabuleiro com None em todas as posições (vazio)
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
    
    def is_valid_position(self, x, y):
        """Verifica se uma posição está dentro dos limites do tabuleiro.
        
        Args:
            x (int): Coordenada x no tabuleiro.
            y (int): Coordenada y no tabuleiro.
            
        Returns:
            bool: True se a posição é válida, False caso contrário.
        """
        return 0 <= x < self.rows and 0 <= y < self.cols
    
    def is_empty(self, x, y):
        """Verifica se uma posição está vazia.
        
        Args:
            x (int): Coordenada x no tabuleiro.
            y (int): Coordenada y no tabuleiro.
            
        Returns:
            bool: True se a posição está vazia, False caso contrário.
        """
        if not self.is_valid_position(x, y):
            return False
        return self.grid[x][y] is None
    
    def place_plate(self, x, y, plate):
        """Coloca um prato no tabuleiro na posição especificada.
        
        Args:
            x (int): Coordenada x no tabuleiro.
            y (int): Coordenada y no tabuleiro.
            plate (list): Lista representando o prato com suas fatias.
            
        Returns:
            bool: True se o prato foi colocado com sucesso, False caso contrário.
        """
        if not self.is_valid_position(x, y) or not self.is_empty(x, y):
            return False
        
        self.grid[x][y] = plate
        return True
    
    def optimize_plates(self, x1, y1, x2, y2):
        """Otimiza dois pratos adjacentes para maximizar fatias do mesmo tipo.
        
        Args:
            x1 (int): Coordenada x do primeiro prato.
            y1 (int): Coordenada y do primeiro prato.
            x2 (int): Coordenada x do segundo prato.
            y2 (int): Coordenada y do segundo prato.
            
        Returns:
            tuple: (bool, list) - True se houve otimização e lista de movimentos realizados.
        """
        if not self.is_valid_position(x1, y1) or not self.is_valid_position(x2, y2):
            return False, []
        
        if self.is_empty(x1, y1) or self.is_empty(x2, y2):
            return False, []
        
        plate1 = self.grid[x1][y1]
        plate2 = self.grid[x2][y2]
        
        # Conta as fatias de cada tipo em cada prato
        count1 = self._count_slice_types(plate1)
        count2 = self._count_slice_types(plate2)
        
        # Verifica se há tipos comuns entre os pratos
        common_types = set(count1.keys()) & set(count2.keys())
        if not common_types:
            return False, []
        
        # Para cada tipo comum, tenta otimizar
        optimized = False
        movements = []
        
        for slice_type in common_types:
            # Se ambos os pratos têm o mesmo tipo, tenta mover fatias para maximizar
            # o número de fatias do mesmo tipo em um único prato
            if count1[slice_type] > 0 and count2[slice_type] > 0:
                # Decide qual prato deve receber as fatias
                if count1[slice_type] >= count2[slice_type]:
                    # Move fatias do prato 2 para o prato 1
                    moved, count = self._move_slices(plate2, plate1, slice_type)
                    if moved:
                        optimized = True
                        # Registra o movimento para animação (origem, destino, tipo, quantidade)
                        movements.append((x2, y2, x1, y1, slice_type, count))
                else:
                    # Move fatias do prato 1 para o prato 2
                    moved, count = self._move_slices(plate1, plate2, slice_type)
                    if moved:
                        optimized = True
                        # Registra o movimento para animação (origem, destino, tipo, quantidade)
                        movements.append((x1, y1, x2, y2, slice_type, count))
        
        return optimized, movements
    
    def _count_slice_types(self, plate):
        """Conta o número de fatias de cada tipo em um prato.
        
        Args:
            plate (list): Lista representando o prato com suas fatias.
            
        Returns:
            dict: Dicionário com a contagem de cada tipo de fatia.
        """
        count = {}
        for slice_type in plate:
            if slice_type is not None:  # Ignora espaços vazios
                count[slice_type] = count.get(slice_type, 0) + 1
        return count
    
    def _move_slices(self, source_plate, target_plate, slice_type):
        """Move fatias de um tipo específico de um prato para outro.
        
        Args:
            source_plate (list): Prato de origem.
            target_plate (list): Prato de destino.
            slice_type: Tipo de fatia a ser movida.
            
        Returns:
            tuple: (bool, int) - True se houve movimentação e o número de fatias movidas.
        """
        # Conta quantas fatias do tipo específico existem no prato de origem
        slices_to_move = source_plate.count(slice_type)
        if slices_to_move == 0:
            return False, 0
        
        # Verifica se há espaço no prato de destino
        empty_slots = target_plate.count(None)
        
        # Se não houver espaços vazios, verifica se podemos fazer trocas
        if empty_slots == 0:
            # Verifica se o prato de destino já tem fatias do mesmo tipo
            target_slices_of_type = target_plate.count(slice_type)
            if target_slices_of_type > 0:
                # Conta outros tipos de fatias no prato de destino
                other_types = {}
                for s in target_plate:
                    if s is not None and s != slice_type:
                        other_types[s] = other_types.get(s, 0) + 1
                
                # Verifica se há espaço no prato de origem para receber outras fatias
                source_empty_slots = source_plate.count(None)
                
                # Se houver pelo menos um tipo diferente no prato de destino e espaço no prato de origem
                if other_types and source_empty_slots >= min(other_types.values()):
                    # Escolhe o tipo com menor quantidade para mover para o prato de origem
                    other_type = min(other_types, key=other_types.get)
                    
                    # Move as fatias do outro tipo para o prato de origem
                    moved = False
                    slices_moved = 0
                    
                    # Primeiro, move as fatias do outro tipo para o prato de origem
                    for i in range(len(target_plate)):
                        if target_plate[i] == other_type and source_empty_slots > 0:
                            target_plate[i] = None
                            
                            # Adiciona a fatia ao prato de origem
                            for j in range(len(source_plate)):
                                if source_plate[j] is None:
                                    source_plate[j] = other_type
                                    break
                            
                            source_empty_slots -= 1
                            moved = True
                    
                    # Agora, move as fatias do tipo específico para o prato de destino
                    empty_slots = target_plate.count(None)
                    slices_to_move = min(slices_to_move, empty_slots)
                    
                    for i in range(len(source_plate)):
                        if source_plate[i] == slice_type and slices_to_move > 0:
                            source_plate[i] = None
                            
                            for j in range(len(target_plate)):
                                if target_plate[j] is None:
                                    target_plate[j] = slice_type
                                    break
                            
                            slices_to_move -= 1
                            slices_moved += 1
                            moved = True
                    
                    return moved, slices_moved
            
            return False, 0
        
        # Limita o número de fatias a mover ao espaço disponível
        slices_to_move = min(slices_to_move, empty_slots)
        
        # Move as fatias
        moved = False
        slices_moved = 0
        for i in range(len(source_plate)):
            if source_plate[i] == slice_type and slices_to_move > 0:
                # Remove a fatia do prato de origem
                source_plate[i] = None
                
                # Adiciona a fatia ao prato de destino
                for j in range(len(target_plate)):
                    if target_plate[j] is None:
                        target_plate[j] = slice_type
                        break
                
                slices_to_move -= 1
                slices_moved += 1
                moved = True
        
        return moved, slices_moved
        
    def is_plate_empty(self, x, y):
        """Verifica se um prato está completamente vazio (todas as posições são None).
        
        Args:
            x (int): Coordenada x no tabuleiro.
            y (int): Coordenada y no tabuleiro.
            
        Returns:
            bool: True se o prato está completamente vazio, False caso contrário.
        """
        if not self.is_valid_position(x, y) or self.is_empty(x, y):
            return False
            
        plate = self.grid[x][y]
        return all(slice_type is None for slice_type in plate)
    
    def check_completed_cakes(self):
        """Verifica se há bolos completos no tabuleiro e os remove.
        
        Um bolo completo é formado quando um prato contém 8 fatias do mesmo tipo.
        
        Returns:
            int: Número de bolos completos encontrados e removidos.
        """
        completed_cakes = 0
        
        for x in range(self.rows):
            for y in range(self.cols):
                if not self.is_empty(x, y):
                    plate = self.grid[x][y]
                    
                    # Conta as fatias de cada tipo
                    count = self._count_slice_types(plate)
                    
                    # Verifica se há algum tipo com 8 fatias (bolo completo)
                    for slice_type, num in count.items():
                        if num == 8:  # Um bolo completo tem 8 fatias
                            # Remove o prato (bolo completo)
                            self.grid[x][y] = None
                            completed_cakes += 1
                            break
        
        # Após verificar bolos completos, verifica e remove pratos vazios
        self.remove_empty_plates()
        
        return completed_cakes
        
    def remove_empty_plates(self):
        """Remove todos os pratos vazios do tabuleiro.
        
        Um prato vazio é aquele que não contém nenhuma fatia (todos os elementos são None).
        
        Returns:
            int: Número de pratos vazios removidos.
        """
        removed_plates = 0
        
        for x in range(self.rows):
            for y in range(self.cols):
                if not self.is_empty(x, y) and self.is_plate_empty(x, y):
                    # Remove o prato vazio
                    self.grid[x][y] = None
                    removed_plates += 1
        
        return removed_plates
        
    def is_full(self):
        """Verifica se o tabuleiro está completamente cheio.
        
        Returns:
            bool: True se o tabuleiro está cheio, False caso contrário.
        """
        for x in range(self.rows):
            for y in range(self.cols):
                if self.is_empty(x, y):
                    return False
        return True
    
    def get_representation(self):
        """Retorna uma representação do tabuleiro.
        
        Returns:
            list: Matriz representando o tabuleiro.
        """
        return copy.deepcopy(self.grid)
    
    def clone(self):
        """Cria uma cópia profunda do tabuleiro.
        
        Returns:
            Board: Uma nova instância de Board com os mesmos valores.
        """
        new_board = Board(self.rows, self.cols)
        new_board.grid = copy.deepcopy(self.grid)
        return new_board
    
    def count_occupied_cells(self):
        """Conta o número de células ocupadas no tabuleiro.
        
        Returns:
            int: Número de células ocupadas (que contêm um prato).
        """
        count = 0
        for x in range(self.rows):
            for y in range(self.cols):
                if not self.is_empty(x, y):
                    count += 1
        return count