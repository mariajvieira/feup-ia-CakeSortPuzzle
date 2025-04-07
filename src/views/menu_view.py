#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Classe MenuView - Responsável por renderizar o menu principal do jogo.
"""

import pygame
import math
import random
from pygame import gfxdraw


class MenuView:
    """Classe que representa a visualização do menu principal com design moderno.
    
    Attributes:
        screen (pygame.Surface): Superfície de renderização do jogo.
        game_controller (GameController): Controlador do jogo.
        colors (dict): Dicionário de cores utilizadas no menu.
        fonts (dict): Dicionário de fontes utilizadas no menu.
        buttons (dict): Dicionário de botões do menu.
        selected_level (int): Nível selecionado.
        selected_algorithm (str): Algoritmo de busca selecionado.
        particles (list): Lista de partículas para efeitos visuais.
        animations (dict): Dicionário de animações do menu.
        assets (dict): Dicionário de recursos gráficos.
    """
    
    def __init__(self, screen, game_controller):
        """Inicializa a visualização do menu.
        
        Args:
            screen (pygame.Surface): Superfície de renderização do jogo.
            game_controller (GameController): Controlador do jogo.
        """
        self.screen = screen
        self.game_controller = game_controller
        self.screen_width, self.screen_height = self.screen.get_size()
        
        # Define as cores utilizadas no menu - Paleta moderna com tons de roxo e rosa
        self.colors = {
            'background_top': (25, 10, 44),  # Roxo escuro
            'background_bottom': (80, 10, 80),  # Roxo médio
            'text': (255, 255, 255),  # Branco
            'text_shadow': (100, 50, 150, 128),  # Sombra roxa
            'button': (140, 50, 200),  # Roxo vibrante
            'button_hover': (200, 70, 220),  # Rosa vibrante
            'button_text': (255, 255, 255),  # Branco
            'selected': (255, 113, 206),  # Rosa neon
            'title_gradient_1': (255, 113, 206),  # Rosa neon
            'title_gradient_2': (126, 113, 255),  # Azul/roxo neon
            'particle': (255, 255, 255, 150),  # Branco translúcido
            'glow': (200, 100, 255, 30),  # Brilho roxo
            'human_mode': (50, 205, 50),  # Verde para o modo humano
            'ai_mode': (0, 191, 255)  # Azul para o modo IA
        }
        
        # Inicializa as fontes - Usando fontes mais modernas
        pygame.font.init()
        available_fonts = pygame.font.get_fonts()
        
        # Tenta encontrar fontes modernas, ou usa as padrão
        title_font = 'arialrounded' if 'arialrounded' in available_fonts else 'arial'
        main_font = 'arialrounded' if 'arialrounded' in available_fonts else 'arial'
        
        self.fonts = {
            'small': pygame.font.SysFont(main_font, 16),
            'medium': pygame.font.SysFont(main_font, 24),
            'large': pygame.font.SysFont(main_font, 28, bold=True),
            'title': pygame.font.SysFont(title_font, 60, bold=True)
        }
        
        # Inicializa as seleções
        self.selected_level = 1
        self.selected_algorithm = 'bfs'
        self.selected_game_mode = 'ai'  # Modo padrão: IA
        
        # Inicializa os botões com design moderno
        self._init_buttons()
        
        # Inicializa as partículas para efeito visual
        self.particles = []
        self._init_particles(50)  # Cria 50 partículas
        
        # Inicializa as animações
        self.animations = {
            'title_wave': 0,
            'glow_angle': 0,
            'button_pulse': 0
        }
        
        # Carrega os recursos gráficos
        self.assets = self._load_assets()
    
    def _load_assets(self):
        """Carrega os recursos gráficos necessários."""
        assets = {}
        try:
            import os
            # Carrega os SVGs como superfícies pygame
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            particle_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'particle.svg'))
            glow_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'glow.svg'))
            play_button_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'play_button.svg'))
            cake_icon_svg = pygame.image.load(os.path.join(base_path, 'assets', 'images', 'cake_icon.svg'))
            
            # Redimensiona conforme necessário
            assets['particle'] = pygame.transform.scale(particle_svg, (20, 20))
            assets['glow'] = pygame.transform.scale(glow_svg, (400, 400))
            assets['play_button'] = pygame.transform.scale(play_button_svg, (50, 50))
            assets['cake_icon'] = pygame.transform.scale(cake_icon_svg, (60, 60))
        except Exception as e:
            print(f"Erro ao carregar assets: {e}")
            # Cria superfícies vazias como fallback
            assets['particle'] = pygame.Surface((20, 20), pygame.SRCALPHA)
            assets['glow'] = pygame.Surface((400, 400), pygame.SRCALPHA)
            assets['play_button'] = pygame.Surface((50, 50), pygame.SRCALPHA)
            assets['cake_icon'] = pygame.Surface((60, 60), pygame.SRCALPHA)
        
        return assets
    
    def _init_particles(self, count):
        """Inicializa partículas para efeitos visuais.
        
        Args:
            count (int): Número de partículas a serem criadas.
        """
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
        """Inicializa os botões do menu com design moderno."""
        # Proporções baseadas no tamanho da tela para responsividade
        button_width = int(self.screen_width * 0.18)
        button_height = int(self.screen_height * 0.06)
        button_spacing = int(self.screen_height * 0.08)
        
        # Divisão clara da tela em seções
        header_height = int(self.screen_height * 0.2)  # Seção superior para título
        footer_height = int(self.screen_height * 0.25)  # Seção inferior para instruções
        content_height = self.screen_height - header_height - footer_height  # Área central para interação
        
        # Posição inicial dos elementos na área de conteúdo
        center_x = self.screen_width // 2
        content_start_y = header_height + int(content_height * 0.1)  # 10% de margem superior
        
        # Botões de nível com bom espaçamento
        level_buttons = {}
        level_width = int(self.screen_width * 0.06)
        level_spacing = int(self.screen_width * 0.08)
        level_start_x = center_x - ((5 * level_width + 4 * (level_spacing - level_width)) // 2)
        level_y = content_start_y + int(content_height * 0.15)
        
        for i in range(1, 6):  # Níveis 1 a 5
            x = level_start_x + (i - 1) * level_spacing
            level_buttons[i] = pygame.Rect(x, level_y, level_width, button_height)
        
        # Botões de algoritmo com bom espaçamento
        algorithm_buttons = {}
        algorithms = ['bfs', 'dfs', 'ids', 'ucs', 'greedy', 'astar', 'wastar']  # Adicionado 'wastar'
        alg_width = int(self.screen_width * 0.06)  # Reduzido para acomodar mais botões
        alg_spacing = int(self.screen_width * 0.08)  # Ajustado espaçamento
        alg_start_x = center_x - ((7 * alg_width + 6 * (alg_spacing - alg_width)) // 2)  # Ajustado para 7 algoritmos
        alg_y = level_y + button_height + button_spacing  # Posicionado abaixo dos níveis
        
        for i, alg in enumerate(algorithms):
            x = alg_start_x + i * alg_spacing
            algorithm_buttons[alg] = pygame.Rect(x, alg_y, alg_width, button_height)
            
        # Botões de modo de jogo
        game_mode_buttons = {}
        modes = ['ai', 'human']
        mode_width = int(self.screen_width * 0.12)
        mode_spacing = int(self.screen_width * 0.15)
        mode_start_x = center_x - mode_spacing // 2
        mode_y = alg_y + button_height + button_spacing  # Posicionado abaixo dos algoritmos
        
        for i, mode in enumerate(modes):
            x = mode_start_x + i * mode_spacing - mode_width // 2
            game_mode_buttons[mode] = pygame.Rect(x, mode_y, mode_width, button_height)
        
        # Botões de ação na parte inferior da área de conteúdo
        action_y = mode_y + button_height + button_spacing + 20
        
        # Botão de iniciar jogo - Destacado
        start_button = pygame.Rect(
            center_x - button_width // 2,
            action_y,
            button_width, 
            button_height + 10  # Um pouco mais alto para destaque
        )
        
        # Botão para sair do jogo
        exit_button = pygame.Rect(
            center_x - button_width // 2,
            action_y + button_height + 30,
            button_width, 
            button_height
        )
        
        self.buttons = {
            'levels': level_buttons,
            'algorithms': algorithm_buttons,
            'game_modes': game_mode_buttons,
            'start': start_button,
            'exit': exit_button
        }
        
        # Armazena as regiões para uso em outros métodos
        self.layout = {
            'header': pygame.Rect(0, 0, self.screen_width, header_height),
            'content': pygame.Rect(0, header_height, self.screen_width, content_height),
            'footer': pygame.Rect(0, self.screen_height - footer_height, self.screen_width, footer_height),
            'level_section': pygame.Rect(0, level_y - 60, self.screen_width, button_height + 80),
            'algorithm_section': pygame.Rect(0, alg_y - 60, self.screen_width, button_height + 80),
            'game_mode_section': pygame.Rect(0, mode_y - 60, self.screen_width, button_height + 80),
            'action_section': pygame.Rect(0, action_y - 20, self.screen_width, 2*button_height + 60)
        }

    def handle_event(self, event):
        """Trata os eventos do menu.
        
        Args:
            event (pygame.event.Event): Evento a ser tratado.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Botão esquerdo do mouse
                self._handle_mouse_click(event.pos)
    
    def _handle_mouse_click(self, pos):
        """Trata os cliques do mouse.
        
        Args:
            pos (tuple): Posição (x, y) do clique.
        """
        # Verifica se clicou em um botão de nível
        for level, rect in self.buttons['levels'].items():
            if rect.collidepoint(pos):
                self.selected_level = level
                return
        
        # Verifica se clicou em um botão de algoritmo
        for alg, rect in self.buttons['algorithms'].items():
            if rect.collidepoint(pos) and self.selected_game_mode == 'ai':
                self.selected_algorithm = alg
                return
                
        # Verifica se clicou em um botão de modo de jogo
        for mode, rect in self.buttons['game_modes'].items():
            if rect.collidepoint(pos):
                self.selected_game_mode = mode
                # Desativa os botões de algoritmo no modo humano
                if mode == 'human':
                    self._disable_algorithm_buttons()
                else:
                    self._enable_algorithm_buttons()
                return
        
        # Verifica se clicou no botão de iniciar jogo
        if self.buttons['start'].collidepoint(pos):
            self.game_controller.start_game(self.selected_level, self.selected_algorithm, self.selected_game_mode)
            return
        
        # Verifica se clicou no botão de sair
        if self.buttons['exit'].collidepoint(pos):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            return
    
    def _disable_algorithm_buttons(self):
        """Desativa os botões de algoritmo."""
        for alg, rect in self.buttons['algorithms'].items():
            rect.width = 0
            rect.height = 0

    def _enable_algorithm_buttons(self):
        """Ativa os botões de algoritmo."""
        for alg, rect in self.buttons['algorithms'].items():
            rect.width = int(self.screen_width * 0.08)
            rect.height = int(self.screen_height * 0.06)
    
    def _update_animations(self):
        """Atualiza as animações do menu."""
        # Atualiza a animação de onda do título
        self.animations['title_wave'] = (self.animations['title_wave'] + 0.05) % (2 * math.pi)
        
        # Atualiza o ângulo do brilho
        self.animations['glow_angle'] = (self.animations['glow_angle'] + 0.01) % (2 * math.pi)
        
        # Atualiza a pulsação dos botões
        self.animations['button_pulse'] = (self.animations['button_pulse'] + 0.03) % (2 * math.pi)
        
        # Atualiza as partículas
        for particle in self.particles:
            # Move a partícula
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            
            # Se a partícula sair da tela, reposiciona
            if (particle['x'] < 0 or particle['x'] > self.screen_width or
                particle['y'] < 0 or particle['y'] > self.screen_height):
                particle['x'] = random.randint(0, self.screen_width)
                particle['y'] = random.randint(0, self.screen_height)
                particle['angle'] = random.uniform(0, 2 * math.pi)
    
    def _draw_gradient_background(self):
        """Desenha um fundo com gradiente dinâmico."""
        # Cria uma superfície para o gradiente
        gradient = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Cores do gradiente com variação temporal
        time_factor = (1 + math.sin(self.animations['glow_angle'])) / 2
        top_color = self.colors['background_top']
        bottom_color = self.colors['background_bottom']
        
        # Desenha o gradiente
        for y in range(self.screen_height):
            # Calcula a cor interpolada
            ratio = y / self.screen_height
            r = top_color[0] * (1 - ratio) + bottom_color[0] * ratio
            g = top_color[1] * (1 - ratio) + bottom_color[1] * ratio
            b = top_color[2] * (1 - ratio) + bottom_color[2] * ratio
            
            # Adiciona um pouco de variação temporal
            r = min(255, r + 10 * time_factor)
            g = min(255, g + 5 * time_factor)
            b = min(255, b + 15 * time_factor)
            
            # Desenha uma linha horizontal com a cor interpolada
            pygame.draw.line(gradient, (r, g, b), (0, y), (self.screen_width, y))
        
        # Aplica o gradiente na tela
        self.screen.blit(gradient, (0, 0))
    
    def _draw_particles(self):
        """Desenha as partículas para efeito visual."""
        for particle in self.particles:
            # Calcula a opacidade com base na posição Y (mais brilhante no topo)
            opacity = max(30, 150 - (particle['y'] / self.screen_height) * 100)
            color = (particle['color'][0], particle['color'][1], particle['color'][2], int(opacity))
            
            # Desenha a partícula como um círculo suave
            gfxdraw.filled_circle(
                self.screen, 
                int(particle['x']), 
                int(particle['y']), 
                int(particle['size']), 
                color
            )
    
    def _draw_glow_effects(self):
        """Desenha efeitos de brilho nas áreas apropriadas."""
        # Brilho no cabeçalho para o título
        header_glow_pos = (self.screen_width // 2, self.layout['header'].height // 2)
        
        # Calcula a opacidade do brilho com base na animação
        glow_opacity = 30 + 20 * math.sin(self.animations['glow_angle'])
        
        # Cria uma cópia do asset de brilho com a opacidade correta
        glow_surface = self.assets['glow'].copy()
        glow_surface.set_alpha(int(glow_opacity))
        
        # Posiciona o brilho centralizado no cabeçalho
        glow_rect = glow_surface.get_rect(center=header_glow_pos)
        self.screen.blit(glow_surface, glow_rect)
        
        # Adiciona um segundo brilho menor no botão de iniciar
        start_glow_pos = (self.screen_width // 2, self.buttons['start'].centery)
        start_glow_surface = pygame.transform.scale(self.assets['glow'], (200, 200))
        start_glow_surface.set_alpha(int(glow_opacity * 0.7))
        start_glow_rect = start_glow_surface.get_rect(center=start_glow_pos)
        self.screen.blit(start_glow_surface, start_glow_rect)
    
    def _draw_title(self):
        """Desenha o título com efeito de onda na seção de cabeçalho."""
        title_text = "Cake Sorting Puzzle"
        
        # Centraliza o título na área de cabeçalho
        title_y = self.layout['header'].height // 2 - 20
        
        # Renderiza cada letra individualmente para criar o efeito de onda
        x_offset = (self.screen_width - len(title_text) * 30) // 2  # Centraliza o título
        
        for i, char in enumerate(title_text):
            # Calcula o deslocamento vertical baseado na animação de onda
            wave_offset = math.sin(self.animations['title_wave'] + i * 0.2) * 5
            
            # Calcula a cor da letra (gradiente entre duas cores)
            ratio = (math.sin(self.animations['title_wave'] + i * 0.2) + 1) / 2
            color1 = self.colors['title_gradient_1']
            color2 = self.colors['title_gradient_2']
            color = (
                int(color1[0] * (1 - ratio) + color2[0] * ratio),
                int(color1[1] * (1 - ratio) + color2[1] * ratio),
                int(color1[2] * (1 - ratio) + color2[2] * ratio)
            )
            
            # Renderiza a sombra do texto
            shadow_char = self.fonts['title'].render(char, True, self.colors['text_shadow'])
            shadow_pos = (x_offset + i * 30 + 2, title_y + wave_offset + 2)
            self.screen.blit(shadow_char, shadow_pos)
            
            # Renderiza o texto
            text_char = self.fonts['title'].render(char, True, color)
            text_pos = (x_offset + i * 30, title_y + wave_offset)
            self.screen.blit(text_char, text_pos)
    
    def _update_animations(self):
        """Atualiza as animações do menu."""
        # Atualiza a animação de onda do título
        self.animations['title_wave'] = (self.animations['title_wave'] + 0.05) % (2 * math.pi)
        
        # Atualiza o ângulo do brilho
        self.animations['glow_angle'] = (self.animations['glow_angle'] + 0.01) % (2 * math.pi)
        
        # Atualiza a pulsação dos botões
        self.animations['button_pulse'] = (self.animations['button_pulse'] + 0.03) % (2 * math.pi)
        
        # Atualiza as partículas
        for particle in self.particles:
            # Move a partícula
            particle['x'] += math.cos(particle['angle']) * particle['speed']
            particle['y'] += math.sin(particle['angle']) * particle['speed']
            
            # Se a partícula sair da tela, reposiciona
            if (particle['x'] < 0 or particle['x'] > self.screen_width or
                particle['y'] < 0 or particle['y'] > self.screen_height):
                particle['x'] = random.randint(0, self.screen_width)
                particle['y'] = random.randint(0, self.screen_height)
                particle['angle'] = random.uniform(0, 2 * math.pi)

    def _draw_buttons(self):
        """Desenha os botões do menu com efeitos modernos."""
        mouse_pos = pygame.mouse.get_pos()
        pulse_factor = (math.sin(self.animations['button_pulse']) + 1) / 2  # Valor entre 0 e 1
        
        # Desenha o rótulo da seção de níveis
        level_label = self.fonts['large'].render("Selecione o Nível:", True, self.colors['text'])
        level_rect = level_label.get_rect(
            centerx=self.screen_width // 2, 
            bottom=self.layout['level_section'].top + 40
        )
        self.screen.blit(level_label, level_rect)
        
        # Desenha os botões de nível
        for level, rect in self.buttons['levels'].items():
            # Verifica se o mouse está sobre o botão ou se está selecionado
            is_hover = rect.collidepoint(mouse_pos)
            is_selected = level == self.selected_level
            
            # Define a cor do botão
            if is_selected:
                base_color = self.colors['selected']
            elif is_hover:
                base_color = self.colors['button_hover']
            else:
                base_color = self.colors['button']
            
            # Adiciona efeito de pulsação para botões selecionados
            if is_selected:
                # Cria um efeito de brilho pulsante ao redor do botão
                glow_size = 4 + 2 * pulse_factor
                glow_rect = rect.inflate(glow_size, glow_size)
                pygame.draw.rect(self.screen, base_color, glow_rect, border_radius=10)
            
            # Desenha o botão com cantos arredondados
            pygame.draw.rect(self.screen, base_color, rect, border_radius=10)
            
            # Adiciona um brilho na parte superior do botão para efeito 3D
            highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
            highlight_color = (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40))
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=10)
            
            # Renderiza o texto do botão
            text = self.fonts['medium'].render(str(level), True, self.colors['button_text'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Desenha o rótulo da seção de algoritmos
        alg_label = self.fonts['large'].render("Selecione o Algoritmo:", True, self.colors['text'])
        alg_rect = alg_label.get_rect(
            centerx=self.screen_width // 2, 
            bottom=self.layout['algorithm_section'].top + 40
        )
        self.screen.blit(alg_label, alg_rect)
        
        # Desenha os botões de algoritmo
        for alg, rect in self.buttons['algorithms'].items():
            # Verifica se o mouse está sobre o botão ou se está selecionado
            is_hover = rect.collidepoint(mouse_pos)
            is_selected = alg == self.selected_algorithm
            
            # Define a cor do botão
            if is_selected:
                base_color = self.colors['selected']
            elif is_hover:
                base_color = self.colors['button_hover']
            else:
                base_color = self.colors['button']
            
            # Adiciona efeito de pulsação para botões selecionados
            if is_selected:
                # Cria um efeito de brilho pulsante ao redor do botão
                glow_size = 4 + 2 * pulse_factor
                glow_rect = rect.inflate(glow_size, glow_size)
                pygame.draw.rect(self.screen, base_color, glow_rect, border_radius=10)
            
            # Desenha o botão com cantos arredondados
            pygame.draw.rect(self.screen, base_color, rect, border_radius=10)
            
            # Adiciona um brilho na parte superior do botão para efeito 3D
            highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
            highlight_color = (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40))
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=10)
            
            # Renderiza o texto do botão
            text = self.fonts['medium'].render(alg.upper(), True, self.colors['button_text'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Desenha o rótulo da seção de modos de jogo
        mode_label = self.fonts['large'].render("Selecione o Modo de Jogo:", True, self.colors['text'])
        mode_rect = mode_label.get_rect(
            centerx=self.screen_width // 2, 
            bottom=self.layout['game_mode_section'].top + 40
        )
        self.screen.blit(mode_label, mode_rect)
        
        # Desenha os botões de modo de jogo
        for mode, rect in self.buttons['game_modes'].items():
            # Verifica se o mouse está sobre o botão ou se está selecionado
            is_hover = rect.collidepoint(mouse_pos)
            is_selected = mode == self.selected_game_mode
            
            # Define a cor do botão baseada no modo
            if is_selected:
                if mode == 'human':
                    base_color = self.colors['human_mode']
                else:  # mode == 'ai'
                    base_color = self.colors['ai_mode']
            elif is_hover:
                base_color = self.colors['button_hover']
            else:
                base_color = self.colors['button']
            
            # Adiciona efeito de pulsação para botões selecionados
            if is_selected:
                # Cria um efeito de brilho pulsante ao redor do botão
                glow_size = 4 + 2 * pulse_factor
                glow_rect = rect.inflate(glow_size, glow_size)
                pygame.draw.rect(self.screen, base_color, glow_rect, border_radius=10)
            
            # Desenha o botão com cantos arredondados
            pygame.draw.rect(self.screen, base_color, rect, border_radius=10)
            
            # Adiciona um brilho na parte superior do botão para efeito 3D
            highlight_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height // 3)
            highlight_color = (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40))
            pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=10)
            
            # Renderiza o texto do botão
            mode_text = "Modo Humano" if mode == "human" else "Modo IA"
            text = self.fonts['medium'].render(mode_text, True, self.colors['button_text'])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        
        # Desenha o botão de iniciar jogo com efeitos especiais
        start_rect = self.buttons['start']
        is_hover = start_rect.collidepoint(mouse_pos)
        
        # Define a cor do botão com efeito de pulsação
        if is_hover:
            base_color = self.colors['button_hover']
            # Aumenta o tamanho do botão quando hover
            display_rect = start_rect.inflate(4, 4)
        else:
            base_color = self.colors['button']
            # Pulsa sutilmente mesmo sem hover
            pulse_amount = 2 * pulse_factor
            display_rect = start_rect.inflate(pulse_amount, pulse_amount)
        
        # Desenha o botão com cantos arredondados
        pygame.draw.rect(self.screen, base_color, display_rect, border_radius=15)
        
        # Adiciona um brilho na parte superior do botão para efeito 3D
        highlight_rect = pygame.Rect(display_rect.x, display_rect.y, display_rect.width, display_rect.height // 3)
        highlight_color = (min(255, base_color[0] + 40), min(255, base_color[1] + 40), min(255, base_color[2] + 40))
        pygame.draw.rect(self.screen, highlight_color, highlight_rect, border_radius=15)
        
        # Renderiza o texto do botão
        text = self.fonts['large'].render("INICIAR JOGO", True, self.colors['button_text'])
        text_rect = text.get_rect(center=display_rect.center)
        
        # Adiciona o ícone de play ao lado do texto
        play_icon = self.assets['play_button']
        icon_rect = play_icon.get_rect(midright=(text_rect.left - 10, text_rect.centery))
        self.screen.blit(play_icon, icon_rect)
        
        # Renderiza o texto
        self.screen.blit(text, text_rect)
        
        # Desenha o botão de sair do jogo
        exit_rect = self.buttons['exit']
        is_exit_hover = exit_rect.collidepoint(mouse_pos)
        
        # Define a cor do botão com efeito de pulsação
        if is_exit_hover:
            exit_color = (220, 70, 70)  # Vermelho mais intenso para hover
            # Aumenta o tamanho do botão quando hover
            exit_display_rect = exit_rect.inflate(4, 4)
        else:
            exit_color = (180, 50, 50)  # Vermelho base para o botão de sair
            # Pulsa sutilmente mesmo sem hover
            pulse_amount = 2 * pulse_factor
            exit_display_rect = exit_rect.inflate(pulse_amount, pulse_amount)
        
        # Desenha o botão com cantos arredondados
        pygame.draw.rect(self.screen, exit_color, exit_display_rect, border_radius=15)
        
        # Adiciona um brilho na parte superior do botão para efeito 3D
        exit_highlight_rect = pygame.Rect(exit_display_rect.x, exit_display_rect.y, 
                                        exit_display_rect.width, exit_display_rect.height // 3)
        exit_highlight_color = (min(255, exit_color[0] + 40), min(255, exit_color[1] + 20), min(255, exit_color[2] + 20))
        pygame.draw.rect(self.screen, exit_highlight_color, exit_highlight_rect, border_radius=15)
        
        # Renderiza o texto do botão de sair
        exit_text = self.fonts['large'].render("SAIR DO JOGO", True, self.colors['button_text'])
        exit_text_rect = exit_text.get_rect(center=exit_display_rect.center)
        self.screen.blit(exit_text, exit_text_rect)
    
    def _draw_instructions(self):
        """Desenha as instruções do jogo com estilo moderno."""
        instructions = [
            "Instruções:",
            "- Selecione um nível e um algoritmo de busca",
            "- Clique em 'INICIAR JOGO' para começar",
            "- No jogo, clique em um prato e depois em uma posição vazia no tabuleiro",
            "- Forme bolos completos (8 fatias do mesmo tipo) para ganhar pontos",
            "- Atinja a pontuação alvo para vencer o nível"
        ]
        
        # Posiciona o painel na parte mais inferior da tela, ocupando toda a largura
        panel_width = self.screen_width  # Ocupa toda a largura da tela
        panel_height = int(self.screen_height * 0.15)  # 15% da altura da tela para o painel
        panel_y = self.screen_height - panel_height  # Posicionado no fundo da tela
        
        panel_rect = pygame.Rect(
            0,               # Começa na extremidade esquerda
            panel_y,         # Na parte inferior da tela
            panel_width,     # Ocupa toda a largura
            panel_height     # Altura fixa para instruções
        )
        
        # Cria uma superfície semi-transparente para o fundo do painel
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill((20, 5, 40, 200))  # Cor de fundo semi-transparente mais escura
        
        # Adiciona um gradiente sutil na parte superior para integrar melhor com o resto da tela
        gradient_height = 10
        for i in range(gradient_height):
            alpha = int(200 * (i / gradient_height))  # Gradiente de transparência
            pygame.draw.line(panel_surface, (20, 5, 40, alpha), 
                             (0, i), (panel_width, i))
        
        # Adiciona uma linha brilhante na borda superior do painel
        pygame.draw.line(panel_surface, (126, 113, 255, 150), 
                         (0, 0), (panel_width, 0), 2)
        
        # Desenha o painel
        self.screen.blit(panel_surface, panel_rect)
        
        # Desenha o ícone do bolo
        cake_icon = self.assets['cake_icon']
        cake_icon = pygame.transform.scale(cake_icon, (50, 50))  # Um pouco menor
        cake_rect = cake_icon.get_rect(topleft=(panel_rect.left + 30, panel_rect.top + 15))
        self.screen.blit(cake_icon, cake_rect)
        
        # Renderiza as instruções em duas colunas para melhor aproveitamento do espaço
        col_width = (panel_width - 120) // 2  # Largura de cada coluna (menos margens)
        
        # Primeira metade das instruções (coluna esquerda)
        col1_x = cake_rect.right + 20
        for i in range(min(3, len(instructions))):
            y = panel_rect.top + 15 + i * 25
            
            # O título tem estilo diferente
            if i == 0:
                text = self.fonts['medium'].render(instructions[i], True, self.colors['selected'])
            else:
                text = self.fonts['small'].render(instructions[i], True, self.colors['text'])
            
            rect = text.get_rect(topleft=(col1_x, y))
            self.screen.blit(text, rect)
        
        # Segunda metade das instruções (coluna direita)
        col2_x = col1_x + col_width
        for i in range(3, len(instructions)):
            y = panel_rect.top + 15 + (i - 3) * 25
            text = self.fonts['small'].render(instructions[i], True, self.colors['text'])
            rect = text.get_rect(topleft=(col2_x, y))
            self.screen.blit(text, rect)
    
    def render(self):
        """Renderiza o menu na tela com efeitos visuais modernos."""
        # Atualiza as animações
        self._update_animations()
        
        # Desenha o fundo com gradiente
        self._draw_gradient_background()
        
        # Desenha os efeitos de brilho
        self._draw_glow_effects()
        
        # Desenha as partículas
        self._draw_particles()
        
        # Desenha o título
        self._draw_title()
        
        # Desenha os botões
        self._draw_buttons()
        
        # Desenha as instruções
        self._draw_instructions()