import math
import pygame
import sys


class Camera:

    def __init__(self) -> None:
        pass

    # Fonction de transformation générique
    def transform_shape(self, x, y, zoom_factor, offset_x, offset_y):
        return x * zoom_factor + offset_x, y * zoom_factor + offset_y

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

    # def draw_transformed_line(self, window, color, start_pos, end_pos, zoom_factor, offset_x, offset_y, width=1):
    #     x1, y1 = self.transform_shape(start_pos[0], start_pos[1], zoom_factor, offset_x, offset_y)
    #     x2, y2 = self.transform_shape(end_pos[0], end_pos[1], zoom_factor, offset_x, offset_y)
    #     pygame.draw.line(window, color, (x1, y1), (x2, y2), width)

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

    def draw_transformed_image(self, window, image, pos, angle, energy, zoom_factor, offset_x, offset_y):
        x, y = pos
        transformed_x, transformed_y = self.transform_shape(x, y, zoom_factor, offset_x, offset_y)
        
        # Redimensionner l'image en fonction du facteur de zoom
        new_width = int(image.get_width() * zoom_factor)
        new_height = int(image.get_height() * zoom_factor)
        resized_image = pygame.transform.scale(image, (new_width, new_height))

        # Appliquer la rotation à l'image
        rotated_image = pygame.transform.rotate(resized_image, -math.degrees(angle))
        
        # Calculer l'alpha en fonction de l'énergie
        alpha_min_threshold = 90 # sur 255
        if energy > 100 / 4:
            alpha = int(((energy - (100 / 4)) / (100 - (100 / 4))) * (255 - alpha_min_threshold) + alpha_min_threshold)
        else:
            alpha = alpha_min_threshold
        rotated_image.set_alpha(alpha)

        # Obtenir le rectangle de l'image après rotation pour centrer l'image sur la position
        image_rect = rotated_image.get_rect(center=(transformed_x, transformed_y))

        # Dessiner l'image transformée dans la fenêtre
        window.blit(rotated_image, image_rect.topleft)

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
