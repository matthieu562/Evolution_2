import math


MAX_ACCELERATION_BOT = 2.5 # 2 
MAX_ANGULAR_SPEED_BOT = 140 # 70
MAX_SPEED_BOT = 100000

def calculate_relative_angle(cell, target_x, target_y):
    cell.x, cell.y = cell.body.position.x, cell.body.position.y

    # Calcul de l'angle de direction vers le point cible
    dx = target_x - cell.x
    dy = target_y - cell.y
    angle_to_target = math.atan2(dy, dx)

    # Calcul de l'angle relatif à l'orientation de la créature
    relative_angle = angle_to_target - cell.body.angle

    # Ajustement de l'angle pour qu'il soit entre -pi et pi
    if relative_angle > math.pi:
        relative_angle -= 2 * math.pi
    elif relative_angle < -math.pi:
        relative_angle += 2 * math.pi

    return relative_angle

class Brain:

    def __init__(self) -> None:
        pass

    def bot_control(self, cell):
        cell.target.x, cell.target.y = cell.target.body.position.x, cell.target.body.position.y
        cell.x, cell.y = cell.body.position.x, cell.body.position.y
        angle_diff = calculate_relative_angle(cell, cell.target.x, cell.target.y)
        acceleration = MAX_ACCELERATION_BOT 
        moving_angle = 0
        speed = cell.body.velocity.length
        if speed > - math.pi / math.radians(MAX_ANGULAR_SPEED_BOT) / 2:# la valeur apres le > n'est pas optimal !! Le bot cyan le bas, une difference notable est cette valeur, mais ca pourrait etre une autre raison
            if abs(angle_diff) > math.radians(MAX_ANGULAR_SPEED_BOT):
                nb_rotation_before_90 = math.floor((abs(angle_diff) - math.pi / 2) // math.radians(MAX_ANGULAR_SPEED_BOT))
                if nb_rotation_before_90 > 1 and speed > MAX_SPEED_BOT - nb_rotation_before_90:
                    acceleration = -MAX_ACCELERATION_BOT/2
                elif nb_rotation_before_90 == 1 and speed > MAX_SPEED_BOT - nb_rotation_before_90:
                    acceleration = 0
                moving_angle = math.radians(MAX_ANGULAR_SPEED_BOT) * math.copysign(1, angle_diff)
            elif abs(angle_diff) > 0:
                moving_angle = angle_diff
            else:
                moving_angle = 0
        else:
            if abs((math.pi - abs(angle_diff))) > math.radians(MAX_ANGULAR_SPEED_BOT):
                moving_angle = -math.radians(MAX_ANGULAR_SPEED_BOT) * math.copysign(1, angle_diff)
            elif abs((math.pi - abs(angle_diff))) > 0:
                moving_angle = -(math.pi - abs(angle_diff)) * math.copysign(1, angle_diff) #-math.radians(MAX_ANGULAR_SPEED_BOT * abs((math.pi - angle_diff)) / math.pi)
            else:
                moving_angle = 0
        
        return acceleration, 2*moving_angle
