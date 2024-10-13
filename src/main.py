import pygame
import os

from constants import *
from game import Game
from menu_manager import Menu_Manager
import menu_globals

def main():
    # Set up window 
    pygame.init()
    pygame.display.set_caption(GAME_TITLE)
    os.environ['SDL_VIDEO_WINDOW_POS'] = '700,100'  # Defines where the windows spawns
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    menu_manager = Menu_Manager()
    
    while True:
        if menu_globals.is_first_loop:
            game = Game(menu_manager, window)
            menu_globals.is_first_loop = False
        if not menu_globals.game_running:
            game.menu_manager.main_menu.update(pygame.event.get())
            game.menu_manager.resize_menus(*game.window.get_size())
            game.menu_manager.main_menu.draw(game.window)
        else:
            game.run()

        pygame.display.update()
        pygame.time.Clock().tick(FPS)

if __name__ == '__main__':
    main()