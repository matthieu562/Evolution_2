import pygame

from constants import *
from game import Game
import menu_globals

def main():
    while True:
        if menu_globals.is_first_loop:
            game = Game()
            menu_globals.is_first_loop = False
        if not menu_globals.game_running:
            game.menu_manager.main_menu.update(pygame.event.get())
            game.menu_manager.main_menu.draw(game.window)
        else:
            game.run()

        pygame.display.update()
        pygame.time.Clock().tick(FPS)

if __name__ == '__main__':
    main()