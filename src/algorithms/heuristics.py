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
    """Heurística baseada no número de fatias necessárias para completar bolos.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        float: Valor da heurística (menor é melhor).
    """
    state = node.state
    board = state.board
    avl_plates = state.avl_plates
    
    # Conta o número total de fatias de cada tipo no tabuleiro
    slice_counts = {}
    for x in range(board.rows):
        for y in range(board.cols):
            if not board.is_empty(x, y):
                for slice_type in board.grid[x][y]:
                    if slice_type is not None:
                        slice_counts[slice_type] = slice_counts.get(slice_type, 0) + 1
    
    # Conta as fatias nos pratos disponíveis
    # MODIFICADO: Conta em visible_plates e plates_queue
    for plate in avl_plates.visible_plates + avl_plates.plates_queue:
        for slice_type in plate:
            if slice_type is not None:
                slice_counts[slice_type] = slice_counts.get(slice_type, 0) + 1
    
    # Calcula quantas fatias estão faltando para completar bolos
    missing_slices = 0
    for slice_type, count in slice_counts.items():
        complete_cakes = count // 8  # Cada bolo tem 8 fatias
        remaining = count % 8
        if remaining > 0:
            missing_slices += (8 - remaining)  # Fatias necessárias para completar
    
    return missing_slices


def clustered_slices_heuristic(node):
    """Heurística baseada no agrupamento de fatias do mesmo tipo.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        float: Valor da heurística (menor é melhor).
    """
    state = node.state
    board = state.board
    avl_plates = state.avl_plates
    
    # Mapeia cada tipo de fatia para suas posições no tabuleiro
    slice_positions = {}
    
    # Verifica o tabuleiro
    for x in range(board.rows):
        for y in range(board.cols):
            if not board.is_empty(x, y):
                for i, slice_type in enumerate(board.grid[x][y]):
                    if slice_type is not None:
                        if slice_type not in slice_positions:
                            slice_positions[slice_type] = []
                        slice_positions[slice_type].append((x, y, i))
    
    # Verifica os pratos disponíveis
    # MODIFICADO: Usa visible_plates em vez de plates
    for p_idx, plate in enumerate(avl_plates.visible_plates):
        for i, slice_type in enumerate(plate):
            if slice_type is not None:
                if slice_type not in slice_positions:
                    slice_positions[slice_type] = []
                # Posição especial para os pratos disponíveis
                slice_positions[slice_type].append((-1, p_idx, i))
    
    # ADICIONADO: Verifica também plates_queue
    for p_idx, plate in enumerate(avl_plates.plates_queue):
        for i, slice_type in enumerate(plate):
            if slice_type is not None:
                if slice_type not in slice_positions:
                    slice_positions[slice_type] = []
                # Posição especial para os pratos na fila
                slice_positions[slice_type].append((-2, p_idx, i))
    
    # Calcula a dispersão das fatias de cada tipo
    total_dispersion = 0
    for slice_type, positions in slice_positions.items():
        # Ignora se há apenas uma fatia deste tipo
        if len(positions) <= 1:
            continue
        
        # Calcula a dispersão como a soma das distâncias Manhattan entre todas as fatias
        dispersion = 0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                x1, y1, _ = positions[i]
                x2, y2, _ = positions[j]
                
                # Se uma das fatias está em um prato disponível, use uma distância fixa maior
                if x1 < 0 or x2 < 0:
                    dispersion += 5
                else:
                    dispersion += abs(x1 - x2) + abs(y1 - y2)
        
        total_dispersion += dispersion
    
    return total_dispersion


def estimated_moves_heuristic(node):
    """Heurística baseada no número estimado de movimentos para completar o jogo.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        float: Valor da heurística (menor é melhor).
    """
    state = node.state
    avl_plates = state.avl_plates
    
    # Estima o número de pratos restantes para colocar
    # MODIFICADO: Usa visible_plates e plates_queue
    remaining_plates = len(avl_plates.visible_plates) + len(avl_plates.plates_queue)
    
    # Cada prato colocado é um movimento, então o número mínimo de movimentos
    # restantes é igual ao número de pratos restantes
    return remaining_plates


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