import math
import pygame
import pymunk
import random

from constants import *
from food import Food
import menu_globals
from pdb import set_trace as bp


USER_ANGLE_ACCEL = 70
USER_ACCEL = 2
SIGMA_ANGLE = 0.5
SIGMA_ACCEL = 0.5

class Cell:

    def __init__(self, space, position, radius, color, images, angle) -> None:
        mass = (radius - CELL_MIN_SIZE)/(CELL_MAX_SIZE - CELL_MIN_SIZE)*(CELL_MAX_MASS - CELL_MIN_MASS) + CELL_MIN_MASS
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        
        # Defines attributes
        self.body = pymunk.Body(mass, inertia)
        self.body.object = self

        self.body.position = position
        self.body.angle = angle
        
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.8
        self.shape.collision_type = CELL_COLLISION_TYPE
        
        self.color = color
        self.random_accel = 0
        self.random_accel_old = 0
        self.body_angular_velocity_old = 0
        self.energy = 0.75*CELL_MAX_ENERGY
        self.images = []
        for image in images:
            self.images.append(pygame.transform.scale(image, (int(radius * 2.2), int(radius * 2.2))))  # Adjust to radius
        self.image = self.images[0]
        self.life_points = CELL_MAX_LIFE_POINTS
        self.damage = 33/FPS
        self.last_reproduction_date = menu_globals.game_clock
        self.visible_objects = []
        self.target = None

        self.space = space
        self.space.add(self.body, self.shape)
  
    def move(self, is_controlled_by_user=False, arrow_keys=(0, 0, 0, 0), brain_command=None):
        self.compute_new_angle_accel(is_controlled_by_user, arrow_keys, brain_command)        
        self.compute_new_accel(is_controlled_by_user, arrow_keys, brain_command)
    
    def compute_new_angle_accel(self, is_controlled_by_user, user_input=None, brain_command=None):
        if is_controlled_by_user:
            if user_input[0] and not user_input[2]: # turn right
                self.body.angular_velocity = math.radians(USER_ANGLE_ACCEL)
            elif user_input[2] and not user_input[0]: # turn left
                self.body.angular_velocity = -math.radians(USER_ANGLE_ACCEL)
            else: 
                self.body.angular_velocity = 0
        else:
            if brain_command:
                self.body.angular_velocity = brain_command[1]
            else:
                # Add more chances to stay in the same direction 
                self.body.angular_velocity = random.gauss(self.body.angular_velocity + self.body_angular_velocity_old, SIGMA_ANGLE)/2.1
            self.body_angular_velocity_old = self.body.angular_velocity
                # self.body.angular_velocity = random.uniform(-USER_ANGLE_ACCEL/100, USER_ANGLE_ACCEL/100)
    
    def compute_new_accel(self, is_controlled_by_user, user_input=None, brain_command=None):
        if is_controlled_by_user:
            if user_input[3] and not user_input[1]: # accel
                accel_x = USER_ACCEL*math.cos(self.body.angle)
                accel_y = USER_ACCEL*math.sin(self.body.angle)
            elif user_input[1] and not user_input[3]: # decel
                accel_x = -USER_ACCEL*math.cos(self.body.angle)
                accel_y = -USER_ACCEL*math.sin(self.body.angle)
            else: 
                accel_x = 0
                accel_y = 0
        else:
            if brain_command:
                self.random_accel = brain_command[0]
            else:
                # Add more chances to keep the same velocity
                # WARNING, One guy might be very lucky and accelerate very hard for several seconds and reach speed of light
                self.random_accel = random.gauss(self.random_accel + self.random_accel_old, SIGMA_ACCEL)/2.05
            self.random_accel_old = self.random_accel
            # random_accel = 10*random.uniform(-USER_ACCEL, USER_ACCEL)
            
            accel_x = self.random_accel*math.cos(self.body.angle)
            accel_y = self.random_accel*math.sin(self.body.angle)
            
        self.body.velocity = pymunk.Vec2d(self.body.velocity.x + accel_x, self.body.velocity.y + accel_y)
                     
    # # Simple circle
    # def draw(self, window):
    #     pygame.draw.circle(window, self.color, self.body.position, self.shape.radius)
    #     pygame.draw.line(window, self.color, self.body.position, (self.body.position[0] + 1.3*self.shape.radius*math.cos(self.body.angle), self.body.position[1] + 1.3*self.shape.radius*math.sin(self.body.angle)), 4)
    
    @classmethod
    def create_new_cells(cls, space, nb_new_cell, images, x=None, y=None, angle=0, radius=None):
        new_cells = []
        for i in range(nb_new_cell):
            # Réinitialiser les variables à None pour garantir la génération de nouvelles valeurs si non fournies
            x_rand = x if x is not None else random.randint(0, WINDOW_WIDTH)
            y_rand = y if y is not None else random.randint(0, WINDOW_HEIGHT)
            angle_rand = angle if angle else math.radians(random.randint(0, 360))
            radius_rand = radius if radius is not None else random.randint(CELL_MIN_SIZE, CELL_MAX_SIZE)
            color = (122, 0, 122) if i != 0 else (0, 45, 223)
            new_cells.append(Cell(space, (x_rand, y_rand), radius_rand, color, images, angle_rand))
        return new_cells
            
    def update_status_before_move(self, food_and_cell_filter):
        self.update_vision(food_and_cell_filter)
        self.select_target()
        
    def update_status(self):
        self.choose_correct_image()
        self.update_image_energy_level()
        self.decrease_energy()
        new_born = self.get_birth()
        return self.is_alive(), new_born

    def select_target(self):
        self.target = None
        for visible_object in self.visible_objects[::-1]:
            if isinstance(visible_object, Food):
                self.target = visible_object
        if not self.target and self.visible_objects:
            self.target = self.visible_objects[0]
                
    def is_alive(self):
        has_energy=True if self.energy > 0 else False
        has_life_points=True if self.life_points > 0 else False
        return all((has_energy, has_life_points))

    def decrease_energy(self):
        if menu_globals.game_clock % FPS == 0:
            self.energy = self.energy - ENERGY_LOSS_OVERTIME
    
    def has_eaten(self, body):
        self.energy += body.body.mass
        self.life_points += 5
        if self.energy > CELL_MAX_ENERGY:
            self.energy = CELL_MAX_ENERGY
        if self.life_points > CELL_MAX_LIFE_POINTS:
            self.life_points = CELL_MAX_LIFE_POINTS

    def choose_correct_image(self):
        if self.life_points >= 2*CELL_MAX_LIFE_POINTS/3:
            self.image = self.images[0]
        elif self.life_points >= CELL_MAX_LIFE_POINTS/3:
            self.image = self.images[1]
        elif self.life_points >= 0:
            self.image = self.images[2]
        # else:
        #     self.image = self.images[0]

    def update_image_energy_level(self):
        # Calculer l'alpha (la transparence de l'image) en fonction de l'énergie
        alpha_min_threshold = 90 # sur 255
        if self.energy > 100 / 4:
            alpha = int(((self.energy - (100 / 4)) / (100 - (100 / 4))) * (255 - alpha_min_threshold) + alpha_min_threshold)
        else:
            alpha = alpha_min_threshold
        self.image.set_alpha(alpha)

    def losses_life_points(self, attacker):
        # Include oppressor's speed in damage ?
        # Damage is applied only once per collision, thus you need to charge the opponent to apply multiple damage
        self.life_points -= self.damage

    def get_charged(self, attacker):
        self.life_points -= min(20, max(attacker.body.velocity.length, 10))

    def get_birth(self):
        if self.energy > 0.75*CELL_MAX_ENERGY and menu_globals.game_clock - self.last_reproduction_date > REPRODUCTION_DELAY*FPS:
            self.energy -= 25
            self.last_reproduction_date = menu_globals.game_clock
            x = self.body.position[0] + 3*self.shape.radius*math.cos(self.body.angle + math.pi)
            y = self.body.position[1] + 3*self.shape.radius*math.sin(self.body.angle + math.pi)
            return Cell.create_new_cells(self.space, 1, self.images, x, y, self.body.angle + math.pi, self.shape.radius)

    # Draw cell as a simple circle with the given color, should be in camera class
    def draw(self, window):
        rotated_image = pygame.transform.rotate(self.image, -math.degrees(self.body.angle))
        alpha_min_threshold = 90
        if self.energy > 100/4:
            alpha = int(((self.energy - (100/4)) / (100 - (100/4))) * (255 - alpha_min_threshold) + alpha_min_threshold)
        else:
            alpha = alpha_min_threshold
        rotated_image.set_alpha(alpha)
        image_rect = rotated_image.get_rect(center=self.body.position)
        window.blit(rotated_image, image_rect.topleft)

    def update_vision(self, food_and_cell_filter):
        """Met à jour la liste des objets visibles. Ajoute ceux qui viennent d'entrer et retire ceux qui ont quitté le champ de vision."""
        current_visible_objects = []
        query_info = self.space.point_query(self.body.position, VISION_DISTANCE, food_and_cell_filter)

        # # Créer une liste pour stocker les résultats valides
        # valid_results = []
        # for result in query_info:
        #     if result.shape.collision_type == CELL_COLLISION_TYPE or result.shape.collision_type == FOOD_COLLISION_TYPE:
        #         other = result.shape.body.object
        #         if isinstance(other, Cell) or isinstance(other, Food) and other != self:
        #             valid_results.append(other)
        # sorted_objects = sorted(valid_results, key=lambda other: (other.body.position - self.body.position).length)
        
        valid_results = []
        for result in query_info:
            if result.shape.collision_type == CELL_COLLISION_TYPE or result.shape.collision_type == FOOD_COLLISION_TYPE:
                other = result.shape.body.object
                if (isinstance(other, Cell) or isinstance(other, Food)) and other != self:
                    distance = (other.body.position - self.body.position).length
                    valid_results.append((other, distance))
        # Trier en fonction de la distance
        sorted_results = sorted(valid_results, key=lambda x: x[1])
        sorted_objects = [obj for obj, distance in sorted_results]
        # Nearest result :
        # min_result = min(sorted_results, key=lambda x: x[1])
        # print(sorted_objects)

        # # On utilise le `shape_query` pour trouver les objets proches dans un rayon
        # query_info = self.space.point_query(self.body.position, VISION_DISTANCE, food_and_cell_filter)
        # results_with_distance = [(result.shape.body, (result.shape.body.position - self.body.position).length)for result in query_info]  
        # sorted_results = sorted(results_with_distance, key=lambda x: x[1])
        # # Extraire les corps triés
        # sorted_bodies = [body for body, distance in sorted_results]
        # for result in query_info:
        #     # On pourrait faire ce tri juste apres avoir recupéré query_info pour plus de perfo
        #     if result.shape.collision_type == CELL_COLLISION_TYPE or result.shape.collision_type == FOOD_COLLISION_TYPE:
        #         other = bodies.shape.body.object
        for sorted_object in sorted_objects:
                # if result.shape.collision_type in (CELL_COLLISION_TYPE, FOOD_COLLISION_TYPE):
                if self.is_in_vision(sorted_object.body.position):
                    current_visible_objects.append(sorted_object)

        # Identifier les objets qui ne sont plus dans le champ de vision
        for body in self.visible_objects[:]:  # Itérer sur une copie pour modification sûre
            if body not in current_visible_objects:
                self.visible_objects.remove(body)
        self.visible_objects = current_visible_objects
        
    def is_in_vision(self, position):
        """Vérifie si une position donnée est dans le cône de vision de la cellule."""
        dx = position.x - self.body.position.x
        dy = position.y - self.body.position.y
        # Calcul de l'angle entre la cellule et l'objet
        angle_to_object = math.atan2(dy, dx)
        angle_diff = (self.body.angle - angle_to_object + math.pi) % (2 * math.pi) - math.pi
        return abs(angle_diff) <= VISION_ANGLE / 2
