import math
import pygame
import sys

from constants import *


class Camera:

    def __init__(self, window) -> None:
        self.zoom_factor = 1
        self.offset_x, self.offset_y = 0, 0
        self.dragging = False
        self.last_mouse_pos = None
        self.window = window
        self.font = pygame.font.Font(None, 36)

    def transform_shape(self, x, y):
        return x * self.zoom_factor + self.offset_x, y * self.zoom_factor + self.offset_y

    def draw_transformed_image(self, image, pos, angle=0):
        x, y = pos
        transformed_x, transformed_y = self.transform_shape(x, y)
        
        # Redimensionner l'image en fonction du facteur de zoom
        new_width = int(image.get_width() * self.zoom_factor)
        new_height = int(image.get_height() * self.zoom_factor)
        resized_image = pygame.transform.scale(image, (new_width, new_height))

        # Appliquer la rotation à l'image
        rotated_image = pygame.transform.rotate(resized_image, -math.degrees(angle))
        
        # Obtenir le rectangle de l'image après rotation pour centrer l'image sur la position
        image_rect = rotated_image.get_rect(center=(transformed_x, transformed_y))

        # Dessiner l'image transformée dans la fenêtre
        self.window.blit(rotated_image, image_rect.topleft)

    def draw_transformed_line(self, color, start_pos, end_pos, width):
        x1, y1 = self.transform_shape(start_pos.x, start_pos.y)
        x2, y2 = self.transform_shape(end_pos.x, end_pos.y)
        x1, y1 = int(x1), int(y1)
        x2, y2 = int(x2), int(y2)
        pygame.draw.line(self.window, color, (x1, y1), (x2, y2), int(width))

    def zoom(self, zoom_amount):
        # Obtenir la position de la souris
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Convertir la position de la souris dans le système de coordonnées de la caméra
        world_mouse_x = (mouse_x - self.offset_x) / self.zoom_factor
        world_mouse_y = (mouse_y - self.offset_y) / self.zoom_factor
        
        # Appliquer le zoom
        self.zoom_factor += zoom_amount
        self.zoom_factor = min(5, max(self.zoom_factor, 0.1))  # Empêcher le zoom de devenir négatif ou nul

        # Recalculer l'offset pour maintenir la position de la souris constante
        self.offset_x = mouse_x - world_mouse_x * self.zoom_factor
        self.offset_y = mouse_y - world_mouse_y * self.zoom_factor

    def draw_vision_cone(self, cell):
        """Dessine le cône de vision de la cellule."""
        vision_distance = VISION_DISTANCE #* self.zoom_factor
        angle_left = cell.body.angle - VISION_ANGLE / 2
        angle_right = cell.body.angle + VISION_ANGLE / 2
        
        point_left = pygame.Vector2()
        point_left.x = cell.body.position.x + vision_distance * math.cos(angle_left)
        point_left.y = cell.body.position.y + vision_distance * math.sin(angle_left)
        
        point_right = pygame.Vector2()
        point_right.x = cell.body.position.x + vision_distance * math.cos(angle_right)
        point_right.y = cell.body.position.y + vision_distance * math.sin(angle_right)
        
        self.draw_transformed_line((255, 255, 0), cell.body.position, point_left, 2)  # Ligne gauche
        self.draw_transformed_line((255, 255, 0), cell.body.position, point_right, 2)  # Ligne droite
        
    def draw_circle(self, cell):
        x, y = cell.body.position
        color = (255, 255, 255)
        transformed_x, transformed_y = self.transform_shape(x, y)
        transformed_radius = int(cell.shape.radius * self.zoom_factor * 4)
        pygame.draw.circle(self.window, color, (int(transformed_x), int(transformed_y)), int(transformed_radius), transformed_radius)
    
    def draw_id(self, cell):
        """Dessine l'ID de la cellule au-dessus de la cellule."""
        x, y = cell.body.position
        transformed_x, transformed_y = self.transform_shape(x, y)

        # Créer une surface de texte pour l'ID
        id_text = self.font.render(str(cell.id), True, (255, 0, 0))  # Rouge
        text_rect = id_text.get_rect(center=(int(transformed_x), int(transformed_y - 20)))  # Positionner au-dessus de la cellule

        # Dessiner le texte dans la fenêtre
        self.window.blit(id_text, text_rect)

    def follow_cell(self, cell):
        """Fait en sorte que la caméra suive une cellule en la gardant au centre de l'écran."""
        # Centrer la cellule à l'écran
        self.offset_x = (WINDOW_WIDTH / 2) - (cell.body.position.x * self.zoom_factor)
        self.offset_y = (WINDOW_HEIGHT / 2) - (cell.body.position.y * self.zoom_factor)

    # # Fonction pour dessiner des formes avec transformation
    # def draw_transformed_rect(self, window, color, rect, zoom_factor, offset_x, offset_y, width=0):
    #     x, y, w, h = rect
    #     transformed_x, transformed_y = self.transform_shape(x, y, zoom_factor, offset_x, offset_y)
    #     transformed_w = w * zoom_factor
    #     transformed_h = h * zoom_factor
    #     pygame.draw.rect(window, color, pygame.Rect(transformed_x, transformed_y, transformed_w, transformed_h), width)

    # def draw_transformed_circle(self, window, color, pos, radius, zoom_factor, offset_x, offset_y, width=0):
    #     x, y = pos
    #     transformed_x, transformed_y = self.transform_shape(x, y, zoom_factor, offset_x, offset_y)
    #     transformed_radius = radius * zoom_factor
    #     pygame.draw.circle(window, color, (int(transformed_x), int(transformed_y)), int(transformed_radius), width)

    # # Fonction pour dessiner la scène
    # def draw_scene_old(self, color, window, zoom_factor, offset_x, offset_y):
    #     window.fill((0, 0, 0))
        
    #     # Exemple d'éléments à dessiner
    #     self.draw_transformed_rect(window, color, (100, 100, 100, 50), zoom_factor, offset_x, offset_y)
    #     self.draw_transformed_circle(window, color, (400, 300), 50, zoom_factor, offset_x, offset_y)
    #     self.draw_transformed_line(window, color, (200, 200), (300, 400), zoom_factor, offset_x, offset_y, width=3)

    # # Fonction pour dessiner une image avec transformation
    # def draw_transformed_image(self, window, image, pos, zoom_factor, offset_x, offset_y):
    #     x, y = pos
    #     transformed_x, transformed_y = self.transform_shape(x, y, zoom_factor, offset_x, offset_y)
        
    #     # Redimensionner l'image en fonction du facteur de zoom
    #     new_width = int(image.get_width() * zoom_factor)
    #     new_height = int(image.get_height() * zoom_factor)
    #     resized_image = pygame.transform.scale(image, (new_width, new_height))
        
    #     window.blit(resized_image, (transformed_x, transformed_y))

    # # Fonction pour dessiner la scène
    # def draw_scene(self, window, image, positions, zoom_factor, offset_x, offset_y):
    #     window.fill((0, 0, 0))
        
    #     # Dessiner les éléments avec transformation
    #     self.draw_transformed_image(window, image, positions, zoom_factor, offset_x, offset_y)

################################################################"

# import math
# import pygame
# import sys


# class Camera:

#     def __init__(self):
#         self.zoom_factor = 1.0
#         self.offset_x = 0
#         self.offset_y = 0

#     def transform_shape(self, x, y, zoom_factor, offset_x, offset_y):
#         return x * zoom_factor + offset_x, y * zoom_factor + offset_y

#     def handle_zoom(self, mouse_pos, zoom_in=True):
#         zoom_scale = 1.1  # Facteur de zoom, 10% à chaque coup de molette
        
#         # Récupérer la position de la souris avant le zoom
#         mouse_x, mouse_y = mouse_pos
#         world_x_before_zoom = (mouse_x - self.offset_x) / self.zoom_factor
#         world_y_before_zoom = (mouse_y - self.offset_y) / self.zoom_factor

#         # Appliquer le zoom
#         if zoom_in:
#             self.zoom_factor *= zoom_scale
#         else:
#             self.zoom_factor /= zoom_scale

#         # Récupérer la position de la souris après le zoom
#         world_x_after_zoom = (mouse_x - self.offset_x) / self.zoom_factor
#         world_y_after_zoom = (mouse_y - self.offset_y) / self.zoom_factor

#         # Ajuster l'offset pour recentrer le zoom autour de la souris
#         self.offset_x += (world_x_before_zoom - world_x_after_zoom) * self.zoom_factor
#         self.offset_y += (world_y_before_zoom - world_y_after_zoom) * self.zoom_factor

#     def handle_mouse_wheel(self, event):
#         # Si la molette de la souris est tournée
#         if event.type == pygame.MOUSEWHEEL:
#             mouse_pos = pygame.mouse.get_pos()
#             if event.y > 0:  # Molette vers le haut = zoom avant
#                 self.handle_zoom(mouse_pos, zoom_in=True)
#             elif event.y < 0:  # Molette vers le bas = zoom arrière
#                 self.handle_zoom(mouse_pos, zoom_in=False)

#     def draw_transformed_image(self, window, image, pos, zoom_factor, offset_x, offset_y):
#         x, y = pos
#         transformed_x, transformed_y = self.transform_shape(x, y, zoom_factor, offset_x, offset_y)

#         # Redimensionner et dessiner l'image transformée
#         new_width = int(image.get_width() * zoom_factor)
#         new_height = int(image.get_height() * zoom_factor)
#         resized_image = pygame.transform.scale(image, (new_width, new_height))
#         window.blit(resized_image, (transformed_x, transformed_y))
