import math
import pygame
import pymunk
import random

from constants import *


class Food:
        
    def __init__(self, space, position, radius, color, image) -> None:
        mass = (radius - CELL_MIN_SIZE)/(CELL_MAX_SIZE - CELL_MIN_SIZE)*(CELL_MAX_MASS - CELL_MIN_MASS) + CELL_MIN_MASS
        inertia = pymunk.moment_for_circle(mass, 0, radius)
        
        # Defines attributes
        self.body = pymunk.Body(mass, inertia)
        self.color = color
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.collision_type = FOOD_COLLISION_TYPE
        self.image = pygame.transform.scale(image, (int(radius * 2.2), int(radius * 2.2)))  # Adjust to radius

        # Update "inner" attributes
        self.body.position = position
        self.shape.elasticity = 0.8
        space.add(self.body, self.shape)
        
    # # Simple circle        
    # def draw(self, window):
    #     pygame.draw.circle(window, self.color, self.body.position, self.shape.radius)

    # def create_new_foods(self, nb_new_food):
    #     for i in range(nb_new_food):
    #         x=random.randint(0, WINDOW_WIDTH)
    #         y=random.randint(0, WINDOW_HEIGHT)
    #         radius=random.randint(CELL_MIN_SIZE, CELL_MAX_SIZE)
    #         color=(120, 190, 120) 
    #         self.all_foods.append(Food(self.space, (x, y), radius, color))
            
    @classmethod
    def create_new_foods(cls, space, nb_new_food, image):
        new_foods = []
        for i in range(nb_new_food):
            x=random.randint(0, WINDOW_WIDTH)
            y=random.randint(0, WINDOW_HEIGHT)
            radius=random.randint(CELL_MIN_SIZE, CELL_MAX_SIZE)
            color=(122, 0, 122) if i != 0 else (0, 45, 223)
            # image=image
            new_foods.append(Food(space, (x, y), radius, color, image))
        return new_foods


    def draw(self, window):
        x, y = self.body.position
        image_rect = self.image.get_rect(center=(x, y))
        window.blit(self.image, image_rect.topleft)
