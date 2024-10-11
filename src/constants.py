from pathlib import Path


GAME_TITLE = 'Evolution 2'

BASE_PATH = Path(__file__).parent.parent
IMAGES_PATH = BASE_PATH / 'static' / 'assets' / 'images' 

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

FPS = 60

CELL_MIN_SIZE = 7 # pixel, radius
CELL_MAX_SIZE = 20 # pixel, radius

CELL_MIN_MASS = 1
CELL_MAX_MASS = 10

CELL_COLLISION_TYPE = 1
FOOD_COLLISION_TYPE = 2

CELL_MAX_ENERGY = 100
CELL_MAX_LIFE_POINTS = 100

REPRODUCTION_DELAY = 6
MAX_FOODS = 100