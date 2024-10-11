import math
import os
import pygame
import pymunk
import numpy as np

from cell import Cell
from constants import *
from food import Food
from images import Images
from menu_manager import Menu_Manager
from population import Population
import menu_globals


NB_CELLS = 10
NB_FOODS = 50
MOUTH_SIZE  = 40 # En degrees, a une ouverture de 40° de chaque coté du centre de la bouche

class Game:
    
    def __init__(self) -> None:
        pygame.init()
        
        ## Set up window ##
        pygame.display.set_caption(GAME_TITLE)
        os.environ['SDL_VIDEO_WINDOW_POS'] = '700,100' # Defines where the windows spawns

        # Handle the Space
        self.space = pymunk.Space()
        self.space.gravity = (0, 0)  # Pas de gravité
        self.space.damping = 0.5  # Frottement global
        self.add_static_walls()
        self.space.add_collision_handler(CELL_COLLISION_TYPE, FOOD_COLLISION_TYPE).begin = self.handle_collision_cell_vs_food
        self.space.add_collision_handler(CELL_COLLISION_TYPE, CELL_COLLISION_TYPE).begin = self.handle_collision_cell_vs_cell

        ## Init attributes
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.menu_manager = Menu_Manager()
        self.clock = pygame.time.Clock()
        self.population = Population(self.space)
        self.images = Images()

        # Populate space
        cell = Cell.create_new_cells(self.space, 1, self.images.user_cell_images)
        self.population.add_cells(cell)
        cells = Cell.create_new_cells(self.space, NB_CELLS, self.images.cell_images)
        self.population.add_cells(cells)
        foods = Food.create_new_foods(self.space, NB_CELLS, self.images.food_image)
        self.population.add_foods(foods)
        
        ## Attributes created later
        self.events = None


    def is_facing_each_other(self, cell1_body, cell2_body, angle_tolerance_degrees=40):
        # Convertir la tolérance angulaire en radians
        angle_tolerance_radians = math.radians(angle_tolerance_degrees)
        
        # Calculer le vecteur de collision de cell1 vers cell2
        collision_vector = pymunk.Vec2d(*(cell2_body.position - cell1_body.position))
        
        # Calculer l'angle du vecteur de collision
        collision_angle = math.atan2(collision_vector.y, collision_vector.x)
        
        # Normaliser les angles des cellules
        cell1_angle = cell1_body.angle % (2 * math.pi)
        cell2_angle = cell2_body.angle % (2 * math.pi)
        collision_angle = collision_angle % (2 * math.pi)

        # Calculer la différence angulaire entre cell1 et le vecteur collision
        angle_diff1 = abs(collision_angle - cell1_angle)
        if angle_diff1 > math.pi:
            angle_diff1 = (2 * math.pi) - angle_diff1

        # Vérifier si cell1 fait face à cell2 (angle dans la tolérance)
        cell1_facing = angle_diff1 <= angle_tolerance_radians

        # Calculer la différence angulaire entre cell2 et le vecteur inverse (de cell2 vers cell1)
        collision_vector_reverse = -collision_vector
        reverse_collision_angle = math.atan2(collision_vector_reverse.y, collision_vector_reverse.x)
        reverse_collision_angle = reverse_collision_angle % (2 * math.pi)
        
        angle_diff2 = abs(reverse_collision_angle - cell2_angle)
        if angle_diff2 > math.pi:
            angle_diff2 = (2 * math.pi) - angle_diff2

        # Vérifier si cell2 fait face à cell1 (angle dans la tolérance)
        cell2_facing = angle_diff2 <= angle_tolerance_radians

        return cell1_facing, cell2_facing

    def handle_collision_cell_vs_cell(self, arbiter, space, data):
        ## Handle cell vs cell
        # Récupérer les shapes impliquées dans la collision
        cell1_shape, cell2_shape = arbiter.shapes
        cell1_body = cell1_shape.body
        cell2_body = cell2_shape.body

        # Vérifier si les deux cellules se font face
        cell1_facing, cell2_facing = self.is_facing_each_other(cell1_body, cell2_body)
        # cell1_object = self.population.body_to_cell.get(cell1_body.id)
        # cell2_object = self.population.body_to_cell.get(cell2_body.id)
        cell1_object = cell1_body.cell_object
        cell2_object = cell2_body.cell_object
        
        if cell1_facing:
            cell2_object.losses_life_points(cell1_object)

        if cell2_facing:
            cell1_object.losses_life_points(cell2_object)
            
        return True  # Continue with the normal collision handling


    def handle_collision_cell_vs_food(self, arbiter, space, data):
        ## Handle cell vs food
        # Get the shapes involved in the collision
        cell_shape, food_shape = arbiter.shapes
        cell_body = cell_shape.body
        food_body = food_shape.body

        # Vector from the cell's position to the food's position
        collision_vector = pymunk.Vec2d(*(food_body.position - cell_body.position))

        # Calculate the angle of this vector relative to the cell's angle
        collision_angle = math.atan2(collision_vector.y, collision_vector.x)

        # Normalize the angles
        cell_angle = cell_body.angle % (2 * math.pi)
        collision_angle = collision_angle % (2 * math.pi)

        # Calculate the angular difference
        angle_diff = abs(collision_angle - cell_angle)

        # Make sure the difference is between 0 and π
        if angle_diff > math.pi:
            angle_diff = (2 * math.pi) - angle_diff

        # If the difference is within the range degrees, consider it a valid collision
        if angle_diff <= math.radians(MOUTH_SIZE):
            cell_object = None
            for cell in self.population.all_cells:  # Assuming all_cells contains the list of cells
                if cell.shape == cell_shape:
                    cell_object = cell
                    break

            food_object = None
            for food in self.population.all_foods:
                if food.shape == food_shape:
                    food_object = food
                    break
            
            if cell_object and food_object:
                self.population.food_killed(food_object, space)
                cell_object.has_eaten(food_object)

        return True  # Continue with the normal collision handling

    ## Deletes food whether its an collision with a 40° angle or not 
    # def handle_collision(self, arbiter, space, data):
    #     # Get the shapes involved in the collision
    #     cell_shape, food_shape = arbiter.shapes

    #     # Find the Food object from your Population list
    #     food_object = None
    #     for food in self.population.all_foods:
    #         if food.shape == food_shape:
    #             food_object = food
    #             break
        
    #     # Remove the Food object from the Population
    #     if food_object:
    #         self.population.all_foods.remove(food_object)
    #         space.remove(food_object.body, food_object.shape)
        
    #     return True  # Continue with the normal collision handling
  
    def handle_user_inputs(self):
        for event in self.events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_globals.game_paused = not menu_globals.game_paused

    def add_static_walls(self):
        """Ajoute des lignes statiques aux bords de la fenêtre."""
        walls = [
            pymunk.Segment(self.space.static_body, (0, 0), (0, WINDOW_HEIGHT), 5),  # Bord gauche
            pymunk.Segment(self.space.static_body, (0, WINDOW_HEIGHT), (WINDOW_WIDTH, WINDOW_HEIGHT), 5),  # Bord bas
            pymunk.Segment(self.space.static_body, (WINDOW_WIDTH, WINDOW_HEIGHT), (WINDOW_WIDTH, 0), 5),  # Bord droit
            pymunk.Segment(self.space.static_body, (WINDOW_WIDTH, 0), (0, 0), 5)  # Bord haut
        ]
        for wall in walls:
            wall.elasticity = 0.9  # Coefficient de rebond
            wall.friction = 0.5  # Coefficient de friction
        self.space.add(*walls)

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

                    # if is_controlled_by_user:
                    #     cell.move(is_controlled_by_user, arrow_keys)
                    # elif menu_globals.game_clock % (FPS/2) == 0:
                    cell.move(is_controlled_by_user, arrow_keys)
                    # if is_controlled_by_user:
                    #     if not cell.update_status():
                    #         self.population.cell_killed(cell, self.space)
                    # else :
                    is_alive, new_born = cell.update_status()
                    if not is_alive:
                        self.population.cell_killed(cell, self.space)
                    if new_born:
                        self.population.add_cells(new_born)

                    cell.draw(self.window)

                for food in self.population.all_foods:
                    food.draw(self.window)
                    
                if menu_globals.game_clock % FPS == 0 and len(self.population.all_foods) <= 50:
                    foods = Food.create_new_foods(self.space, 5, self.images.food_image)
                    self.population.add_foods(foods)

            self.space.step(4/FPS)
            menu_globals.game_clock += 1
            self.clock.tick()
            pygame.display.flip()
            pygame.time.Clock().tick(FPS)
            pygame.display.set_caption(f"{GAME_TITLE}, fps: {self.clock.get_fps():.1f}")

