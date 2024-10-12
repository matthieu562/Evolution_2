import math
import os
import pygame
import pymunk
import numpy as np

from camera import Camera  # Importation de la classe Camera
from cell import Cell
from collision_handler import Collision_Handler
from constants import *
from food import Food
from images import Images
from menu_manager import Menu_Manager
from population import Population
import menu_globals

NB_CELLS = 10
NB_FOODS = 50

class Game:
    
    def __init__(self) -> None:
        pygame.init()
        
        ## Set up window ##
        pygame.display.set_caption(GAME_TITLE)
        os.environ['SDL_VIDEO_WINDOW_POS'] = '700,100'  # Defines where the windows spawns

        # Handle the Space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # Pas de gravité
        self.space.damping = 0.5  # Frottement global
        self.add_static_walls()
        
        # Handle collision
        self.collision_handler = Collision_Handler(self)
        self.space.add_collision_handler(CELL_COLLISION_TYPE, FOOD_COLLISION_TYPE).begin = self.collision_handler.handle_collision_cell_vs_food
        self.space.add_collision_handler(CELL_COLLISION_TYPE, CELL_COLLISION_TYPE).begin = self.collision_handler.handle_collision_cell_vs_cell

        ## Init attributes
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.menu_manager = Menu_Manager()
        self.clock = pygame.time.Clock()
        self.population = Population(self.space)
        self.images = Images()
        self.camera = Camera(self.window)

        # Populate space
        cell = Cell.create_new_cells(self.space, 1, self.images.user_cell_images)
        self.population.add_cells(cell)
        cells = Cell.create_new_cells(self.space, NB_CELLS, self.images.cell_images)
        self.population.add_cells(cells)
        foods = Food.create_new_foods(self.space, NB_CELLS, self.images.food_image)
        self.population.add_foods(foods)
        
        ## Attributes created later
        self.events = None
        # self.walls = None
        
  
    def handle_user_inputs(self):
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_globals.game_paused = not menu_globals.game_paused
                if event.key == pygame.K_r:
                    self.camera.zoom_factor = 1  # Zoom par défaut
                    self.camera.offset_x, self.camera.offset_y = 0, 0  # Offset de déplacement

            # Gestion du zoom
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Zoom avant
                    zoom_amount = 0.1
                    # self.camera.zoom_factor *= 1.1
                elif event.y < 0:  # Zoom arrière
                    # self.camera.zoom_factor /= 1.1
                    zoom_amount = -0.1
                    
                self.camera.zoom(zoom_amount)

            # Gestion du clic droit pour la translation (pan)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Clic droit
                self.camera.dragging = True
                self.camera.last_mouse_pos = pygame.mouse.get_pos()

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:  # Relâchement clic droit
                self.camera.dragging = False

        if self.camera.dragging:
            # Si on maintient le clic droit, on calcule la translation
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self.camera.last_mouse_pos:
                dx = mouse_x - self.camera.last_mouse_pos[0]
                dy = mouse_y - self.camera.last_mouse_pos[1]
                self.camera.offset_x += dx
                self.camera.offset_y += dy
                self.camera.last_mouse_pos = (mouse_x, mouse_y)

    def add_static_walls(self):
        """Ajoute des lignes statiques aux bords de la fenêtre."""
        radius = 5
        self.walls = [
            pymunk.Segment(self.space.static_body, (0, 0), (0, WINDOW_HEIGHT), radius),  # Bord gauche
            pymunk.Segment(self.space.static_body, (0, WINDOW_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT), radius),  # Bord bas
            pymunk.Segment(self.space.static_body, (WINDOW_WIDTH, WINDOW_HEIGHT), (WINDOW_WIDTH, 0), radius),  # Bord droit
            pymunk.Segment(self.space.static_body, (WINDOW_WIDTH, 0), (0, 0), radius)  # Bord haut
        ]
        for wall in self.walls:
            wall.elasticity = 0.9
            wall.friction = 0.5
        self.space.add(*self.walls)

    def run(self):
        is_prey_controlled = False
        
        while menu_globals.game_running:
            self.events = pygame.event.get()
            self.handle_user_inputs()

            if menu_globals.game_paused:
                self.menu_manager.pause_menu.update(self.events)
                self.menu_manager.pause_menu.draw(self.window)
            else:
                # The actual game starts here
                self.window.fill(pygame.Color('black'))

                keyboard_keys = pygame.key.get_pressed()
                arrow_keys = (
                    keyboard_keys[pygame.K_RIGHT],
                    keyboard_keys[pygame.K_DOWN],
                    keyboard_keys[pygame.K_LEFT],
                    keyboard_keys[pygame.K_UP]
                )
                is_prey_controlled = any(arrow_keys) or is_prey_controlled

                for cell in self.population.all_cells:
                    is_controlled_by_user = self.population.all_cells.index(cell) == 0 and is_prey_controlled

                    cell.move(is_controlled_by_user, arrow_keys)
                    is_alive, new_born = cell.update_status()
                    if not is_alive:
                        self.population.cell_killed(cell, self.space)
                    if new_born:
                        self.population.add_cells(new_born)

                    self.camera.draw_transformed_image(cell.image, cell.body.position, cell.body.angle)

                for food in self.population.all_foods:
                    self.camera.draw_transformed_image(food.image, food.body.position)

                for wall in self.walls:
                    self.camera.draw_transformed_line(WALL_COLOR, wall.a, wall.b, 2*wall.radius)

                if menu_globals.game_clock % FPS == 0 and len(self.population.all_foods) <= MAX_FOODS:
                    foods = Food.create_new_foods(self.space, 5, self.images.food_image)
                    self.population.add_foods(foods)

            self.space.step(4/FPS)
            menu_globals.game_clock += 1
            self.clock.tick()
            pygame.display.flip()
            pygame.time.Clock().tick(FPS)
            pygame.display.set_caption(f"{GAME_TITLE}, fps: {self.clock.get_fps():.1f}")
