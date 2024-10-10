import os
import pygame

from menu_manager import Menu_Manager
from constants import *
import menu_globals

class Game:
    
    def __init__(self) -> None:
        pygame.init()
        
        ## Set up window ##
        pygame.display.set_caption('Evolution 2 !')
        os.environ['SDL_VIDEO_WINDOW_POS'] = '700,100' # Defines where the windows spawns

        ## Init attributes
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.menu_manager = Menu_Manager()
                
        ## Attributes created later
        self.events = None
        
    def handle_user_inputs(self):
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_globals.game_paused = not menu_globals.game_paused
    
    def run(self):
        while menu_globals.game_running:
            self.window.fill(pygame.Color('black'))

            self.events = pygame.event.get()
            self.handle_user_inputs()

            if menu_globals.game_paused:
                self.menu_manager.pause_menu.update(self.events)
                self.menu_manager.pause_menu.draw(self.window)
            else:
                # The actual game starts here
                self.window.fill(pygame.Color('pink'))
            
            pygame.display.flip()
            pygame.time.Clock().tick(GAME_FREQ)

