#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe GameView - Responsável por renderizar o jogo na tela.
"""

import pygame
import os
import math


class GameView:
    """Classe que representa a visualização do jogo.
    
    Attributes:
        screen (pygame.Surface): Superfície de renderização do jogo.
        game_state (GameState): Estado atual do jogo.
        colors (dict): Dicionário de cores utilizadas no jogo.
        fonts (dict): Dicionário de fontes utilizadas no jogo.
        board_rect (pygame.Rect): Retângulo que representa o tabuleiro.
        cell_size (int): Tamanho de cada célula do tabuleiro.
        plate_rects (list): Lista de retângulos que representam os pratos disponíveis.
    """
    
    def __init__(self, screen, game_state):
        """Inicializa a visualização do jogo.
        
        Args:
            screen (pygame.Surface): Superfície de renderização do jogo.
            game_state (GameState): Estado atual do jogo.
        """
        self.screen = screen
        self.game_state = game_state
        
        # Define as cores utilizadas no jogo (esquema colorido com cores distintas)
        self.colors = {
            'background': (255, 240, 245),  # Rosa claro para o fundo
            'board': (255, 228, 240),      # Rosa mais claro para o tabuleiro
            'grid_line': (219, 112, 147),  # Rosa médio para as linhas da grade
            'text': (199, 21, 133),        # Rosa escuro para o texto
            'highlight': (255, 105, 180, 100),  # Rosa quente com transparência
            'plate': (255, 240, 245),      # Rosa muito claro para os pratos
            # Cores para os diferentes tipos de fatias (cores totalmente distintas)
            'slice_1': (255, 20, 147),     # Rosa profundo
            'slice_2': (255, 165, 0),      # Laranja
            'slice_3': (50, 205, 50),      # Verde lima
            'slice_4': (30, 144, 255),     # Azul dodger
            'slice_5': (255, 215, 0),      # Ouro
            'slice_6': (138, 43, 226),     # Violeta
            'slice_7': (220, 20, 60),      # Vermelho carmesim
            'slice_8': (0, 206, 209),      # Turquesa
            'slice_9': (255, 105, 180)     # Rosa quente
            
        }
        
        # Configurações para animações
        self.animations = {
            'active': True,                # Animações ativadas por padrão
            'plate_move_duration': 20,     # Duração da animação de movimento de prato
            'cake_complete_duration': 30,  # Duração da animação de bolo completo
            'current_animations': [],      # Lista de animações ativas
            'particles': []                # Lista de partículas para efeitos
        }

        
        # Inicializa as fontes
        pygame.font.init()
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 14),
            'medium': pygame.font.SysFont('Arial', 20),
            'large': pygame.font.SysFont('Arial', 28),
            'title': pygame.font.SysFont('Arial', 36, bold=True)
        }
        
        # Calcula o tamanho e posição do tabuleiro
        self._calculate_layout()
    
    def _calculate_layout(self):
        """Calcula o layout da tela."""
        screen_width, screen_height = self.screen.get_size()
        
        # Calcula o tamanho de cada célula do tabuleiro
        board_width = min(screen_width * 0.7, screen_height * 0.7)
        self.cell_size = int(board_width / max(self.game_state.board.rows, self.game_state.board.cols))
        
        # Calcula o tamanho e posição do tabuleiro
        board_width = self.cell_size * self.game_state.board.cols
        board_height = self.cell_size * self.game_state.board.rows
        board_x = (screen_width - board_width) // 2
        board_y = (screen_height - board_height) // 3
        self.board_rect = pygame.Rect(board_x, board_y, board_width, board_height)
        
        # Calcula o tamanho e posição dos pratos disponíveis
        plate_size = self.cell_size * 0.8
        plate_spacing = plate_size * 1.2
        plates_width = plate_spacing * len(self.game_state.avl_plates.plates)
        plates_x = (screen_width - plates_width) // 2
        plates_y = board_y + board_height + 50
        
        self.plate_rects = []
        for i in range(len(self.game_state.avl_plates.plates)):
            x = plates_x + i * plate_spacing
            y = plates_y
            self.plate_rects.append(pygame.Rect(x, y, plate_size, plate_size))
    
    def render(self, selected_plate=-1):
        """Renderiza o jogo na tela.
        
        Args:
            selected_plate (int): Índice do prato selecionado.
        """
        # Limpa a tela
        self.screen.fill(self.colors['background'])
        
        # Renderiza o tabuleiro
        self._render_board()
        
        # Renderiza os pratos disponíveis
        self._render_available_plates(selected_plate)
        
        # Renderiza as informações do jogo
        self._render_game_info()
        
        # Renderiza as partículas e animações ativas
        self._render_animations()
        
        # Renderiza a mensagem de fim de jogo, se aplicável
        if self.game_state.game_over:
            self._render_game_over()
    
    def _render_board(self):
        """Renderiza o tabuleiro do jogo."""
        # Desenha o fundo do tabuleiro
        pygame.draw.rect(self.screen, self.colors['board'], self.board_rect)
        
        # Desenha as linhas da grade
        for i in range(self.game_state.board.rows + 1):
            y = self.board_rect.top + i * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid_line'],
                            (self.board_rect.left, y),
                            (self.board_rect.right, y), 2)
        
        for j in range(self.game_state.board.cols + 1):
            x = self.board_rect.left + j * self.cell_size
            pygame.draw.line(self.screen, self.colors['grid_line'],
                            (x, self.board_rect.top),
                            (x, self.board_rect.bottom), 2)
        
        # Desenha os pratos no tabuleiro
        for i in range(self.game_state.board.rows):
            for j in range(self.game_state.board.cols):
                if not self.game_state.board.is_empty(i, j):
                    plate = self.game_state.board.grid[i][j]
                    x = self.board_rect.left + j * self.cell_size
                    y = self.board_rect.top + i * self.cell_size
                    self._render_plate(x, y, plate)
    
    def _reorganize_plate(self, plate):
        """Reorganiza as fatias do prato para que fatias do mesmo tipo fiquem em posições consecutivas.
        
        Args:
            plate (list): Lista representando o prato com suas fatias.
            
        Returns:
            list: Lista reorganizada com fatias do mesmo tipo em posições consecutivas.
        """
        if not plate:
            return plate
            
        # Cria um dicionário para agrupar fatias por tipo
        slices_by_type = {}
        for slice_type in plate:
            if slice_type is not None:
                if slice_type not in slices_by_type:
                    slices_by_type[slice_type] = 0
                slices_by_type[slice_type] += 1
        
        # Cria um novo prato com as fatias agrupadas
        reorganized_plate = [None] * 8  # Um prato tem 8 posições
        current_position = 0
        
        # Adiciona cada tipo de fatia em posições consecutivas
        for slice_type, count in slices_by_type.items():
            for i in range(count):
                if current_position < 8:  # Garante que não exceda o tamanho do prato
                    reorganized_plate[current_position] = slice_type
                    current_position += 1
        
        return reorganized_plate
    
    def _render_plate(self, x, y, plate):
        """Renderiza um prato com suas fatias.
        
        Args:
            x (int): Coordenada x do prato.
            y (int): Coordenada y do prato.
            plate (list): Lista representando o prato com suas fatias.
        """
        # Desenha o fundo do prato com um efeito de brilho
        plate_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        pygame.draw.ellipse(self.screen, self.colors['plate'], plate_rect)
        
        # Adiciona um brilho suave ao prato
        glow_rect = plate_rect.inflate(-8, -8)
        pygame.draw.ellipse(self.screen, (255, 255, 255, 100), glow_rect)
        pygame.draw.ellipse(self.screen, self.colors['grid_line'], plate_rect, 2)
        
        # Desenha as fatias do prato
        if plate:
            # Calcula o centro do prato
            center_x = x + self.cell_size // 2
            center_y = y + self.cell_size // 2
            radius = self.cell_size // 2 - 4
            
            # Reorganiza as fatias para que fatias do mesmo tipo fiquem em posições consecutivas
            reorganized_plate = self._reorganize_plate(plate)
            
            # Desenha cada fatia como um setor de círculo com animação
            for i, slice_type in enumerate(reorganized_plate):
                if slice_type is not None:
                    # Calcula os ângulos inicial e final do setor com animação
                    # Adiciona uma pequena oscilação para dar vida às fatias
                    animation_offset = 0
                    if self.animations['active']:
                        # Cria um efeito de oscilação suave para cada fatia
                        animation_offset = math.sin(pygame.time.get_ticks() * 0.005 + i * 0.7) * 3
                    
                    start_angle = i * 45 + animation_offset  # 360 / 8 = 45 graus por fatia
                    end_angle = (i + 1) * 45 + animation_offset
                    
                    # Converte para radianos
                    start_rad = start_angle * 3.14159 / 180
                    end_rad = end_angle * 3.14159 / 180
                    
                    # Calcula os pontos do polígono que representa o setor
                    points = []
                    points.append((center_x, center_y))  # Centro do círculo
                    
                    # Adiciona pontos ao longo do arco
                    for angle in range(int(start_angle), int(end_angle) + 1, 5):
                        rad = angle * 3.14159 / 180
                        px = center_x + radius * pygame.math.Vector2(1, 0).rotate(-angle).x
                        py = center_y + radius * pygame.math.Vector2(1, 0).rotate(-angle).y
                        points.append((px, py))
                    
                    # Desenha o setor com um efeito de brilho
                    if len(points) > 2:
                        # Desenha a fatia principal
                        pygame.draw.polygon(self.screen, self.colors[f'slice_{slice_type}'], points)
                        
                        # Adiciona um brilho na borda da fatia
                        pygame.draw.polygon(self.screen, self.colors['grid_line'], points, 1)
                        
                        # Adiciona um efeito de brilho no centro da fatia
                        if self.animations['active']:
                            # Cria um ponto de brilho que se move ao longo da fatia
                            glow_pos = (center_x + (radius * 0.6) * pygame.math.Vector2(1, 0).rotate(-(start_angle + end_angle) / 2).x,
                                        center_y + (radius * 0.6) * pygame.math.Vector2(1, 0).rotate(-(start_angle + end_angle) / 2).y)
                            
                            # Desenha o brilho como um pequeno círculo
                            glow_size = 3 + math.sin(pygame.time.get_ticks() * 0.01) * 2
                            pygame.draw.circle(self.screen, (255, 255, 255, 150), glow_pos, glow_size)
    
    def _render_available_plates(self, selected_plate):
        """Renderiza os pratos disponíveis.
        
        Args:
            selected_plate (int): Índice do prato selecionado.
        """
        for i, rect in enumerate(self.plate_rects):
            if i < len(self.game_state.avl_plates.plates):
                plate = self.game_state.avl_plates.plates[i]
                
                # Destaca o prato selecionado
                if i == selected_plate:
                    highlight_rect = rect.inflate(10, 10)
                    pygame.draw.rect(self.screen, self.colors['highlight'], highlight_rect)
                
                # Desenha o prato
                self._render_plate(rect.x, rect.y, plate)
                
                # Desenha o índice do prato
                text = self.fonts['small'].render(str(i + 1), True, self.colors['text'])
                text_rect = text.get_rect(center=(rect.centerx, rect.bottom + 15))
                self.screen.blit(text, text_rect)
    
    def _render_game_info(self):
        """Renderiza as informações do jogo."""
        # Renderiza o título
        title = self.fonts['title'].render("Cake Sorting Puzzle", True, self.colors['text'])
        title_rect = title.get_rect(centerx=self.screen.get_width() // 2, top=10)
        self.screen.blit(title, title_rect)
        
        # Renderiza o nível
        level_text = self.fonts['medium'].render(f"Nível: {self.game_state.level}", True, self.colors['text'])
        level_rect = level_text.get_rect(left=10, top=10)
        self.screen.blit(level_text, level_rect)
        
        # Renderiza a pontuação
        score_text = self.fonts['medium'].render(
            f"Pontuação: {self.game_state.score}/{self.game_state.target_score}",
            True, self.colors['text'])
        score_rect = score_text.get_rect(left=10, top=level_rect.bottom + 5)
        self.screen.blit(score_text, score_rect)
        
        # Renderiza o número de movimentos
        moves_text = self.fonts['medium'].render(f"Movimentos: {self.game_state.moves}", True, self.colors['text'])
        moves_rect = moves_text.get_rect(left=10, top=score_rect.bottom + 5)
        self.screen.blit(moves_text, moves_rect)
        
        # Renderiza as instruções
        instructions = [
            "Instruções:",
            "- Clique em um prato disponível para selecioná-lo",
            "- Clique em uma posição vazia no tabuleiro para colocá-lo",
            "- Pressione ESC para voltar ao menu",
            "- Pressione S para resolver automaticamente",
            "- Pressione A para ativar/desativar solução automática"
        ]
        
        y = self.screen.get_height() - 120
        for instruction in instructions:
            text = self.fonts['small'].render(instruction, True, self.colors['text'])
            rect = text.get_rect(left=10, top=y)
            self.screen.blit(text, rect)
            y += 20
    
    def _render_game_over(self):
        """Renderiza a mensagem de fim de jogo."""
        # Cria um retângulo semi-transparente para o fundo
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Preto com 150 de transparência
        self.screen.blit(overlay, (0, 0))
        
        # Renderiza a mensagem principal com animação
        if self.game_state.win:
            message = "Parabéns! Você venceu!"
            # Adiciona partículas de celebração se ganhou
            if len(self.animations['particles']) < 100 and self.animations['active']:
                self._add_celebration_particles()
        else:
            message = "Fim de Jogo"
        
        # Adiciona efeito de pulsação ao texto
        pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)
        font_size = int(36 * pulse)
        pulsing_font = pygame.font.SysFont('Arial', font_size, bold=True)
        
        text = pulsing_font.render(message, True, (255, 192, 203))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 20))
        self.screen.blit(text, text_rect)
        
        # Renderiza a pontuação final
        score_text = self.fonts['large'].render(f"Pontuação: {self.game_state.score}", True, (255, 182, 193))
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, text_rect.bottom + 30))
        self.screen.blit(score_text, score_rect)
        
        # Renderiza a instrução para voltar ao menu
        instruction = self.fonts['medium'].render("Pressione ESC para voltar ao menu", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.screen.get_width() // 2, score_rect.bottom + 30))
        self.screen.blit(instruction, instruction_rect)
    
    def get_plate_at_pos(self, pos):
        """Retorna o índice do prato na posição especificada.
        
        Args:
            pos (tuple): Posição (x, y) a verificar.
            
        Returns:
            int: Índice do prato ou -1 se não houver prato na posição.
        """
        for i, rect in enumerate(self.plate_rects):
            if i < len(self.game_state.avl_plates.plates) and rect.collidepoint(pos):
                return i
        return -1
    
    def get_board_pos_at_pos(self, pos):
        """Retorna a posição do tabuleiro na posição especificada.
        
        Args:
            pos (tuple): Posição (x, y) a verificar.
            
        Returns:
            tuple: Posição (linha, coluna) no tabuleiro ou None se fora do tabuleiro.
        """
        if self.board_rect.collidepoint(pos):
            # Calcula a posição relativa dentro do tabuleiro
            rel_x = pos[0] - self.board_rect.left
            rel_y = pos[1] - self.board_rect.top
            
            # Converte para coordenadas do tabuleiro
            col = rel_x // self.cell_size
            row = rel_y // self.cell_size
            
            # Verifica se está dentro dos limites do tabuleiro
            if 0 <= row < self.game_state.board.rows and 0 <= col < self.game_state.board.cols:
                return (row, col)
        
        return None
        
    def _render_animations(self):
        """Renderiza todas as animações ativas e partículas."""
        # Renderiza e atualiza todas as partículas
        particles_to_keep = []
        
        for particle in self.animations['particles']:
            # Atualiza a posição da partícula
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            # Aplica gravidade
            particle['vy'] += 0.1
            
            # Reduz o tamanho gradualmente
            size = particle['size'] * (particle['life'] / particle['max_life'])
            
            # Desenha a partícula
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color = list(particle['color'])
                if len(color) == 3:
                    color.append(alpha)
                else:
                    color[3] = alpha
                
                # Desenha diferentes formas de partículas
                if particle.get('type') == 'star':
                    # Desenha uma estrela
                    points = []
                    for i in range(10):
                        angle = i * 36  # 360 / 10 = 36 graus
                        radius = size if i % 2 == 0 else size / 2
                        px = particle['x'] + radius * pygame.math.Vector2(1, 0).rotate(-angle).x
                        py = particle['y'] + radius * pygame.math.Vector2(1, 0).rotate(-angle).y
                        points.append((px, py))
                    pygame.draw.polygon(self.screen, color, points)
                elif particle.get('type') == 'heart':
                    # Simula um coração com círculos
                    pygame.draw.circle(self.screen, color, (int(particle['x'] - size/2), int(particle['y'] - size/2)), int(size/2))
                    pygame.draw.circle(self.screen, color, (int(particle['x'] + size/2), int(particle['y'] - size/2)), int(size/2))
                    points = [
                        (particle['x'] - size, particle['y'] - size/2),
                        (particle['x'] + size, particle['y'] - size/2),
                        (particle['x'], particle['y'] + size)
                    ]
                    pygame.draw.polygon(self.screen, color, points)
                else:
                    # Desenha um círculo padrão
                    pygame.draw.circle(self.screen, color, (int(particle['x']), int(particle['y'])), int(size))
                
                particles_to_keep.append(particle)
        
        # Atualiza a lista de partículas
        self.animations['particles'] = particles_to_keep
        
        # Renderiza as animações de movimento de fatias
        slice_animations_to_keep = []
        for anim in self.animations.get('slice_movements', []):
            # Atualiza o progresso da animação
            anim['progress'] += 0.05
            
            if anim['progress'] <= 1.0:
                # Calcula a posição atual usando interpolação
                current_x = anim['start_x'] + (anim['end_x'] - anim['start_x']) * anim['progress']
                current_y = anim['start_y'] + (anim['end_y'] - anim['start_y']) * anim['progress']
                
                # Desenha a fatia em movimento
                color = self.colors[f'slice_{anim["slice_type"]}'] 
                pygame.draw.circle(self.screen, color, (int(current_x), int(current_y)), 10)
                
                # Adiciona um rastro de partículas
                if pygame.time.get_ticks() % 3 == 0:
                    self.animations['particles'].append({
                        'x': current_x,
                        'y': current_y,
                        'vx': (pygame.time.get_ticks() % 6 - 3) * 0.3,
                        'vy': (pygame.time.get_ticks() % 6 - 3) * 0.3,
                        'color': color,
                        'size': 3,
                        'life': 20,
                        'max_life': 20
                    })
                
                slice_animations_to_keep.append(anim)
        
        # Atualiza a lista de animações de fatias
        self.animations['slice_movements'] = slice_animations_to_keep
    
    def add_cake_complete_animation(self, x, y):
        """Adiciona uma animação de bolo completo na posição especificada.
        
        Args:
            x (int): Coordenada x no tabuleiro.
            y (int): Coordenada y no tabuleiro.
        """
        if not self.animations['active']:
            return
            
        # Converte coordenadas do tabuleiro para coordenadas da tela
        screen_x = self.board_rect.left + y * self.cell_size + self.cell_size // 2
        screen_y = self.board_rect.top + x * self.cell_size + self.cell_size // 2
        
        # Adiciona partículas para celebrar o bolo completo
        for _ in range(50):
            angle = pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() % 360)
            speed = 2 + pygame.math.Vector2(1, 0).length() * 3
            
            # Cores vibrantes em tons de rosa
            colors = [
                (255, 20, 147),   # Rosa profundo
                (255, 105, 180),  # Rosa quente
                (255, 182, 193),  # Rosa claro
                (255, 0, 255),    # Magenta
                (238, 130, 238)   # Violeta
            ]
            
            # Adiciona diferentes tipos de partículas para mais variedade
            particle_types = ['circle', 'star', 'heart']
            
            particle = {
                'x': screen_x,
                'y': screen_y,
                'vx': angle.x * speed * pygame.math.Vector2(1, 0).normalize().x,
                'vy': angle.y * speed * pygame.math.Vector2(1, 0).normalize().y,
                'color': colors[pygame.time.get_ticks() % len(colors)],
                'size': 3 + pygame.math.Vector2(1, 0).length() * 2,
                'life': 60,
                'max_life': 60,
                'type': particle_types[pygame.time.get_ticks() % len(particle_types)]
            }
            
            self.animations['particles'].append(particle)
            
    def add_slice_movement_animation(self, source_x, source_y, target_x, target_y, slice_type):
        """Adiciona uma animação de movimento de fatia entre dois pratos.
        
        Args:
            source_x (int): Coordenada x do prato de origem no tabuleiro.
            source_y (int): Coordenada y do prato de origem no tabuleiro.
            target_x (int): Coordenada x do prato de destino no tabuleiro.
            target_y (int): Coordenada y do prato de destino no tabuleiro.
            slice_type (int): Tipo da fatia que está sendo movida.
        """
        if not self.animations['active']:
            return
            
        # Converte coordenadas do tabuleiro para coordenadas da tela
        start_x = self.board_rect.left + source_y * self.cell_size + self.cell_size // 2
        start_y = self.board_rect.top + source_x * self.cell_size + self.cell_size // 2
        end_x = self.board_rect.left + target_y * self.cell_size + self.cell_size // 2
        end_y = self.board_rect.top + target_x * self.cell_size + self.cell_size // 2
        
        # Inicializa a lista de animações de fatias se não existir
        if 'slice_movements' not in self.animations:
            self.animations['slice_movements'] = []
        
        # Adiciona a animação de movimento
        self.animations['slice_movements'].append({
            'start_x': start_x,
            'start_y': start_y,
            'end_x': end_x,
            'end_y': end_y,
            'slice_type': slice_type,
            'progress': 0.0  # 0.0 a 1.0 para controlar o progresso da animação
        })
    
    def _add_celebration_particles(self):
        """Adiciona partículas de celebração por toda a tela."""
        for _ in range(5):
            # Posição aleatória na tela
            x = pygame.time.get_ticks() % self.screen.get_width()
            y = pygame.time.get_ticks() % self.screen.get_height()
            
            # Velocidade aleatória
            vx = (pygame.time.get_ticks() % 10) - 5
            vy = -5 - (pygame.time.get_ticks() % 5)
            
            # Cores vibrantes em tons de rosa
            colors = [
                (255, 20, 147),   # Rosa profundo
                (255, 105, 180),  # Rosa quente
                (255, 182, 193),  # Rosa claro
                (255, 0, 255),    # Magenta
                (238, 130, 238)   # Violeta
            ]
            
            particle = {
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'color': colors[pygame.time.get_ticks() % len(colors)],
                'size': 3 + (pygame.time.get_ticks() % 5),
                'life': 60 + (pygame.time.get_ticks() % 30),
                'max_life': 60 + (pygame.time.get_ticks() % 30)
            }
            
            self.animations['particles'].append(particle)