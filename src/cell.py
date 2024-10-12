import math
import pygame
import pymunk
import random

from constants import *
import menu_globals

USER_ANGLE_ACCEL = 90
USER_ACCEL = 3
ACCEL = 10
SIGMA_ANGLE = 0.5
SIGMA_ACCEL = 0.5

class Cell:

    def __init__(self, space, position, radius, color, images, angle) -> None:
        mass = (radius - CELL_MIN_SIZE)/(CELL_MAX_SIZE - CELL_MIN_SIZE)*(CELL_MAX_MASS - CELL_MIN_MASS) + CELL_MIN_MASS
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        
        # Defines attributes
        self.body = pymunk.Body(mass, inertia)
        self.body.cell_object = self
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
        self.damage = 20
        self.last_reproduction_date = menu_globals.game_clock

        self.space = space
        self.space.add(self.body, self.shape)
  
    def move(self, is_controlled_by_user=False, arrow_keys=(0, 0, 0, 0)):
        self.compute_new_angle_accel(is_controlled_by_user, arrow_keys)        
        self.compute_new_accel(is_controlled_by_user, arrow_keys)
    
    def compute_new_angle_accel(self, is_controlled_by_user, user_input=None):
        if is_controlled_by_user:
            if user_input[0] and not user_input[2]: # turn right
                self.body.angular_velocity = math.radians(USER_ANGLE_ACCEL)
            elif user_input[2] and not user_input[0]: # turn left
                self.body.angular_velocity = -math.radians(USER_ANGLE_ACCEL)
            else: 
                self.body.angular_velocity = 0
        else:
            # Add more chances to stay in the same direction 
            self.body.angular_velocity = random.gauss(self.body.angular_velocity + self.body_angular_velocity_old, SIGMA_ANGLE)/2.1
            self.body_angular_velocity_old = self.body.angular_velocity
            # self.body.angular_velocity = random.uniform(-USER_ANGLE_ACCEL/100, USER_ANGLE_ACCEL/100)
    
    def compute_new_accel(self, is_controlled_by_user, user_input=None):
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
            radius_rand = radius if radius is not None else random.randint(CELL_MIN_SIZE, CELL_MAX_SIZE)
            
            color = (122, 0, 122) if i != 0 else (0, 45, 223)
            new_cells.append(Cell(space, (x_rand, y_rand), radius_rand, color, images, angle))
        return new_cells

    def update_status(self):
        self.choose_correct_image()
        self.update_image_energy_level()
        self.decrease_energy()
        new_born = self.get_birth()
        return self.is_alive(), new_born

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
