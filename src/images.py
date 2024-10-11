from pathlib import Path
import pygame

from constants import *


class Images:
    
    def __init__(self) -> None:
        self.cell_image = pygame.image.load(IMAGES_PATH / 'cell.png')
        self.cell_image = pygame.transform.rotate(self.cell_image, 180)
        self.cell_image_lvl1_damaged = pygame.image.load(IMAGES_PATH / 'cell_lvl1_damaged.png')
        self.cell_image_lvl1_damaged = pygame.transform.rotate(self.cell_image_lvl1_damaged, 180)
        self.cell_image_lvl2_damaged = pygame.image.load(IMAGES_PATH / 'cell_lvl2_damaged.png')
        self.cell_image_lvl2_damaged = pygame.transform.rotate(self.cell_image_lvl2_damaged, 180)
        self.cell_images = [self.cell_image, self.cell_image_lvl1_damaged, self.cell_image_lvl2_damaged]
        self.user_cell_image = pygame.image.load(IMAGES_PATH / 'cell_user.png')
        self.user_cell_image = pygame.transform.rotate(self.user_cell_image, 180)
        self.user_cell_image_lvl1_damaged = pygame.image.load(IMAGES_PATH / 'cell_user_lvl1_damaged.png')
        self.user_cell_image_lvl1_damaged = pygame.transform.rotate(self.user_cell_image_lvl1_damaged, 180)
        self.user_cell_image_lvl2_damaged = pygame.image.load(IMAGES_PATH / 'cell_user_lvl2_damaged.png')
        self.user_cell_image_lvl2_damaged = pygame.transform.rotate(self.user_cell_image_lvl2_damaged, 180)
        self.user_cell_images = [self.user_cell_image, self.user_cell_image_lvl1_damaged, self.user_cell_image_lvl2_damaged]
        self.food_image = pygame.image.load(IMAGES_PATH / 'food.png')
        # self.food_image = self.load_image_with_red_tint(IMAGES_PATH / 'food.png', 0.1)
        

    ## Met un film rouge, mais pas opti car parcourt chaque pixel
    # def load_image_with_red_tint(self, image_path, red_factor):
    #     # red_factor : 0 = pas de rouge, 1 = rouge complet 
    #     # Charger l'image
    #     image = pygame.image.load(image_path).convert_alpha()

    #     # Créer une copie de l'image pour éviter de modifier l'original
    #     tinted_image = image.copy()

    #     # Obtenir les dimensions de l'image
    #     width, height = tinted_image.get_size()

    #     # Accéder aux pixels de l'image
    #     for x in range(width):
    #         for y in range(height):
    #             # Obtenir la couleur du pixel
    #             r, g, b, a = tinted_image.get_at((x, y))

    #             # Appliquer la teinte rouge en fonction du red_factor
    #             r = min(255, r + int(255 * red_factor))  # Augmenter le rouge
    #             # Laisser le vert et le bleu inchangés
    #             tinted_image.set_at((x, y), (r, g, b, a))

    #     return tinted_image

    ## Met un film rouge, mais askip y a un carré noir autour, a vérifié
    # def load_image_with_red_tint(self, image_path, red_factor):
    #     # red_factor : 0 = pas de rouge, 1 = rouge complet 
    #     # Charger l'image
    #     image = pygame.image.load(image_path).convert_alpha()

    #     # Convertir l'image en tableau NumPy
    #     image_array = pygame.surfarray.array3d(image)

    #     # Appliquer la teinte rouge
    #     # Multiplier le canal rouge par le facteur, s'assurer de ne pas dépasser 255
    #     image_array[..., 0] = np.clip(image_array[..., 0] + int(255 * red_factor), 0, 255)

    #     # Convertir le tableau NumPy de retour en surface Pygame
    #     tinted_image = pygame.surfarray.make_surface(image_array)

    #     return tinted_image
