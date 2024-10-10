import pygame

from constants import *
from game import Game
import menu_globals

def main():
    game = Game()
    
    while True:
        if not menu_globals.game_running:
            game.menu_manager.main_menu.update(pygame.event.get())
            game.menu_manager.main_menu.draw(game.window)
        else:
            game.run()

        pygame.display.update()
        pygame.time.Clock().tick(GAME_FREQ)


if __name__ == '__main__':
    main()