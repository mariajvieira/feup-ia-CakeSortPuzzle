import pygame
import math
import random
from pygame import gfxdraw


class MenuView:
    
    def __init__(self, screen, game_controller):
        self.screen = screen
        self.game_controller = game_controller
        self.screen_width, self.screen_height = self.screen.get_size()
        
        self.colors = {
            'background_top': (25, 10, 44),
            'background_bottom': (80, 10, 80),
            'text': (255, 255, 255),
            'text_shadow': (100, 50, 150, 128),
            'button': (140, 50, 200),
            'button_hover': (200, 70, 220),
            'button_text': (255, 255, 255),
            'selected': (255, 113, 206),
            'title_gradient_1': (255, 113, 206),
            'title_gradient_2': (126, 113, 255),
            'particle': (255, 255, 255, 150),
            'glow': (200, 100, 255, 30),
            'human_mode': (50, 205, 50),
            'ai_mode': (0, 191, 255),
            'slider_bg': (80, 30, 100),
            'slider_fg': (200, 70, 220),
            'slider_handle': (255, 113, 206)
        }
        
        pygame.font.init()
        available_fonts = pygame.font.get_fonts()
        
        title_font = 'arialrounded' if 'arialrounded' in available_fonts else 'arial'
        main_font = 'arialrounded' if 'arialrounded' in available_fonts else 'arial'
        
        self.fonts = {
            'small': pygame.font.SysFont(main_font, 16),
            'medium': pygame.font.SysFont(main_font, 24),
            'large': pygame.font.SysFont(main_font, 28, bold=True),
            'title': pygame.font.SysFont(title_font, 60, bold=True)
        }
        
        self.selected_level = 1
        self.selected_algorithm = 'bfs'
        self.selected_game_mode = 'ai'
        
        self.board_rows = 2
        self.board_cols = 2
        self.plate_count = 6
        
        self._init_buttons()
        
        self.particles = []
        self._init_particles(50)
        
        self.animations = {
            'title_wave': 0,
            'glow_angle': 0,
            'button_pulse': 0
        }
        
        self.assets = self._load_assets()
    
    def _load_assets(self):
        assets = {}
        try:
            import os
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            particle_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'particle.svg'))
            glow_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'glow.svg'))
            play_button_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'play_button.svg'))
            cake_icon_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'cake_icon.svg'))
            
            assets['particle'] = pygame.transform.scale(particle_svg, (20, 20))
            assets['glow'] = pygame.transform.scale(glow_svg, (400, 400))
            assets['play_button'] = pygame.transform.scale(play_button_svg, (50, 50))
            assets['cake_icon'] = pygame.transform.scale(cake_icon_svg, (60, 60))
        except Exception as e:
            print(f"Erro ao carregar assets: {e}")
            assets['particle'] = pygame.Surface((20, 20), pygame.SRCALPHA)
            assets['glow'] = pygame.Surface((400, 400), pygame.SRCALPHA)
            assets['play_button'] = pygame.Surface((50, 50), pygame.SRCALPHA)
            assets['cake_icon'] = pygame.Surface((60, 60), pygame.SRCALPHA)
        
        return assets
    
    def _init_particles(self, count):
        for _ in range(count):
            particle = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.uniform(1, 3),
                'speed': random.uniform(0.2, 1.0),
                'angle': random.uniform(0, 2 * math.pi),
                'color': (255, 255, 255, random.randint(30, 150))
            }
            self.particles.append(particle)
    
    def _init_buttons(self):
        button_width = int(self.screen_width * 0.18)
        button_height = int(self.screen_height * 0.055)
        button_spacing = int(self.screen_height * 0.05)  
        
        header_height = int(self.screen_height * 0.18)
        footer_height = int(self.screen_height * 0.20)
        content_height = self.screen_height - header_height - footer_height
        
        center_x = self.screen_width // 2
        content_start_y = header_height + int(content_height * 0.05)
        
        algorithm_buttons = {}
        algorithms = ['bfs', 'dfs', 'ids', 'ucs', 'greedy', 'astar', 'wastar']
        alg_width = int(self.screen_width * 0.06)
        alg_spacing = int(self.screen_width * 0.08)
        alg_start_x = center_x - ((7 * alg_width + 6 * (alg_spacing - alg_width)) // 2)
        alg_y = content_start_y + int(content_height * 0.10) 
        
        for i, alg in enumerate(algorithms):
            x = alg_start_x + i * alg_spacing
            algorithm_buttons[alg] = pygame.Rect(x, alg_y, alg_width, button_height)
            
        game_mode_buttons = {}
        modes = ['ai', 'human']
        mode_width = int(self.screen_width * 0.12)
        mode_spacing = int(self.screen_width * 0.15)
        mode_start_x = center_x - mode_spacing // 2
        mode_y = alg_y + button_height + button_spacing
        
        for i, mode in enumerate(modes):
            x = mode_start_x + i * mode_spacing - mode_width // 2
            game_mode_buttons[mode] = pygame.Rect(x, mode_y, mode_width, button_height)
        
        config_width = int(self.screen_width * 0.15)
        config_x = self.screen_width - config_width - 20
        config_y = mode_y + button_height + button_spacing
        
        control_height = int(button_height * 0.8)
        control_spacing = int(button_height * 1.2)
        button_small = int(button_height * 0.7)
        
        rows_value_rect = pygame.Rect(config_x + config_width//2 - button_small, config_y, button_small*2, control_height)
        rows_minus = pygame.Rect(config_x, config_y, button_small, button_small)
        rows_plus = pygame.Rect(config_x + config_width - button_small, config_y, button_small, button_small)
        
        cols_value_rect = pygame.Rect(config_x + config_width//2 - button_small, config_y + control_spacing, button_small*2, control_height)
        cols_minus = pygame.Rect(config_x, config_y + control_spacing, button_small, button_small)
        cols_plus = pygame.Rect(config_x + config_width - button_small, config_y + control_spacing, button_small, button_small)
        
        plates_value_rect = pygame.Rect(config_x + config_width//2 - button_small, config_y + 2 * control_spacing, button_small*2, control_height)
        plates_minus = pygame.Rect(config_x, config_y + 2 * control_spacing, button_small, button_small)
        plates_plus = pygame.Rect(config_x + config_width - button_small, config_y + 2 * control_spacing, button_small, button_small)
        
        rows_slider = rows_value_rect
        cols_slider = cols_value_rect
        plates_slider = plates_value_rect
        
        file_buttons = {}
        actions = ['load', 'save']
        file_width = int(self.screen_width * 0.12)
        file_spacing = int(self.screen_width * 0.15)
        file_start_x = center_x - file_spacing // 2
        file_y = config_y + 2 * button_height + int(button_spacing * 0.7) 
        
        for i, action in enumerate(actions):
            x = file_start_x + i * file_spacing - file_width // 2
            file_buttons[action] = pygame.Rect(x, file_y, file_width, button_height)
        
        action_y = file_y + button_height + int(button_spacing * 0.5)  
        
        start_button = pygame.Rect(
            center_x - button_width // 2,
            action_y,
            button_width, 
            button_height + 5
        )
        
        exit_button = pygame.Rect(
            center_x - button_width // 2,
            action_y + button_height + 10,
            button_width, 
            button_height
        )
        
        self.buttons = {
            'algorithms': algorithm_buttons,
            'game_modes': game_mode_buttons,
            'start': start_button,
            'exit': exit_button,
            'files': file_buttons,
            'board_config': {
                'rows_slider': rows_slider,
                'rows_minus': rows_minus,
                'rows_plus': rows_plus,
                'cols_slider': cols_slider,
                'cols_minus': cols_minus,
                'cols_plus': cols_plus,
                'plates_slider': plates_slider,
                'plates_minus': plates_minus,
                'plates_plus': plates_plus
            }
        }
        
        self.layout = {
            'header': pygame.Rect(0, 0, self.screen_width, header_height),
            'content': pygame.Rect(0, header_height, self.screen_width, content_height),
            'footer': pygame.Rect(0, self.screen_height - footer_height, self.screen_width, footer_height),
            'algorithm_section': pygame.Rect(0, alg_y - 40, self.screen_width, button_height + 60),
            'game_mode_section': pygame.Rect(0, mode_y - 40, self.screen_width, button_height + 60),
            'board_config_section': pygame.Rect(self.screen_width - 200, mode_y - 40, 180, 3 * button_height + 60),
            'file_section': pygame.Rect(0, file_y - 40, self.screen_width, button_height + 60),
            'action_section': pygame.Rect(0, action_y - 20, self.screen_width, 2*button_height + 40)
        }

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_mouse_click(event.pos)
    
    def _handle_mouse_click(self, pos):
        for alg, rect in self.buttons['algorithms'].items():
            if rect.collidepoint(pos) and self.selected_game_mode == 'ai':
                self.selected_algorithm = alg
                return
                
        for mode, rect in self.buttons['game_modes'].items():
            if rect.collidepoint(pos):
                self.selected_game_mode = mode
                if mode == 'human':
                    self._disable_algorithm_buttons()
                else:
                    self._enable_algorithm_buttons()
                return
        
        board_config = self.buttons['board_config']
        
        if board_config['rows_minus'].collidepoint(pos) and self.board_rows > 2:
            self.board_rows -= 1
            return
        if board_config['rows_plus'].collidepoint(pos) and self.board_rows < 6:
            self.board_rows += 1
            return
            
        if board_config['cols_minus'].collidepoint(pos) and self.board_cols > 2:
            self.board_cols -= 1
            return
        if board_config['cols_plus'].collidepoint(pos) and self.board_cols < 6:
            self.board_cols += 1
            return
            
        if board_config['plates_minus'].collidepoint(pos) and self.plate_count > 3:
            self.plate_count -= 1
            return
        if board_config['plates_plus'].collidepoint(pos) and self.plate_count < 20:
            self.plate_count += 1
            return
        
        if self.buttons['start'].collidepoint(pos):
            self.game_controller.start_game(self.selected_level, self.selected_algorithm, self.selected_game_mode,
                                           board_rows=self.board_rows,
                                           board_cols=self.board_cols,
                                           plate_count=self.plate_count)
            return
        
        if self.buttons['exit'].collidepoint(pos):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
        
        for action, rect in self.buttons['files'].items():
            if rect.collidepoint(pos):
                if action == 'load':
                    self._handle_load_state()
                elif action == 'save':
                    self._handle_save_state()
                return
    
    def _handle_load_state(self):
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.askopenfilename(
            title="Carregar Estado do Jogo",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            from src.models.game_state import GameState
            loaded_state = GameState.load_from_file(file_path)
            
            if loaded_state:
                self.game_controller.start_game_with_state(loaded_state, self.selected_algorithm, self.selected_game_mode)

    def _handle_save_state(self):
        if not hasattr(self.game_controller, 'game_state') or self.game_controller.game_state is None:
            return
        
        import tkinter as tk
        from tkinter import filedialog
        
        root = tk.Tk()
        root.withdraw()
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar Estado do Jogo",
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            self.game_controller.game_state.save_to_file(file_path)
    
    def _disable_algorithm_buttons(self):
        for alg, rect in self.buttons['algorithms'].items():
            rect.width = 0
            rect.height = 0

    def _enable_algorithm_buttons(self):
        for alg, rect in self.buttons['algorithms'].items():
            rect.width = int(self.screen_width * 0.08)
            rect.height = int(self.screen_height * 0.06)
    
    def _update_animations(self):
        self.animations['title_wave'] = (self.animations['title_wave'] + 0.05) % (2 * math.pi)
        
        self.animations['glow_angle'] = (self.animations['glow_angle'] + 0.01) % (2 * math.pi)
        
        self.animations['button_pulse'] = (self.animations['button_pulse'] + 0.03) % (2 * math.pi)
        
        for particle in self.particles:
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            
            if (particle['x'] < 0 or particle['x'] > self.screen_width or
                particle['y'] < 0 or particle['y'] > self.screen_height):
                particle['x'] = random.randint(0, self.screen_width)
                particle['y'] = random.randint(0, self.screen_height)
                particle['angle'] = random.uniform(0, 2 * math.pi)
    
    def _draw_gradient_background(self):
        gradient = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        time_factor = (1 + math.sin(self.animations['glow_angle'])) / 2
        top_color = self.colors['background_top']
        bottom_color = self.colors['background_bottom']
        
        for y in range(self.screen_height):
            ratio = y / self.screen_height
            r = top_color[0] * (1 - ratio) + bottom_color[0] * ratio
            g = top_color[1] * (1 - ratio) + bottom_color[1] * ratio
            b = top_color[2] * (1 - ratio) + bottom_color[2] * ratio
            
            r = min(255, r + 10 * time_factor)
            g = min(255, g + 5 * time_factor)
            b = min(255, b + 15 * time_factor)
            
            pygame.draw.line(gradient, (r, g, b), (0, y), (self.screen_width, y))
        
        self.screen.blit(gradient, (0, 0))
    
    def _draw_particles(self):
        for particle in self.particles:
            opacity = max(30, 150 - (particle['y'] / self.screen_height) * 100)
            color = (particle['color'][0], particle['color'][1], particle['color'][2], int(opacity))
            
            gfxdraw.filled_circle(
                self.screen, 
                int(particle['x']), 
                int(particle['y']), 
                int(particle['size']), 
                color
            )
    
    def _draw_glow_effects(self):
        header_glow_pos = (self.screen_width // 2, self.layout['header'].height // 2)
        
        glow_opacity = 30 + 20 * math.sin(self.animations['glow_angle'])
        
        glow_surface = self.assets['glow'].copy()
        glow_surface.set_alpha(int(glow_opacity))
        
        glow_rect = glow_surface.get_rect(center=header_glow_pos)
        self.screen.blit(glow_surface, glow_rect)
        
        start_glow_pos = (self.screen_width // 2, self.buttons['start'].centery)
        start_glow_surface = pygame.transform.scale(self.assets['glow'], (200, 200))
        start_glow_surface.set_alpha(int(glow_opacity * 0.7))
        start_glow_rect = start_glow_surface.get_rect(center=start_glow_pos)
        self.screen.blit(start_glow_surface, start_glow_rect)
    
    def _draw_title(self):
        title_text = "Cake Sorting Puzzle"
        
        title_y = self.layout['header'].height // 2 - 20
        
        x_offset = (self.screen_width - len(title_text) * 30) // 2
        
        for i, char in enumerate(title_text):
            wave_offset = math.sin(self.animations['title_wave'] + i * 0.2) * 5
            
            ratio = (math.sin(self.animations['title_wave'] + i * 0.2) + 1) / 2
            color1 = self.colors['title_gradient_1']
            color2 = self.colors['title_gradient_2']
            color = (
                int(color1[0] * (1 - ratio) + color2[0] * ratio),
                int(color1[1] * (1 - ratio) + color2[1] * ratio),
                int(color1[2] * (1 - ratio) + color2[2] * ratio)
            )
            
            shadow_char = self.fonts['title'].render(char, True, self.colors['text_shadow'])
            shadow_pos = (x_offset + i * 30 + 2, title_y + wave_offset + 2)
            self.screen.blit(shadow_char, shadow_pos)
            
            text_char = self.fonts['title'].render(char, True, color)
            text_pos = (x_offset + i * 30, title_y + wave_offset)
            self.screen.blit(text_char, text_pos)
    
    def _update_animations(self):
        self.animations['title_wave'] = (self.animations['title_wave'] + 0.05) % (2 * math.pi)
        
        self.animations['glow_angle'] = (self.animations['glow_angle'] + 0.01) % (2 * math.pi)
        
        self.animations['button_pulse'] = (self.animations['button_pulse'] + 0.03) % (2 * math.pi)
        
        for particle in self.particles:
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            
            if (particle['x'] < 0 or particle['x'] > self.screen_width or
                particle['y'] < 0 or particle['y'] > self.screen_height):
                particle['x'] = random.randint(0, self.screen_width)
                particle['y'] = random.randint(0, self.screen_height)
                particle['angle'] = random.uniform(0, 2 * math.pi)

    def _draw_buttons(self):
        mouse_pos = pygame.mouse.get_pos()
        pulse_factor = (math.sin(self.animations['button_pulse']) + 1) / 2
        
        if self.selected_game_mode == 'ai':
            alg_label = self.fonts['large'].render("Selecione o Algoritmo:", True, self.colors['text'])
            alg_rect = alg_label.get_rect(
                centerx=self.screen_width // 2, 
                bottom=self.layout['algorithm_section'].top + 40
            )
            self.screen.blit(alg_label, alg_rect)
            
            for alg, rect in self.buttons['algorithms'].items():
                is_hover = rect.collidepoint(mouse_pos)
                is_selected = alg == self.selected_algorithm
                
                if is_selected:
                    base_color = self.colors['selected']
                elif is_hover:
                    base_color = self.colors['button_hover']
                else:
                    base_color = self.colors['button']
                
                if is_selected:
                    glow_size = 4 + 2 * pulse_factor
                    glow_rect = rect.inflate(glow_size, glow_size)
                    pygame.draw.rect(self.screen, base_color, glow_rect, border_radius=10)
                
                pygame.draw.rect(self.screen, base_color, rect, border_radius=10)
                
                highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
                highlight_color = (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40))
                pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=10)
                
                text = self.fonts['medium'].render(alg.upper(), True, self.colors['button_text'])
                text_rect = text.get_rect(center=rect.center)
                self.screen.blit(text, text_rect)
        
        mode_label = self.fonts['large'].render("Selecione o Modo de Jogo:", True, self.colors['text'])
        mode_rect = mode_label.get_rect(
            centerx=self.screen_width // 2, 
            bottom=self.layout['game_mode_section'].top + 40
        )
        self.screen.blit(mode_label, mode_rect)
        
        for mode, rect in self.buttons['game_modes'].items():
            is_hover = rect.collidepoint(mouse_pos)
            is_selected = mode == self.selected_game_mode
            
            if is_selected:
                if mode == 'human':
                    base_color = self.colors['human_mode']
                else:
                    base_color = self.colors['ai_mode']
            elif is_hover:
                base_color = self.colors['button_hover']
            else:
                base_color = self.colors['button']
            
            if is_selected:
                glow_size = 4 + 2 * pulse_factor
                glow_rect = rect.inflate(glow_size, glow_size)
                pygame.draw.rect(self.screen, base_color, glow_rect, border_radius=10)
            
            pygame.draw.rect(self.screen, base_color, rect, border_radius=10)
            
            highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
            highlight_color = (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40))
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=10)
            
            mode_text = "Modo Humano" if mode == "human" else "Modo IA"
            text = self.fonts['medium'].render(mode_text, True, self.colors['button_text'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        
        start_rect = self.buttons['start']
        is_hover = start_rect.collidepoint(mouse_pos)
        
        if is_hover:
            base_color = self.colors['button_hover']
            display_rect = start_rect.inflate(4, 4)
        else:
            base_color = self.colors['button']
            pulse_amount = 2 * pulse_factor
            display_rect = start_rect.inflate(pulse_amount, pulse_amount)
        
        pygame.draw.rect(self.screen, base_color, display_rect, border_radius=15)
        
        highlight_rect = pygame.Rect(display_rect.x, display_rect.y, display_rect.width, display_rect.height // 3)
        highlight_color = (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40))
        pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=15)
        
        text = self.fonts['large'].render("INICIAR JOGO", True, self.colors['button_text'])
        text_rect = text.get_rect(center=display_rect.center)
        
        play_icon = self.assets['play_button']
        icon_rect = play_icon.get_rect(midright=(text_rect.left - 10, text_rect.centery))
        self.screen.blit(play_icon, icon_rect)
        
        self.screen.blit(text, text_rect)
        
        exit_rect = self.buttons['exit']
        is_exit_hover = exit_rect.collidepoint(mouse_pos)
        
        if is_exit_hover:
            exit_color = (220, 70, 70)  
            exit_display_rect = exit_rect.inflate(4, 4)
        else:
            exit_color = (180, 50, 50) 
            pulse_amount = 2 * pulse_factor
            exit_display_rect = exit_rect.inflate(pulse_amount, pulse_amount)
        
        pygame.draw.rect(self.screen, exit_color, exit_display_rect, border_radius=15)
        
        exit_highlight_rect = pygame.Rect(exit_display_rect.x, exit_display_rect.y, 
                                        exit_display_rect.width, exit_display_rect.height // 3)
        exit_highlight_color = (min(255, exit_color[0] + 40), min(255, exit_color[1] + 20), min(255, exit_color[2] + 20))
        pygame.draw.rect(self.screen, exit_highlight_color, exit_highlight_rect, border_radius=15)
        
        exit_text = self.fonts['large'].render("SAIR DO JOGO", True, self.colors['button_text'])
        exit_text_rect = exit_text.get_rect(center=exit_display_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
    
    def _draw_board_config(self):
        section_title = self.fonts['large'].render("Configurações", True, self.colors['text'])
        title_rect = section_title.get_rect(centerx=self.screen_width - 110, top=self.layout['board_config_section'].top - 30)
        self.screen.blit(section_title, title_rect)
        
        board_config = self.buttons['board_config']
        
        config_area = pygame.Rect(
            board_config['rows_minus'].left - 10,
            title_rect.top - 10,
            (board_config['rows_plus'].right - board_config['rows_minus'].left) + 20,
            (board_config['plates_plus'].bottom - title_rect.top) + 20
        )
        pygame.draw.rect(self.screen, (40, 15, 60, 150), config_area, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['selected'], config_area, 2, border_radius=10)
        
        minus_text = self.fonts['medium'].render("-", True, self.colors['text'])
        plus_text = self.fonts['medium'].render("+", True, self.colors['text'])
        
        rows_label = self.fonts['medium'].render("Linhas:", True, self.colors['text'])
        rows_rect = rows_label.get_rect(centerx=config_area.centerx, top=board_config['rows_minus'].top - 30)
        self.screen.blit(rows_label, rows_rect)
        
        rows_value = self.fonts['large'].render(str(self.board_rows), True, self.colors['selected'])
        rows_value_rect = rows_value.get_rect(center=board_config['rows_slider'].center)
        self.screen.blit(rows_value, rows_value_rect)
        
        pygame.draw.rect(self.screen, self.colors['button'], board_config['rows_minus'], border_radius=5)
        pygame.draw.rect(self.screen, self.colors['button'], board_config['rows_plus'], border_radius=5)
        self.screen.blit(minus_text, minus_text.get_rect(center=board_config['rows_minus'].center))
        self.screen.blit(plus_text, plus_text.get_rect(center=board_config['rows_plus'].center))
        
        cols_label = self.fonts['medium'].render("Colunas:", True, self.colors['text'])
        cols_rect = cols_label.get_rect(centerx=config_area.centerx, top=board_config['cols_minus'].top - 30)
        self.screen.blit(cols_label, cols_rect)
        
        cols_value = self.fonts['large'].render(str(self.board_cols), True, self.colors['selected'])
        cols_value_rect = cols_value.get_rect(center=board_config['cols_slider'].center)
        self.screen.blit(cols_value, cols_value_rect)
        
        pygame.draw.rect(self.screen, self.colors['button'], board_config['cols_minus'], border_radius=5)
        pygame.draw.rect(self.screen, self.colors['button'], board_config['cols_plus'], border_radius=5)
        self.screen.blit(minus_text, minus_text.get_rect(center=board_config['cols_minus'].center))
        self.screen.blit(plus_text, plus_text.get_rect(center=board_config['cols_plus'].center))
        
        plates_label = self.fonts['medium'].render("Bolos:", True, self.colors['text'])
        plates_rect = plates_label.get_rect(centerx=config_area.centerx, top=board_config['plates_minus'].top - 30)
        self.screen.blit(plates_label, plates_rect)
        
        plates_value = self.fonts['large'].render(str(self.plate_count), True, self.colors['selected'])
        plates_value_rect = plates_value.get_rect(center=board_config['plates_slider'].center)
        self.screen.blit(plates_value, plates_value_rect)
        
        pygame.draw.rect(self.screen, self.colors['button'], board_config['plates_minus'], border_radius=5)
        pygame.draw.rect(self.screen, self.colors['button'], board_config['plates_plus'], border_radius=5)
        self.screen.blit(minus_text, minus_text.get_rect(center=board_config['plates_minus'].center))
        self.screen.blit(plus_text, plus_text.get_rect(center=board_config['plates_plus'].center))
    
    def _draw_instructions(self):
        instructions = [
            "Instruções:",
            "- Selecione um nível e um algoritmo de busca",
            "- Clique em 'INICIAR JOGO' para começar",
            "- No jogo, clique em um prato e depois em uma posição vazia no tabuleiro",
            "- Forme bolos completos (8 fatias do mesmo tipo) para ganhar pontos",
            "- Atinja a pontuação alvo para vencer o nível"
        ]
        
        panel_width = self.screen_width  
        panel_height = int(self.screen_height * 0.15)  
        panel_y = self.screen_height - panel_height 
        
        panel_rect = pygame.Rect(
            0,               
            panel_y,         
            panel_width,     
            panel_height    
        )
        
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((20, 5, 40, 200)) 
        
        gradient_height = 10
        for i in range(gradient_height):
            alpha = int(200 * (i / gradient_height)) 
            pygame.draw.line(panel_surface, (20, 5, 40, alpha), 
                             (0, i), (panel_width, i))
        
        pygame.draw.line(panel_surface, (126, 113, 255, 150), 
                         (0, 0), (panel_width, 0), 2)
        
        self.screen.blit(panel_surface, panel_rect)
        
        cake_icon = self.assets['cake_icon']
        cake_icon = pygame.transform.scale(cake_icon, (50, 50))  
        cake_rect = cake_icon.get_rect(topleft=(panel_rect.left + 30, panel_rect.top + 15))
        self.screen.blit(cake_icon, cake_rect)
        
        col_width = (panel_width - 120) // 2  
        
        col1_x = cake_rect.right + 20
        for i in range(min(3, len(instructions))):
            y = panel_rect.top + 15 + i * 25
            
            if i == 0:
                text = self.fonts['medium'].render(instructions[i], True, self.colors['selected'])
            else:
                text = self.fonts['small'].render(instructions[i], True, self.colors['text'])
            
            rect = text.get_rect(topleft=(col1_x, y))
            self.screen.blit(text, rect)
        
        col2_x = col1_x + col_width
        for i in range(3, len(instructions)):
            y = panel_rect.top + 15 + (i - 3) * 25
            text = self.fonts['small'].render(instructions[i], True, self.colors['text'])
            rect = text.get_rect(topleft=(col2_x, y))
            self.screen.blit(text, rect)
    
    def render(self):
        self._update_animations()
        
        self._draw_gradient_background()
        
        self._draw_glow_effects()
        
        self._draw_particles()
        
        self._draw_title()
        
        self._draw_buttons()
        
        self._draw_board_config()
        
        self._draw_instructions()