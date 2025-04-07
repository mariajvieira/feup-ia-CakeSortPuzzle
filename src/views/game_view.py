import pygame
import os
import math


class GameView:
    
    def __init__(self, screen, game_state, game_controller=None):
        self.screen = screen
        self.game_state = game_state
        self.game_controller = game_controller
        
        self.colors = {
            'background': (255, 240, 245), 
            'board': (255, 228, 240),      
            'grid_line': (219, 112, 147), 
            'text': (199, 21, 133),        
            'highlight': (255, 105, 180, 100), 
            'plate': (255, 240, 245),     
            'slice_1': (255, 20, 147),    
            'slice_2': (255, 165, 0),     
            'slice_3': (50, 205, 50),    
            'slice_4': (30, 144, 255),  
            'slice_5': (255, 215, 0),    
            'slice_6': (138, 43, 226),   
            'slice_7': (220, 20, 60),    
            'slice_8': (0, 206, 209),    
            'slice_9': (255, 105, 180)    
            
        }
        
        self.animations = {
            'active': True,               
            'plate_move_duration': 20,   
            'cake_complete_duration': 30,  
            'current_animations': [],   
            'particles': []              
        }

        
        pygame.font.init()
        self.fonts = {
            'small': pygame.font.SysFont('Arial', 14),
            'medium': pygame.font.SysFont('Arial', 20),
            'large': pygame.font.SysFont('Arial', 28),
            'title': pygame.font.SysFont('Arial', 36, bold=True)
        }
        
        self._calculate_layout()
    
    def _calculate_layout(self):
        screen_width, screen_height = self.screen.get_size()
        
        board_width = min(screen_width * 0.7, screen_height * 0.7)
        self.cell_size = int(board_width / max(self.game_state.board.rows, self.game_state.board.cols))
        
        board_width = self.cell_size * self.game_state.board.cols
        board_height = self.cell_size * self.game_state.board.rows
        board_x = (screen_width - board_width) // 2
        board_y = (screen_height - board_height) // 3
        self.board_rect = pygame.Rect(board_x, board_y, board_width, board_height)
        
        plate_size = self.cell_size * 0.8
        plate_spacing = plate_size * 1.2
        plates_width = plate_spacing * len(self.game_state.avl_plates.visible_plates)
        plates_x = (screen_width - plates_width) // 2
        plates_y = board_y + board_height + 50
        
        self.plate_rects = []
        for i in range(len(self.game_state.avl_plates.visible_plates)):
            x = plates_x + i * plate_spacing
            y = plates_y
            self.plate_rects.append(pygame.Rect(x, y, plate_size, plate_size))
    
    def render(self, selected_plate=-1):
        self.screen.fill(self.colors['background'])
        
        self._render_board()
        
        self._render_available_plates(selected_plate)
        
        self._render_game_info()
        
        self._render_animations()
        
        if self.game_state.game_over:
            self._render_game_over()
    
    def _render_board(self):
        pygame.draw.rect(self.screen, self.colors['board'], self.board_rect)
        
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
        
        for i in range(self.game_state.board.rows):
            for j in range(self.game_state.board.cols):
                if not self.game_state.board.is_empty(i, j):
                    plate = self.game_state.board.grid[i][j]
                    x = self.board_rect.left + j * self.cell_size
                    y = self.board_rect.top + i * self.cell_size
                    self._render_plate(x, y, plate)
    
    def _reorganize_plate(self, plate):
        if not plate:
            return plate
            
        slices_by_type = {}
        for slice_type in plate:
            if slice_type is not None:
                if slice_type not in slices_by_type:
                    slices_by_type[slice_type] = 0
                slices_by_type[slice_type] += 1
        
        reorganized_plate = [None] * 8 
        current_position = 0
        
        for slice_type, count in slices_by_type.items():
            for i in range(count):
                if current_position < 8:  
                    reorganized_plate[current_position] = slice_type
                    current_position += 1
        
        return reorganized_plate
    
    def _render_plate(self, x, y, plate):
        plate_rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        pygame.draw.ellipse(self.screen, self.colors['plate'], plate_rect)
        
        glow_rect = plate_rect.inflate(-8, -8)
        pygame.draw.ellipse(self.screen, (255, 255, 255, 100), glow_rect)
        pygame.draw.ellipse(self.screen, self.colors['grid_line'], plate_rect, 2)
        
        if plate:
            center_x = x + self.cell_size // 2
            center_y = y + self.cell_size // 2
            radius = self.cell_size // 2 - 4
            
            reorganized_plate = self._reorganize_plate(plate)
            
            for i, slice_type in enumerate(reorganized_plate):
                if slice_type is not None:
                    animation_offset = 0
                    if self.animations['active']:
                        animation_offset = math.sin(pygame.time.get_ticks() * 0.005 + i * 0.7) * 3
                    
                    start_angle = i * 45 + animation_offset  # 360 / 8 = 45 graus por fatia
                    end_angle = (i + 1) * 45 + animation_offset
                    
                    start_rad = start_angle * 3.14159 / 180
                    end_rad = end_angle * 3.14159 / 180
                    
                    points = []
                    points.append((center_x, center_y)) 
                    
                    for angle in range(int(start_angle), int(end_angle) + 1, 5):
                        rad = angle * 3.14159 / 180
                        px = center_x + radius * pygame.math.Vector2(1, 0).rotate(-angle).x
                        py = center_y + radius * pygame.math.Vector2(1, 0).rotate(-angle).y
                        points.append((px, py))
                    
                    if len(points) > 2:
                        pygame.draw.polygon(self.screen, self.colors[f'slice_{slice_type}'], points)
                        
                        pygame.draw.polygon(self.screen, self.colors['grid_line'], points, 1)
                        
                        if self.animations['active']:
                            glow_pos = (center_x + (radius * 0.6) * pygame.math.Vector2(1, 0).rotate(-(start_angle + end_angle) / 2).x,
                                        center_y + (radius * 0.6) * pygame.math.Vector2(1, 0).rotate(-(start_angle + end_angle) / 2).y)
                            
                            glow_size = 3 + math.sin(pygame.time.get_ticks() * 0.01) * 2
                            pygame.draw.circle(self.screen, (255, 255, 255, 150), glow_pos, glow_size)
    
    def _render_available_plates(self, selected_plate):
        for i, rect in enumerate(self.plate_rects):
            if i < len(self.game_state.avl_plates.visible_plates):
                plate = self.game_state.avl_plates.visible_plates[i]
                
                if i == selected_plate:
                    highlight_rect = rect.inflate(10, 10)
                    pygame.draw.rect(self.screen, self.colors['highlight'], highlight_rect)
                
                self._render_plate(rect.x, rect.y, plate)
                
                text = self.fonts['small'].render(str(i + 1), True, self.colors['text'])
                text_rect = text.get_rect(center=(rect.centerx, rect.bottom + 15))
                self.screen.blit(text, text_rect)
    
    def _render_game_info(self):
        title = self.fonts['title'].render("Cake Sorting Puzzle", True, self.colors['text'])
        title_rect = title.get_rect(centerx=self.screen.get_width() // 2, top=10)
        self.screen.blit(title, title_rect)
                
        score_text = self.fonts['medium'].render(
            f"Bolos concluídos: {self.game_state.score}",
            True, self.colors['text'])
        score_rect = score_text.get_rect(left=10, top=10)
        self.screen.blit(score_text, score_rect)
        
        moves_text = self.fonts['medium'].render(f"Movimentos: {self.game_state.moves}", True, self.colors['text'])
        moves_rect = moves_text.get_rect(left=10, top=score_rect.bottom + 5)
        self.screen.blit(moves_text, moves_rect)
        
        plates_remaining = self.game_state.avl_plates.get_remaining_plates()
        total_plates = self.game_state.avl_plates.total_plate_limit
        plates_text = self.fonts['medium'].render(f"Pratos Restantes: {plates_remaining}/{total_plates}", True, self.colors['text'])
        plates_rect = plates_text.get_rect(left=10, top=moves_rect.bottom + 5)
        self.screen.blit(plates_text, plates_rect)
        
        if (
            hasattr(self, 'game_controller')
            and self.game_controller
            and getattr(self.game_controller, 'game_mode', 'human') == 'ai'
        ):
            algorithm_text = self.fonts['medium'].render(
                f"Algoritmo: {self.game_controller.algorithm.upper()}", 
                True, self.colors['text']
            )
            algorithm_rect = algorithm_text.get_rect(right=self.screen.get_width() - 10, top=10)
            self.screen.blit(algorithm_text, algorithm_rect)

            if self.game_controller.solution_time > 0:
                time_text = self.fonts['medium'].render(
                    f"Tempo de solução: {self.game_controller.solution_time:.3f}s", 
                    True, self.colors['text']
                )
                time_rect = time_text.get_rect(right=self.screen.get_width() - 10, top=algorithm_rect.bottom + 5)
                self.screen.blit(time_text, time_rect)
        
        instructions = [
            "Instruções:",
            "- Clique em um prato disponível para selecioná-lo",
            "- Clique em uma posição vazia no tabuleiro para colocá-lo",
            "- Pressione ESC para voltar ao menu",
            "- Pressione S para resolver automaticamente",
            "- Pressione A para ativar/desativar solução automática",
            f"- Complete todos os {total_plates} pratos sem preencher o tabuleiro para vencer"
        ]
        
        y = self.screen.get_height() - 140
        for instruction in instructions:
            text = self.fonts['small'].render(instruction, True, self.colors['text'])
            rect = text.get_rect(left=10, top=y)
            self.screen.blit(text, rect)
            y += 20
    
    def _render_game_over(self):
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        self.screen.blit(overlay, (0, 0))
        
        if self.game_state.win:
            message = "Parabéns! Você venceu!"
            if len(self.animations['particles']) < 100 and self.animations['active']:
                self._add_celebration_particles()
        else:
            message = "Perdeu :( , fim do jogo"
        
        pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.005)
        font_size = int(36 * pulse)
        pulsing_font = pygame.font.SysFont('Arial', font_size, bold=True)
        
        text = pulsing_font.render(message, True, (255, 192, 203))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 20))
        self.screen.blit(text, text_rect)
        
        score_text = self.fonts['large'].render(f"Bolos concluídos: {self.game_state.score}", True, (255, 182, 193))
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, text_rect.bottom + 30))
        self.screen.blit(score_text, score_rect)
        
        instruction = self.fonts['medium'].render("Pressione ESC para voltar ao menu", True, (255, 255, 255))
        instruction_rect = instruction.get_rect(center=(self.screen.get_width() // 2, score_rect.bottom + 30))
        self.screen.blit(instruction, instruction_rect)
    
    def get_plate_at_pos(self, pos):
        for i, rect in enumerate(self.plate_rects):
            if i < len(self.game_state.avl_plates.visible_plates) and rect.collidepoint(pos):
                return i
        return -1
    
    def get_board_pos_at_pos(self, pos):
        if self.board_rect.collidepoint(pos):
            rel_x = pos[0] - self.board_rect.left
            rel_y = pos[1] - self.board_rect.top
            
            col = rel_x // self.cell_size
            row = rel_y // self.cell_size
            
            if 0 <= row < self.game_state.board.rows and 0 <= col < self.game_state.board.cols:
                return (row, col)
        
        return None
        
    def _render_animations(self):
        particles_to_keep = []
        
        for particle in self.animations['particles']:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            particle['vy'] += 0.1
            
            size = particle['size'] * (particle['life'] / particle['max_life'])
            
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                color = list(particle['color'])
                if len(color) == 3:
                    color.append(alpha)
                else:
                    color[3] = alpha
                
                if particle.get('type') == 'star':
                    points = []
                    for i in range(10):
                        angle = i * 36  
                        radius = size if i % 2 == 0 else size / 2
                        px = particle['x'] + radius * pygame.math.Vector2(1, 0).rotate(-angle).x
                        py = particle['y'] + radius * pygame.math.Vector2(1, 0).rotate(-angle).y
                        points.append((px, py))
                    pygame.draw.polygon(self.screen, color, points)
                elif particle.get('type') == 'heart':
                    pygame.draw.circle(self.screen, color, (int(particle['x'] - size/2), int(particle['y'] - size/2)), int(size/2))
                    pygame.draw.circle(self.screen, color, (int(particle['x'] + size/2), int(particle['y'] - size/2)), int(size/2))
                    points = [
                        (particle['x'] - size, particle['y'] - size/2),
                        (particle['x'] + size, particle['y'] - size/2),
                        (particle['x'], particle['y'] + size)
                    ]
                    pygame.draw.polygon(self.screen, color, points)
                else:
                    pygame.draw.circle(self.screen, color, (int(particle['x']), int(particle['y'])), int(size))
                
                particles_to_keep.append(particle)
        
        self.animations['particles'] = particles_to_keep
        
        slice_animations_to_keep = []
        for anim in self.animations.get('slice_movements', []):
            anim['progress'] += 0.05
            
            if anim['progress'] <= 1.0:
                current_x = anim['start_x'] + (anim['end_x'] - anim['start_x']) * anim['progress']
                current_y = anim['start_y'] + (anim['end_y'] - anim['start_y']) * anim['progress']
                
                color = self.colors[f'slice_{anim["slice_type"]}'] 
                pygame.draw.circle(self.screen, color, (int(current_x), int(current_y)), 10)
                
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
        
        self.animations['slice_movements'] = slice_animations_to_keep
    
    def add_cake_complete_animation(self, x, y):
        if not self.animations['active']:
            return
            
        screen_x = self.board_rect.left + y * self.cell_size + self.cell_size // 2
        screen_y = self.board_rect.top + x * self.cell_size + self.cell_size // 2
        
        for _ in range(50):
            angle = pygame.math.Vector2(1, 0).rotate(pygame.time.get_ticks() % 360)
            speed = 2 + pygame.math.Vector2(1, 0).length() * 3
            
            colors = [
                (255, 20, 147),  
                (255, 105, 180), 
                (255, 182, 193),
                (255, 0, 255), 
                (238, 130, 238)  
            ]
            
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
        if not self.animations['active']:
            return
            
        start_x = self.board_rect.left + source_y * self.cell_size + self.cell_size // 2
        start_y = self.board_rect.top + source_x * self.cell_size + self.cell_size // 2
        end_x = self.board_rect.left + target_y * self.cell_size + self.cell_size // 2
        end_y = self.board_rect.top + target_x * self.cell_size + self.cell_size // 2
        
        if 'slice_movements' not in self.animations:
            self.animations['slice_movements'] = []
        
        self.animations['slice_movements'].append({
            'start_x': start_x,
            'start_y': start_y,
            'end_x': end_x,
            'end_y': end_y,
            'slice_type': slice_type,
            'progress': 0.0  
        })
    
    def _add_celebration_particles(self):
        for _ in range(5):
            x = pygame.time.get_ticks() % self.screen.get_width()
            y = pygame.time.get_ticks() % self.screen.get_height()
            
            vx = (pygame.time.get_ticks() % 10) - 5
            vy = -5 - (pygame.time.get_ticks() % 5)
            
            colors = [
                (255, 20, 147),  
                (255, 105, 180),  
                (255, 182, 193),  
                (255, 0, 255),   
                (238, 130, 238)   
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