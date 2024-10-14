import math
import pymunk

from constants import *


MOUTH_SIZE  = math.radians(35) # a une ouverture de 40° de chaque coté du centre de la bouche

class Collision_Handler:
    def __init__(self, game) -> None:
        self.game = game
        self.colliding_cells = set() 

    def handle_collision_cell_vs_cell(self, arbiter, space, data):
        cell1_shape, cell2_shape = arbiter.shapes
        cell1_body = cell1_shape.body
        cell2_body = cell2_shape.body

        cell1_object = cell1_body.object
        cell2_object = cell2_body.object

        # Ajouter les cellules à l'ensemble des collisions
        self.colliding_cells.add(tuple(sorted((cell1_object, cell2_object))))

        is_cell1_facing, is_cell2_facing = self.is_facing_each_other(cell1_body, cell2_body)
        if is_cell1_facing:
            cell2_object.get_charged(cell1_object)

        if is_cell2_facing:
            cell1_object.get_charged(cell2_object)

        return True  # Continue with the normal collision handling

    def separate_cells(self, arbiter, space, data):
        cell1_shape, cell2_shape = arbiter.shapes
        cell1_body = cell1_shape.body
        cell2_body = cell2_shape.body

        cell1_object = cell1_body.object
        cell2_object = cell2_body.object

        # Retirer les cellules de l'ensemble des collisions
        self.colliding_cells.discard(tuple(sorted((cell1_object, cell2_object))))
        return True

    def handle_collision_cell_vs_food(self, arbiter, space, data):
        ## Handle cell vs food
        cell_shape, food_shape = arbiter.shapes
        cell_body = cell_shape.body
        food_body = food_shape.body
        collision_vector = pymunk.Vec2d(*(food_body.position - cell_body.position))

        # Calculate the angle of this vector relative to the cell's angle
        collision_angle = math.atan2(collision_vector.y, collision_vector.x)

        # Normalize the angles
        cell_angle = cell_body.angle % (2 * math.pi)
        collision_angle = collision_angle % (2 * math.pi)
        angle_diff = abs(collision_angle - cell_angle)

        # Make sure the difference is between 0 and π
        if angle_diff > math.pi:
            angle_diff = (2 * math.pi) - angle_diff

        # If the difference is within the range degrees, consider it a valid collision
        if angle_diff <= MOUTH_SIZE:
            cell_object = None
            for cell in self.game.population.all_cells: 
                if cell.shape == cell_shape:
                    cell_object = cell
                    break

            food_object = None
            for food in self.game.population.all_foods:
                if food.shape == food_shape:
                    food_object = food
                    break
            
            if cell_object and food_object:
                self.game.population.food_killed(food_object, space)
                cell_object.has_eaten(food_object)

        return True 

    def is_facing_each_other(self, cell1_body, cell2_body):        
        collision_vector = pymunk.Vec2d(*(cell2_body.position - cell1_body.position))
        collision_angle = math.atan2(collision_vector.y, collision_vector.x)
        
        # Normaliser les angles des cellules
        cell1_angle = cell1_body.angle % (2 * math.pi)
        cell2_angle = cell2_body.angle % (2 * math.pi)
        collision_angle = collision_angle % (2 * math.pi)

        # Calculer la différence angulaire entre cell1 et le vecteur collision
        angle_diff1 = abs(collision_angle - cell1_angle)
        if angle_diff1 > math.pi:
            angle_diff1 = (2 * math.pi) - angle_diff1
        is_cell1_facing = angle_diff1 <= MOUTH_SIZE

        # Calculer la différence angulaire entre cell2 et le vecteur inverse (de cell2 vers cell1)
        collision_vector_reverse = -collision_vector
        reverse_collision_angle = math.atan2(collision_vector_reverse.y, collision_vector_reverse.x)
        reverse_collision_angle = reverse_collision_angle % (2 * math.pi)
        
        angle_diff2 = abs(reverse_collision_angle - cell2_angle)
        if angle_diff2 > math.pi:
            angle_diff2 = (2 * math.pi) - angle_diff2
        is_cell2_facing = angle_diff2 <= MOUTH_SIZE

        return is_cell1_facing, is_cell2_facing
    
    def handle_ongoing_collisions(self):
        for cell1, cell2 in self.colliding_cells:
            is_cell1_facing, is_cell2_facing = self.is_facing_each_other(cell1.body, cell2.body)
            if is_cell1_facing:
                cell2.losses_life_points(cell1)
            if is_cell2_facing:
                cell1.losses_life_points(cell2)

    # def handle_collision_cell_vs_cell(self, arbiter, space, data):
    #     ## Handle cell vs cell
    #     # Récupérer les shapes impliquées dans la collision
    #     cell1_shape, cell2_shape = arbiter.shapes
    #     cell1_body = cell1_shape.body
    #     cell2_body = cell2_shape.body

    #     # Vérifier si les deux cellules se font face
    #     cell1_facing, cell2_facing = self.is_facing_each_other(cell1_body, cell2_body)
    #     # cell1_object = self.population.body_to_cell.get(cell1_body.id)
    #     # cell2_object = self.population.body_to_cell.get(cell2_body.id)
    #     cell1_object = cell1_body.object
    #     cell2_object = cell2_body.object
        
    #     if cell1_facing:
    #         cell2_object.losses_life_points(cell1_object)

    #     if cell2_facing:
    #         cell1_object.losses_life_points(cell2_object)
            
    #     return True  # Continue with the normal collision handling


    ## Deletes food whether its an collision with a 40° angle or not 
    # def handle_collision(self, arbiter, space, data):
    #     # Get the shapes involved in the collision
    #     cell_shape, food_shape = arbiter.shapes

    #     # Find the Food object from your Population list
    #     food_object = None
    #     for food in self.game.population.all_foods:
    #         if food.shape == food_shape:
    #             food_object = food
    #             break
        
    #     # Remove the Food object from the Population
    #     if food_object:
    #         self.game.population.all_foods.remove(food_object)
    #         space.remove(food_object.body, food_object.shape)
        
    #     return True  # Continue with the normal collision handling
