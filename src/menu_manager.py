import pygame
import pygame_menu

from constants import *
import menu_globals as menu_globals


class Menu_Manager:
    def __init__(self):
        self.window_width, self.window_height = WINDOW_WIDTH, WINDOW_HEIGHT
        self.main_menu = self.create_main_menu()
        self.pause_menu = self.create_pause_menu()

    def create_main_menu(self):
        main_menu = pygame_menu.Menu('Evolution 2 !', self.window_width, self.window_height, theme=pygame_menu.themes.THEME_DARK)
        main_menu.add.button('Play', self.start_game)
        main_menu.add.button('Quit', pygame_menu.events.EXIT)
        return main_menu

    def create_pause_menu(self):
        pause_menu = pygame_menu.Menu('Pause', self.window_width, self.window_height, theme=pygame_menu.themes.THEME_DARK)
        pause_menu.add.button('Resume', self.resume_game)
        pause_menu.add.button('Back to menu', self.go_to_main_menu)
        pause_menu.add.button('Quit', self.quit_game)
        return pause_menu

    def resize_menus(self, window_width, window_height):
        self.window_width, self.window_height = window_width, window_height
        self.main_menu = self.create_main_menu()
        self.pause_menu = self.create_pause_menu()

    def quit_game(self):
        pygame.quit()
        exit()
    
    def start_game(self):
        menu_globals.is_first_loop = True
        menu_globals.game_running = True
        menu_globals.game_paused = False

    def resume_game(self):
        menu_globals.game_paused = False

    def go_to_main_menu(self):
        menu_globals.game_running = False
        menu_globals.game_paused = False
