#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de algoritmos de busca - Implementa os algoritmos BFS, DFS, IDS e UCS
para resolver o puzzle de ordenação de bolos.
"""

import heapq
from collections import deque


class Node:
    """Classe que representa um nó na árvore de busca.
    
    Attributes:
        state (GameState): Estado do jogo associado a este nó.
        parent (Node): Nó pai na árvore de busca.
        action (tuple): Ação que levou a este nó (x, y, plate_index).
        cost (int): Custo acumulado para chegar a este nó.
        depth (int): Profundidade deste nó na árvore de busca.
    """
    
    def __init__(self, state, parent=None, action=None, cost=0, depth=0):
        """Inicializa um novo nó.
        
        Args:
            state (GameState): Estado do jogo associado a este nó.
            parent (Node, optional): Nó pai na árvore de busca.
            action (tuple, optional): Ação que levou a este nó (x, y, plate_index).
            cost (int, optional): Custo acumulado para chegar a este nó.
            depth (int, optional): Profundidade deste nó na árvore de busca.
        """
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = depth
    
    def __lt__(self, other):
        """Comparação para uso em filas de prioridade.
        
        Args:
            other (Node): Outro nó para comparação.
            
        Returns:
            bool: True se este nó tem menor custo que o outro.
        """
        return self.cost < other.cost


def get_successors(node):
    """Retorna os nós sucessores de um nó dado.
    
    Args:
        node (Node): Nó atual.
        
    Returns:
        list: Lista de nós sucessores.
    """
    successors = []
    state = node.state
    
    # Para cada posição no tabuleiro
    for x in range(state.board.rows):
        for y in range(state.board.cols):
            # Se a posição estiver vazia
            if state.board.is_empty(x, y):
                # Para cada prato disponível visível
                for plate_index in range(len(state.avl_plates.visible_plates)):
                    # Cria um novo estado
                    new_state = state.clone()
                    
                    # Tenta colocar o prato no tabuleiro
                    success, _ = new_state.place_plate(x, y, plate_index)
                    if success:
                        # Cria um novo nó
                        action = (x, y, plate_index)
                        cost = node.cost + 1  # Cada movimento tem custo 1
                        depth = node.depth + 1
                        successor = Node(new_state, node, action, cost, depth)
                        successors.append(successor)
    
    return successors


def is_goal(node):
    """Verifica se um nó representa um estado objetivo.
    
    Args:
        node (Node): Nó a ser verificado.
        
    Returns:
        bool: True se o nó representa um estado objetivo, False caso contrário.
    """
    # Vitória agora é quando todos os pratos foram colocados sem preencher o tabuleiro
    return node.state.win or (node.state.avl_plates.is_exhausted() and not node.state.board.is_full())


def get_solution_path(node):
    """Retorna o caminho da solução a partir do nó objetivo.
    
    Args:
        node (Node): Nó objetivo.
        
    Returns:
        list: Lista de ações que levam do estado inicial ao objetivo.
    """
    path = []
    current = node
    
    while current.parent is not None:
        path.append(current.action)
        current = current.parent
    
    # Inverte o caminho para obter a ordem correta (do início ao fim)
    path.reverse()
    
    return path


def bfs(initial_state):
    """Implementa o algoritmo de busca em largura (BFS).
    
    Args:
        initial_state (GameState): Estado inicial do jogo.
        
    Returns:
        tuple: (bool, list) - Sucesso e caminho da solução ou None.
    """
    # Cria o nó inicial
    initial_node = Node(initial_state)
    
    # Verifica se o estado inicial já é um objetivo
    if is_goal(initial_node):
        return True, []
    
    # Inicializa a fila e o conjunto de estados visitados
    queue = deque([initial_node])
    visited = set()
    
    while queue:
        # Remove o primeiro nó da fila
        node = queue.popleft()
        
        # Obtém uma representação hashable do estado
        state_repr = str(node.state.get_state_representation())
        
        # Verifica se o estado já foi visitado
        if state_repr in visited:
            continue
        
        # Marca o estado como visitado
        visited.add(state_repr)
        
        # CORREÇÃO: Verificar se o nó atual é um objetivo
        if is_goal(node):
            return True, get_solution_path(node)
        
        # Gera os sucessores
        for successor in get_successors(node):
            # Não precisamos verificar o objetivo aqui, pois verificamos cada nó quando é retirado da fila
            queue.append(successor)
    
    # Não encontrou solução
    return False, None


def dfs(initial_state, depth_limit=None):
    """Implementa o algoritmo de busca em profundidade (DFS).
    
    Args:
        initial_state (GameState): Estado inicial do jogo.
        depth_limit (int, optional): Limite de profundidade para a busca.
        
    Returns:
        tuple: (bool, list) - Sucesso e caminho da solução ou None.
    """
    # Cria o nó inicial
    initial_node = Node(initial_state)
    
    # Verifica se o estado inicial já é um objetivo
    if is_goal(initial_node):
        return True, []
    
    # Define um limite de profundidade padrão se não for especificado
    if depth_limit is None:
        # Usar o número total de pratos como base para o limite (cada prato pode ser uma ação)
        depth_limit = initial_state.avl_plates.total_plate_limit * 2
    
    # Inicializa a pilha e o conjunto de estados visitados
    stack = [initial_node]
    visited = set()
    
    while stack:
        # Remove o último nó da pilha
        node = stack.pop()
        
        # Verifica se atingiu o limite de profundidade
        if node.depth >= depth_limit:
            continue
        
        # Obtém uma representação hashable do estado
        state_repr = str(node.state.get_state_representation())
        
        # Verifica se o estado já foi visitado
        if state_repr in visited:
            continue
        
        # Marca o estado como visitado
        visited.add(state_repr)
        
        # Verifica se este é um estado objetivo
        if is_goal(node):
            return True, get_solution_path(node)
        
        # Gera os sucessores
        successors = get_successors(node)
        
        # Embaralha os sucessores para evitar tendência para uma direção específica
        import random
        random.shuffle(successors)
        
        # Adiciona todos os sucessores à pilha
        for successor in successors:
            stack.append(successor)
    
    # Não encontrou solução
    return False, None


def ids(initial_state, max_depth=50):
    """Implementa o algoritmo de busca em profundidade iterativa (IDS).
    
    Args:
        initial_state (GameState): Estado inicial do jogo.
        max_depth (int, optional): Profundidade máxima para a busca.
        
    Returns:
        tuple: (bool, list) - Sucesso e caminho da solução ou None.
    """
    for depth in range(max_depth + 1):
        success, path = dfs(initial_state, depth)
        if success:
            return True, path
    
    # Não encontrou solução dentro do limite de profundidade
    return False, None


def ucs(initial_state):
    """Implementa o algoritmo de busca de custo uniforme (UCS).
    
    Args:
        initial_state (GameState): Estado inicial do jogo.
        
    Returns:
        tuple: (bool, list) - Sucesso e caminho da solução ou None.
    """
    # Cria o nó inicial
    initial_node = Node(initial_state)
    
    # Verifica se o estado inicial já é um objetivo
    if is_goal(initial_node):
        return True, []
    
    # Inicializa a fila de prioridade e o conjunto de estados visitados
    priority_queue = [initial_node]  # heapq usa o operador < para comparação
    visited = set()
    
    while priority_queue:
        # Remove o nó de menor custo da fila
        node = heapq.heappop(priority_queue)
        
        # Obtém uma representação hashable do estado
        state_repr = str(node.state.get_state_representation())
        
        # Verifica se o estado já foi visitado
        if state_repr in visited:
            continue
        
        # Marca o estado como visitado
        visited.add(state_repr)
        
        # Gera os sucessores
        for successor in get_successors(node):
            # Verifica se o sucessor é um objetivo
            if is_goal(successor):
                return True, get_solution_path(successor)
            
            # Adiciona o sucessor à fila de prioridade
            heapq.heappush(priority_queue, successor)
    
    # Não encontrou solução
    return False, None


def get_algorithm(algorithm_name):
    """Retorna a função de algoritmo correspondente ao nome."""
    algorithms = {
        'bfs': bfs,
        'dfs': lambda state: dfs(state, depth_limit=state.avl_plates.total_plate_limit * 3),
        'ids': ids,
        'ucs': ucs
    }
    
    return algorithms.get(algorithm_name.lower())