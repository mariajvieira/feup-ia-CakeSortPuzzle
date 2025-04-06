#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe AvailablePlates - Responsável por gerenciar os pratos disponíveis para o jogador.
"""

import random
import copy


class AvailablePlates:
    """Classe que representa os pratos disponíveis para o jogador.
    
    Attributes:
        plates (list): Lista de pratos disponíveis.
        visible_plates (list): Lista de pratos visíveis para o jogador (no máximo 3).
        max_plates (int): Número máximo de pratos visíveis simultaneamente.
        slice_types (list): Tipos de fatias disponíveis no jogo.
        plates_used (int): Número de pratos já utilizados pelo jogador.
        total_plate_limit (int): Limite total de pratos disponíveis no jogo.
        plates_queue (list): Fila de pratos que serão disponibilizados.
    """
    
    def __init__(self, level=1):
        """Inicializa os pratos disponíveis.
        
        Args:
            level (int): Nível do jogo, que influencia a complexidade dos pratos.
        """
        self.max_plates = 3  # Número máximo de pratos visíveis simultaneamente
        self.total_plate_limit = 18  # Limite total de pratos no jogo
        self.plates_used = 0  # Contador de pratos já utilizados
        
        # Define os tipos de fatias disponíveis com base no nível
        self.slice_types = self._get_slice_types(level)
        
        # Inicializa os pratos disponíveis visíveis e a fila de pratos
        self.visible_plates = []
        self.plates_queue = []
        
        # Gera todos os pratos para o jogo (18 pratos)
        self._generate_all_plates(level)
        
        # Mostra os primeiros 3 pratos
        self._refill_visible_plates()
    
    def _get_slice_types(self, level):
        """Retorna os tipos de fatias disponíveis com base no nível.
        
        Args:
            level (int): Nível do jogo.
            
        Returns:
            list: Lista de tipos de fatias disponíveis.
        """
        # Tipos básicos de fatias (cores/sabores diferentes)
        basic_types = [1, 2, 3, 4, 5]
        
        # Adiciona mais tipos conforme o nível aumenta
        if level >= 3:
            basic_types.extend([6, 7])
        if level >= 5:
            basic_types.extend([8, 9])
        
        return basic_types
    
    def _generate_all_plates(self, level):
        """Gera todos os pratos para o jogo.
        
        Args:
            level (int): Nível do jogo.
        """
        # Limpa a fila de pratos
        self.plates_queue = []
        
        # Gera todos os pratos de uma vez (18 pratos)
        for _ in range(self.total_plate_limit):
            plate = self._generate_single_plate(level)
            self.plates_queue.append(plate)
    
    def _generate_single_plate(self, level):
        """Gera um único prato com fatias aleatórias.
        
        Args:
            level (int): Nível do jogo.
            
        Returns:
            list: Um prato com fatias aleatórias.
        """
        # Determina o número de fatias no prato (entre 1 e 5, aumentando com o nível)
        num_slices = random.randint(1, min(5, level + 2))
        
        # Inicializa o prato com 8 espaços vazios (None)
        plate = [None] * 8
        
        # Preenche o prato com fatias aleatórias
        for _ in range(num_slices):
            # Escolhe um tipo de fatia aleatório
            slice_type = random.choice(self.slice_types)
            
            # Encontra um espaço vazio no prato
            empty_indices = [i for i, slice_val in enumerate(plate) if slice_val is None]
            if empty_indices:  # Se houver espaços vazios
                index = random.choice(empty_indices)
                plate[index] = slice_type
        
        return plate
    
    def _refill_visible_plates(self):
        """Preenche os pratos visíveis com pratos da fila, se disponíveis."""
        # Preenche os pratos visíveis até o máximo ou até acabar a fila
        while len(self.visible_plates) < self.max_plates and self.plates_queue:
            self.visible_plates.append(self.plates_queue.pop(0))
    
    def get_plate(self, index):
        """Retorna um prato específico.
        
        Args:
            index (int): Índice do prato na lista de disponíveis visíveis.
            
        Returns:
            list: O prato solicitado ou None se o índice for inválido.
        """
        if 0 <= index < len(self.visible_plates):
            return copy.deepcopy(self.visible_plates[index])
        return None
    
    def remove_plate(self, index):
        """Remove um prato da lista de disponíveis visíveis e atualiza os pratos disponíveis.
        
        Args:
            index (int): Índice do prato a ser removido.
            
        Returns:
            bool: True se o prato foi removido com sucesso, False caso contrário.
        """
        if 0 <= index < len(self.visible_plates):
            # Remove o prato
            self.visible_plates.pop(index)
            
            # Incrementa o contador de pratos utilizados
            self.plates_used += 1
            
            # Reabastece os pratos visíveis se necessário e se ainda houver na fila
            self._refill_visible_plates()
            
            return True
        return False
    
    def has_plates(self):
        """Verifica se ainda há pratos disponíveis para uso.
        
        Returns:
            bool: True se há pratos disponíveis, False caso contrário.
        """
        return len(self.visible_plates) > 0 or len(self.plates_queue) > 0
    
    def is_exhausted(self):
        """Verifica se todos os pratos disponíveis já foram utilizados.
        
        Returns:
            bool: True se todos os pratos já foram utilizados, False caso contrário.
        """
        return self.plates_used >= self.total_plate_limit
    
    def get_remaining_plates(self):
        """Retorna o número de pratos restantes para uso.
        
        Returns:
            int: Número de pratos restantes.
        """
        return self.total_plate_limit - self.plates_used
    
    def get_visible_plate_count(self):
        """Retorna o número de pratos visíveis.
        
        Returns:
            int: Número de pratos visíveis.
        """
        return len(self.visible_plates)
    
    def get_representation(self):
        """Retorna uma representação dos pratos disponíveis.
        
        Returns:
            dict: Dicionário com informações sobre os pratos disponíveis.
        """
        return {
            'visible_plates': copy.deepcopy(self.visible_plates),
            'plates_used': self.plates_used,
            'total_limit': self.total_plate_limit,
            'queue_size': len(self.plates_queue)
        }
    
    def clone(self):
        """Cria uma cópia profunda dos pratos disponíveis.
        
        Returns:
            AvailablePlates: Uma nova instância de AvailablePlates com os mesmos valores.
        """
        new_avl_plates = AvailablePlates(1)  # Nível 1 temporário
        new_avl_plates.visible_plates = copy.deepcopy(self.visible_plates)
        new_avl_plates.plates_queue = copy.deepcopy(self.plates_queue)
        new_avl_plates.max_plates = self.max_plates
        new_avl_plates.slice_types = copy.deepcopy(self.slice_types)
        new_avl_plates.plates_used = self.plates_used
        new_avl_plates.total_plate_limit = self.total_plate_limit
        
        return new_avl_plates