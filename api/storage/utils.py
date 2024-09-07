# Simulated backend database stored in a JSON file
import json

DATABASE_FILE = "database.json"

def read_items():
    with open(DATABASE_FILE, "r") as file:
        items = json.load(file)
    return items

def write_items(items):
    with open(DATABASE_FILE, "w") as file:
        json.dump(items, file)