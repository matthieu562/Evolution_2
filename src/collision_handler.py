import math
import pymunk


MOUTH_SIZE  = 40 # En degrees, a une ouverture de 40° de chaque coté du centre de la bouche

class Collision_Handler:
    def __init__(self, game) -> None:
        self.game = game
    
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
            for cell in self.game.population.all_cells:  # Assuming all_cells contains the list of cells
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

        return True  # Continue with the normal collision handling

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
