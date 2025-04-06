#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de heurísticas - Implementa as funções heurísticas para os algoritmos de busca.
"""


def free_slots_heuristic(node):
    """Heurística baseada no número de slots vazios no tabuleiro.
    
    Avalia o número de slots vazios disponíveis no tabuleiro.
    Um maior número de slots vazios proporciona mais flexibilidade para reorganizar os bolos,
    enquanto menos slots vazios indica que o jogador está mais próximo de perder,
    pois há menos espaço para colocar novos pratos.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        int: Valor da heurística (inversamente proporcional ao número de slots vazios).
    """
    board = node.state.board
    empty_slots = sum(1 for i in range(board.rows) for j in range(board.cols) if board.is_empty(i, j))
    
    # Quanto mais slots vazios, melhor (menor valor heurístico)
    # Usamos o valor máximo possível de slots vazios menos o valor atual
    max_slots = board.rows * board.cols
    return max_slots - empty_slots


def missing_slices_heuristic(node):
    """Heurística baseada no número de fatias faltantes para completar os bolos.
    
    Calcula o número total de cada tipo de fatia necessária para completar todos os bolos no tabuleiro.
    Um valor menor sugere uma configuração de tabuleiro melhor.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        int: Valor da heurística (número de fatias faltantes).
    """
    board = node.state.board
    avl_plates = node.state.avl_plates
    
    # Conta as fatias de cada tipo no tabuleiro e nos pratos disponíveis
    slice_counts = {}
    
    # Conta as fatias no tabuleiro
    for i in range(board.rows):
        for j in range(board.cols):
            if not board.is_empty(i, j):
                plate = board.grid[i][j]
                for slice_type in plate:
                    if slice_type is not None:
                        if slice_type not in slice_counts:
                            slice_counts[slice_type] = 0
                        slice_counts[slice_type] += 1
    
    # Conta as fatias nos pratos disponíveis
    for plate in avl_plates.plates:
        for slice_type in plate:
            if slice_type is not None:
                if slice_type not in slice_counts:
                    slice_counts[slice_type] = 0
                slice_counts[slice_type] += 1
    
    # Calcula quantas fatias faltam para completar cada tipo de bolo
    # Um bolo completo tem 8 fatias do mesmo tipo
    missing_slices = 0
    for slice_type, count in slice_counts.items():
        if count < 8:  # Se não tiver 8 fatias, está incompleto
            missing_slices += (8 - count)
    
    return missing_slices


def clustered_slices_heuristic(node):
    """Heurística baseada no agrupamento de fatias similares.
    
    Avalia o quão bem as fatias do mesmo bolo estão agrupadas - ou seja, se as fatias do mesmo bolo
    estão no mesmo prato ou em pratos próximos uns dos outros.
    Uma pontuação de agrupamento mais alta significa que serão necessários menos movimentos para completar os bolos.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        int: Valor da heurística (inversamente proporcional ao agrupamento).
    """
    board = node.state.board
    
    # Mapeia cada tipo de fatia para suas posições no tabuleiro
    slice_positions = {}
    
    # Coleta as posições de todas as fatias no tabuleiro
    for i in range(board.rows):
        for j in range(board.cols):
            if not board.is_empty(i, j):
                plate = board.grid[i][j]
                for slice_type in plate:
                    if slice_type is not None:
                        if slice_type not in slice_positions:
                            slice_positions[slice_type] = []
                        slice_positions[slice_type].append((i, j))
    
    # Calcula a dispersão das fatias de cada tipo
    # Menor dispersão = melhor agrupamento
    total_dispersion = 0
    for slice_type, positions in slice_positions.items():
        if len(positions) <= 1:
            continue  # Não há dispersão com apenas uma fatia
        
        # Calcula a distância Manhattan entre todas as fatias do mesmo tipo
        dispersion = 0
        for i in range(len(positions)):
            for j in range(i+1, len(positions)):
                r1, c1 = positions[i]
                r2, c2 = positions[j]
                manhattan_dist = abs(r1 - r2) + abs(c1 - c2)
                dispersion += manhattan_dist
        
        total_dispersion += dispersion
    
    return total_dispersion


def estimated_moves_heuristic(node):
    """Heurística baseada no número estimado de movimentos para finalizar o nível.
    
    Avalia o número mínimo de movimentos necessários para atingir a pontuação alvo
    com base nas colocações atuais e nos pratos disponíveis.
    Um valor menor indica um estado mais otimizado.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        int: Valor da heurística (número estimado de movimentos).
    """
    # Distância até a pontuação alvo
    score_distance = node.state.target_score - node.state.score
    
    # Cada bolo completo vale 1 ponto, então precisamos de score_distance bolos completos
    # Estimamos que cada movimento de prato contribui para no máximo 1/4 de um bolo completo
    # (assumindo que precisamos de pelo menos 4 movimentos para completar um bolo)
    estimated_moves = score_distance * 4
    
    # Ajusta com base no número de pratos disponíveis
    # Quanto mais pratos disponíveis, mais movimentos podem ser necessários
    estimated_moves += len(node.state.avl_plates.plates)
    
    return estimated_moves


def combined_custom_heuristic(node):
    """Heurística combinada personalizada que considera todas as heurísticas anteriores.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        int: Valor da heurística combinada.
    """
    # Pesos para cada heurística
    w1, w2, w3, w4 = 1.0, 2.0, 1.5, 3.0
    
    h1 = free_slots_heuristic(node)
    h2 = missing_slices_heuristic(node)
    h3 = clustered_slices_heuristic(node)
    h4 = estimated_moves_heuristic(node)
    
    return w1 * h1 + w2 * h2 + w3 * h3 + w4 * h4