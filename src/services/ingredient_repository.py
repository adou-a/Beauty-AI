from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_PATH = BASE_DIR/'data'/'ingredients.json'

with open(DATA_PATH,'r',encoding='utf-8')as file:
    ingredients = json.load(file)
    print(ingredients)