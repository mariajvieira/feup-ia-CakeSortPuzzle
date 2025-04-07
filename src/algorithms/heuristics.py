"""
Módulo de heurísticas - Implementa as funções heurísticas para os algoritmos de busca.
"""


def free_slots_heuristic(node):
    board = node.state.board
    empty_slots = sum(1 for i in range(board.rows) for j in range(board.cols) if board.is_empty(i, j))
    
    max_slots = board.rows * board.cols
    return max_slots - empty_slots


def missing_slices_heuristic(node):
    state = node.state
    board = state.board
    avl_plates = state.avl_plates
    
    slice_counts = {}
    for x in range(board.rows):
        for y in range(board.cols):
            if not board.is_empty(x, y):
                for slice_type in board.grid[x][y]:
                    if slice_type is not None:
                        slice_counts[slice_type] = slice_counts.get(slice_type, 0) + 1
    
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
    state = node.state
    board = state.board
    avl_plates = state.avl_plates
    
    slice_positions = {}
    
    for x in range(board.rows):
        for y in range(board.cols):
            if not board.is_empty(x, y):
                for i, slice_type in enumerate(board.grid[x][y]):
                    if slice_type is not None:
                        if slice_type not in slice_positions:
                            slice_positions[slice_type] = []
                        slice_positions[slice_type].append((x, y, i))
    
    for p_idx, plate in enumerate(avl_plates.visible_plates):
        for i, slice_type in enumerate(plate):
            if slice_type is not None:
                if slice_type not in slice_positions:
                    slice_positions[slice_type] = []
                slice_positions[slice_type].append((-1, p_idx, i))
    
    for p_idx, plate in enumerate(avl_plates.plates_queue):
        for i, slice_type in enumerate(plate):
            if slice_type is not None:
                if slice_type not in slice_positions:
                    slice_positions[slice_type] = []
                slice_positions[slice_type].append((-2, p_idx, i))
    
    total_dispersion = 0
    for slice_type, positions in slice_positions.items():
        if len(positions) <= 1:
            continue
        
        dispersion = 0
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                x1, y1, _ = positions[i]
                x2, y2, _ = positions[j]
                
                if x1 < 0 or x2 < 0:
                    dispersion += 5
                else:
                    dispersion += abs(x1 - x2) + abs(y1 - y2)
        
        total_dispersion += dispersion
    
    return total_dispersion


def estimated_moves_heuristic(node):
    state = node.state
    avl_plates = state.avl_plates
    
    remaining_plates = len(avl_plates.visible_plates) + len(avl_plates.plates_queue)
    
    return remaining_plates


def combined_custom_heuristic(node):
    # Pesos para cada heurística
    w1, w2, w3, w4 = 1.0, 2.0, 1.5, 3.0
    
    h1 = free_slots_heuristic(node)
    h2 = missing_slices_heuristic(node)
    h3 = clustered_slices_heuristic(node)
    h4 = estimated_moves_heuristic(node)
    
    return w1 * h1 + w2 * h2 + w3 * h3 + w4 * h4