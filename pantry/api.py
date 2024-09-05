from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import json
from models import InventoryItem

app = FastAPI()

# Simulated backend database stored in a JSON file
DATABASE_FILE = "database.json"

def read_items():
    with open(DATABASE_FILE, "r") as file:
        items = json.load(file)
    return items

def write_items(items):
    with open(DATABASE_FILE, "w") as file:
        json.dump(items, file)

@app.get("/items", response_model=List[InventoryItem])
def get_items():
    items = read_items()
    return items

@app.get("/items/{item_id}", response_model=InventoryItem)
def get_item(item_id: str):
    items = read_items()
    for item in items:
        if item["id"] == item_id:
            return item
    return {"error": "Item not found"}

@app.post("/items", response_model=InventoryItem)
def create_item(item: InventoryItem):
    items = read_items()
    item_dict = item.dict()
    items.append(item_dict)
    write_items(items)
    return item

@app.put("/items/{item_id}", response_model=InventoryItem)
def update_item(item_id: str, item: InventoryItem):
    items = read_items()
    for i, existing_item in enumerate(items):
        if existing_item["id"] == item_id:
            items[i] = item.dict()
            items[i]["id"] = item_id  # Ensure the ID remains the same
            write_items(items)
            return item
    return {"error": "Item not found"}

@app.delete("/items/{item_id}")
def delete_item(item_id: str):
    items = read_items()
    for i, item in enumerate(items):
        if item["id"] == item_id:
            del items[i]
            write_items(items)
            return {"message": "Item deleted"}
    return {"error": "Item not found"}