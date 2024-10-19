from pathlib import Path
import math

import sys
import os

# Pour créer un exécutable avec pyinstaller
if getattr(sys, 'frozen', False):
    # commande to get the .exe (do it in Evolution/src folder)
    #pyinstaller --onefile --add-data "../static/assets/images;static/assets/images" main.py
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Pendant le développement
BASE_PATH = Path(BASE_PATH)
# BASE_PATH = Path(__file__).parent.parent # En mode normale quand y a pas bsoin de ce qu'il y a haut dessus

GAME_TITLE = 'Evolution 2'

IMAGES_PATH = BASE_PATH / 'static' / 'assets' / 'images' 

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

WORLD_WIDTH = 1000*2
WORLD_HEIGHT = 600*2

FPS = 60

CELL_MIN_SIZE = 7 # pixel, radius
CELL_MAX_SIZE = 20 # pixel, radius

CELL_MIN_MASS = 1
CELL_MAX_MASS = 10

CELL_COLLISION_TYPE = 1
FOOD_COLLISION_TYPE = 2

CELL_MAX_ENERGY = 100
ENERGY_LOSS_OVERTIME = 3
CELL_MAX_LIFE_POINTS = 100

REPRODUCTION_DELAY = 5
MAX_FOODS = 500
FOOD_SPAWN_AMOUNT = 30

WALL_COLOR = (110, 86, 10)

VISION_DISTANCE = 150
VISION_ANGLE = math.pi / 2
MOUTH_ANGLE = math.radians(30)
