import os
from fastapi import APIRouter
import requests
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
from models.models import InventoryItemMacros

# load .env file
load_dotenv()

# Load your USDA API Key
USDA_API_KEY = os.getenv('USDA_API_KEY')


# Define a function to search for food items using the USDA FoodData Central API
def search_food_item(item_name: str) -> Optional[int]:
    """
    Search for food items using the USDA FoodData Central API.
    Returns the fdcId of the first result, or None if no result is found.
    """
    search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={USDA_API_KEY}"
    params = {
        'query': item_name,
        "startDate": "2021-01-01",
        "endDate": "2021-12-30"
    }
    response = requests.get(search_url, params=params)
    
    if response.status_code == 200:
        search_data = response.json()
        if search_data['foods']:
            # Return the first food's FDC ID
            return search_data['foods'][0]['fdcId']
    return None

def fetch_food_details(fdc_id: int, format: str = 'full', nutrients: Optional[List[int]] = None) -> Optional[InventoryItemMacros]:
    """
    Fetch detailed food nutrient information using the FDC ID.
    Supports optional format (abridged/full) and nutrient filtering.
    """
    detail_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {
        'api_key': USDA_API_KEY,
        'format': format
    }
    if nutrients:
        params['nutrients'] = ','.join(map(str, nutrients))
    
    response = requests.get(detail_url, params=params)
    print(response)
    if response.status_code == 200:
        food_data = response.json()
        nutrients = {nutrient['nutrient']['name']: nutrient['amount'] for nutrient in food_data.get('foodNutrients', [])}
        
        # Map USDA nutrient data to your InventoryItemMacros model
        return InventoryItemMacros(
            protein=nutrients.get('Protein', 0),
            carbohydrates=nutrients.get('Carbohydrate, by difference', 0),
            fiber=nutrients.get('Fiber, total dietary', 0),
            sugar=nutrients.get('Sugars, total including NLEA', 0),
            fat=nutrients.get('Total lipid (fat)', 0),
            saturated_fat=nutrients.get('Fatty acids, total saturated', 0),
            polyunsaturated_fat=nutrients.get('Fatty acids, total polyunsaturated', 0),
            monounsaturated_fat=nutrients.get('Fatty acids, total monounsaturated', 0),
            trans_fat=nutrients.get('Fatty acids, total trans', 0),
            cholesterol=nutrients.get('Cholesterol', 0),
            sodium=nutrients.get('Sodium, Na', 0),
            potassium=nutrients.get('Potassium, K', 0),
            vitamin_a=nutrients.get('Vitamin A, RAE', 0),
            vitamin_c=nutrients.get('Vitamin C, total ascorbic acid', 0),
            calcium=nutrients.get('Calcium, Ca', 0),
            iron=nutrients.get('Iron, Fe', 0)
        )
    
    return None

def query_food_api(item_name: str) -> Optional[InventoryItemMacros]:
    """
    Query the USDA FoodData Central API to retrieve macro information for a given food item.
    First searches for the item, then fetches detailed nutrient information using the fdcId.
    Portion size is in grams by default.
    """
    fdc_id = search_food_item(item_name)
    
    if fdc_id:
        return fetch_food_details(fdc_id)
    
    return None

macro_router = APIRouter(prefix="/macros")

@macro_router.get("/item")
def get_item_macros(item_name: str):
    """
    Endpoint to get the macro information for a given food item.
    """
    macro_data = query_food_api(item_name)
    print(macro_data)
    if macro_data:
        return macro_data
    else:
        return {"error": "Item not found or data unavailable"}
