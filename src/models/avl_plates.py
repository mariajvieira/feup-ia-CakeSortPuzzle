#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe AvailablePlates - Responsável por gerenciar os pratos disponíveis para o jogador.
"""

import random
import copy


class AvailablePlates:
    """Classe que representa os pratos disponíveis para o jogador.
    
    Cada prato é representado por uma lista de até 8 elementos, onde cada elemento
    representa uma fatia de bolo de um determinado tipo.
    
    Attributes:
        plates (list): Lista de pratos disponíveis.
        max_plates (int): Número máximo de pratos disponíveis simultaneamente.
        slice_types (list): Tipos de fatias disponíveis no jogo.
    """
    
    def __init__(self, level=1):
        """Inicializa os pratos disponíveis.
        
        Args:
            level (int): Nível do jogo, que influencia a quantidade e complexidade dos pratos.
        """
        self.max_plates = 3  # Número máximo de pratos disponíveis simultaneamente
        
        # Define os tipos de fatias disponíveis com base no nível
        self.slice_types = self._get_slice_types(level)
        
        # Inicializa os pratos disponíveis
        self.plates = []
        self._generate_plates(level)
    
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
    
    def _generate_plates(self, level):
        """Gera pratos aleatórios com base no nível.
        
        Args:
            level (int): Nível do jogo.
        """
        # Limpa os pratos existentes
        self.plates = []
        
        # Determina o número de pratos a gerar
        num_plates = min(self.max_plates, level + 2)
        
        # Gera os pratos
        for _ in range(num_plates):
            plate = self._generate_single_plate(level)
            self.plates.append(plate)
    
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
    
    def get_plate(self, index):
        """Retorna um prato específico.
        
        Args:
            index (int): Índice do prato na lista de disponíveis.
            
        Returns:
            list: O prato solicitado ou None se o índice for inválido.
        """
        if 0 <= index < len(self.plates):
            return copy.deepcopy(self.plates[index])
        return None
    
    def remove_plate(self, index):
        """Remove um prato da lista de disponíveis e gera um novo se necessário.
        
        Args:
            index (int): Índice do prato a ser removido.
            
        Returns:
            bool: True se o prato foi removido com sucesso, False caso contrário.
        """
        if 0 <= index < len(self.plates):
            # Remove o prato
            self.plates.pop(index)
            
            # Gera um novo prato se o número de pratos disponíveis for menor que o máximo
            if len(self.plates) < self.max_plates:
                new_plate = self._generate_single_plate(1)  # Nível 1 para simplicidade
                self.plates.append(new_plate)
            
            return True
        return False
    
    def has_plates(self):
        """Verifica se ainda há pratos disponíveis.
        
        Returns:
            bool: True se há pratos disponíveis, False caso contrário.
        """
        return len(self.plates) > 0
    
    def get_representation(self):
        """Retorna uma representação dos pratos disponíveis.
        
        Returns:
            list: Lista de pratos disponíveis.
        """
        return copy.deepcopy(self.plates)
    
    def clone(self):
        """Cria uma cópia profunda dos pratos disponíveis.
        
        Returns:
            AvailablePlates: Uma nova instância de AvailablePlates com os mesmos valores.
        """
        new_avl_plates = AvailablePlates(1)  # Nível 1 temporário
        new_avl_plates.plates = copy.deepcopy(self.plates)
        new_avl_plates.max_plates = self.max_plates
        new_avl_plates.slice_types = copy.deepcopy(self.slice_types)
        
        return new_avl_plates