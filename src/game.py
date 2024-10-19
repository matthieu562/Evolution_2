import math
import pygame
import pymunk
import numpy as np

from brain import Brain
from camera import Camera  # Importation de la classe Camera
from cell import Cell
from collision_handler import Collision_Handler
from constants import *
from food import Food
from images import Images
from menu_manager import Menu_Manager
from population import Population
import menu_globals


NB_CELLS = 150
NB_FOODS = 300

class Game:

    def __init__(self, menu_manager, window) -> None:
        # Loop sur créé (new), init, start. Dans un tableau
        # Handle the Space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # Pas de gravité
        self.space.damping = 0.5  # Frottement global
        self.add_static_walls()

        # Handle collision
        self.collision_handler = Collision_Handler(self)
        self.space.add_collision_handler(CELL_COLLISION_TYPE, FOOD_COLLISION_TYPE).begin = self.collision_handler.handle_collision_cell_vs_food
        self.space.add_collision_handler(CELL_COLLISION_TYPE, CELL_COLLISION_TYPE).begin = self.collision_handler.handle_collision_cell_vs_cell
        self.space.add_collision_handler(CELL_COLLISION_TYPE, CELL_COLLISION_TYPE).separate  = self.collision_handler.separate_cells

        # self.menu_manager = Menu_Manager()
        self.window = window
        self.menu_manager = menu_manager
        self.clock = pygame.time.Clock()
        self.population = Population(self.space)
        self.images = Images()
        self.camera = Camera(self.window)

        # Populate space
        Cell.initialize()
        cell = Cell.create_new_cells(self.space, 1, self.images.user_cell_images)
        self.population.add_cells(cell)
        cells = Cell.create_new_cells(self.space, NB_CELLS, self.images.cell_images)
        self.population.add_cells(cells)
        foods = Food.create_new_foods(self.space, NB_CELLS, self.images.food_image)
        self.population.add_foods(foods)

        ## Filter creation
        self.cell_filter = pymunk.ShapeFilter(group=1)
        self.food_filter = pymunk.ShapeFilter(group=2)
        self.food_and_cell_filter = pymunk.ShapeFilter(group=1 | 2)

        # Brain
        self.brain = Brain()

        ## Attributes created later
        self.display_user_position = False
        self.follow_cell = True
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
                if event.key == pygame.K_SPACE:
                    self.display_user_position = not self.display_user_position
                if event.key == pygame.K_t:
                    self.follow_cell = not self.follow_cell
            # Gestion du zoom
            if event.type == pygame.MOUSEWHEEL:
                if event.y > 0:  # Zoom avant
                    zoom_amount = 0.1
                elif event.y < 0:  # Zoom arrière
                    zoom_amount = -0.1
                else:
                    zoom_amount = 0

                self.camera.zoom(zoom_amount)

            if event.type == pygame.VIDEORESIZE:
                # Redimensionner la fenêtre
                # self.window = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                # Adapter le menu à la nouvelle taille
                self.menu_manager.resize_menus(event.w, event.h)

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
        # offset = 20
        # self.walls = [
        #     pymunk.Segment(self.space.static_body, (0 - offset, 0), (0 - offset, WORLD_HEIGHT), offset),  # Bord gauche
        #     pymunk.Segment(self.space.static_body, (0, WORLD_HEIGHT + offset), (WORLD_WIDTH, WORLD_HEIGHT + offset), offset),  # Bord bas
        #     pymunk.Segment(self.space.static_body, (WORLD_WIDTH + offset, WORLD_HEIGHT), (WORLD_WIDTH + offset, 0), offset),  # Bord droit
        #     pymunk.Segment(self.space.static_body, (WORLD_WIDTH, 0 - offset), (0, 0 - offset), offset)  # Bord haut
        # ]
        radius = 8
        self.walls = [
            pymunk.Segment(self.space.static_body, (0, 0), (0, WORLD_HEIGHT), radius),  # Bord gauche
            pymunk.Segment(self.space.static_body, (0, WORLD_HEIGHT), (WORLD_WIDTH, WORLD_HEIGHT), radius),  # Bord bas
            pymunk.Segment(self.space.static_body, (WORLD_WIDTH, WORLD_HEIGHT), (WORLD_WIDTH, 0), radius),  # Bord droit
            pymunk.Segment(self.space.static_body, (WORLD_WIDTH, 0), (0, 0), radius)  # Bord haut
        ]
        for wall in self.walls:
            wall.elasticity = 0.9
            wall.friction = 0.5
        self.space.add(*self.walls)

    def is_player_alive(self):
        return any(cell.id == 0 for cell in self.population.all_cells)

    def enable_respawn(self):
        if menu_globals.respawn_enabled and not self.is_player_alive():
            cell = Cell.create_new_cells(self.space, 1, self.images.user_cell_images)
            cell[0].id = 0
            self.population.add_cells(cell)

    def run(self):
        is_prey_controlled = False

        # State machine
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
                self.enable_respawn()
                for cell in self.population.all_cells:
                    cell.update_status_before_move(self.food_and_cell_filter, self.population.all_player_family_members)

                self.collision_handler.handle_ongoing_collisions()
                    
                # Signaux slot python
                # Architecture : Component based Architecture
                for cell in self.population.all_cells:
                ## Debug
                    # self.camera.draw_id(cell)
                    # cell 0 used for debug :
                    # if self.population.all_cells.index(cell) == 0 and cell.target:
                    #     self.camera.draw_circle(cell.target)
                    if cell.id == 0 and self.display_user_position:
                        self.camera.draw_circle(cell)
                    if cell.id == 0 and self.follow_cell:
                        self.camera.follow_cell(cell)
                    is_controlled_by_user = cell.id == 0 and is_prey_controlled
                    brain_command = None
                    if cell.target:
                        accel, angle_speed = self.brain.bot_control(cell)
                        brain_command = (accel, angle_speed)
                    cell.move(is_controlled_by_user, arrow_keys, brain_command)
                    is_alive, new_born = cell.update_status()
                    if not is_alive:
                        self.population.cell_killed(cell, self.space)
                    if new_born:
                        self.population.add_cells(new_born)
                    if cell in self.population.all_player_family_members and not is_alive:
                        self.population.player_family_members_killed(cell)
                    if new_born and (cell.id == 0 or cell in self.population.all_player_family_members):
                        self.population.add_player_family_members(new_born)

                    self.camera.draw_transformed_image(cell.image, cell.body.position, cell.body.angle)
                    # self.camera.draw_vision_cone(cell)

                for food in self.population.all_foods:
                    self.camera.draw_transformed_image(food.image, food.body.position)

                for wall in self.walls:
                    self.camera.draw_transformed_line(WALL_COLOR, wall.a, wall.b, 2*wall.radius)

                if menu_globals.game_clock % FPS == 0 and len(self.population.all_foods) <= MAX_FOODS:
                    foods = Food.create_new_foods(self.space, FOOD_SPAWN_AMOUNT, self.images.food_image)
                    self.population.add_foods(foods)

                self.space.step(4/FPS)
                menu_globals.game_clock += 1
            self.clock.tick()
            pygame.display.flip()
            pygame.time.Clock().tick(FPS)
            pygame.display.set_caption(f"{GAME_TITLE}, fps: {self.clock.get_fps():.1f}")
