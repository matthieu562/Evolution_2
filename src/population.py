from constants import *


class Population:
    def __init__(self, space) -> None:
        self.all_cells = []
        self.all_foods = []
        self.space = space
        
    def add_cells(self, cells):
        if isinstance(cells, list):
            self.all_cells.extend(cells)
        else:
            self.all_cells.append(cells) # Not really used

    def add_foods(self, foods):
        if isinstance(foods, list):
            self.all_foods.extend(foods)
        else:
            self.all_foods.append(foods) # Not really used

    def cell_killed(self, dead_cell, space):
        self.all_cells.remove(dead_cell)
        space.remove(dead_cell.body, dead_cell.shape)
        
    def food_killed(self, dead_food, space):
        self.all_foods.remove(dead_food)
        space.remove(dead_food.body, dead_food.shape)