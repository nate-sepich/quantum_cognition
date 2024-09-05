from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import json

app = FastAPI()

class InventoryItemMacros(BaseModel):
    protein: Optional[float] = 0
    carbohydrates: Optional[float] = 0
    fiber: Optional[float] = 0
    sugar: Optional[float] = 0
    fat: Optional[float] = 0
    saturated_fat: Optional[float] = 0
    polyunsaturated_fat: Optional[float] = 0
    monounsaturated_fat: Optional[float] = 0
    trans_fat: Optional[float] = 0
    cholesterol: Optional[float] = 0
    sodium: Optional[float] = 0
    potassium: Optional[float] = 0
    vitamin_a: Optional[float] = 0
    vitamin_c: Optional[float] = 0
    calcium: Optional[float] = 0
    iron: Optional[float] = 0

# Simulated backend database stored in a JSON file
DATABASE_FILE = "database.json"

def read_items():
    with open(DATABASE_FILE, "r") as file:
        items = json.load(file)
    return items

def write_items(items):
    with open(DATABASE_FILE, "w") as file:
        json.dump(items, file)

@app.get("/items")
def get_items():
    items = read_items()
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    items = read_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}

@app.post("/items")
def create_item(item: InventoryItemMacros):
    items = read_items()
    items.append(item.dict())
    write_items(items)
    return item

@app.put("/items/{item_id}")
def update_item(item_id: int, item: InventoryItemMacros):
    items = read_items()
    for i, existing_item in enumerate(items):
        if existing_item["id"] == item_id:
            items[i] = item.dict()
            write_items(items)
            return item
    return {"error": "Item not found"}

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    items = read_items()
    for i, item in enumerate(items):
        if item["id"] == item_id:
            del items[i]
            write_items(items)
            return {"message": "Item deleted"}
    return {"error": "Item not found"}

