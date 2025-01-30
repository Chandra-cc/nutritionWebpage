import os
import json
import kaggle
import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApi
import re
# Specify the path to your kaggle.json file (adjust the path if necessary)
kaggle_json_path = 'kaggle.json'  # Adjust this path

# Load the Kaggle API key from the specified file
try:
    with open(kaggle_json_path, 'r') as f:
        kaggle_json = json.load(f)
        # Set the environment variables for Kaggle authentication
        os.environ['KAGGLE_USERNAME'] = kaggle_json['username']
        os.environ['KAGGLE_KEY'] = kaggle_json['key']
    print("Kaggle API credentials loaded successfully.")
except FileNotFoundError:
    print(f"Error: The file '{kaggle_json_path}' was not found.")
    exit(1)

# Authenticate using the environment variables
api = KaggleApi()
api.authenticate()

# Dataset download function
def download_datasets():
    # Dataset paths (from Kaggle)
    dataset_1 = "lakshaysharma07/diet-dataset-calorie"
    dataset_2 = "prajwaldongre/top-100-healthiest-food-in-the-world"
    dataset_3 = "ulrikthygepedersen/nutritional-food-facts"  # New dataset to be included

    # Download datasets from Kaggle
    print("Downloading 'Diet Dataset Calorie'...")
    api.dataset_download_files(dataset_1, path='datasets/', unzip=True)
    print(f"Downloaded {dataset_1}.")

    print("Downloading 'Top 100 Healthiest Food'...")
    api.dataset_download_files(dataset_2, path='datasets/', unzip=True)
    print(f"Downloaded {dataset_2}.")

    print("Downloading 'Nutritional Food Facts'...")
    api.dataset_download_files(dataset_3, path='datasets/', unzip=True)
    print(f"Downloaded {dataset_3}.")

# Function to load and process the downloaded datasets
def process_datasets():
    try:
        diet_df = pd.read_csv('datasets/Calorie_value.csv')
        healthiest_food_df = pd.read_csv('datasets/Top 100 Healthiest Food in the World.csv')
        nutritional_food_df = pd.read_csv('datasets/nutritionalfacts_fruit_vegetables_seafood.csv')
        string_to_add = " grams"

       
        # Standardize columns in diet dataset
        diet_df.rename(columns={'food items': 'Food', 'Avg Serving Size': 'Serving', 'Category': 'Food Category'}, inplace=True)

         # Update the 'Food' column by appending the string to the end of each value
        diet_df['Serving'] = diet_df['Serving'].apply(lambda x: str(x) + string_to_add)

        # Standardize columns in healthiest food dataset
        healthiest_food_df.rename(columns={
            'Food': 'Food',
            'Nutrition Value (per 100g)': 'Nutrition Value',
            'Quantity': 'Serving',
            'Originated From': 'Origin',
            'Calories': 'Calories',
            'Protein (g)': 'Protein',
            'Fiber (g)': 'Fiber',
            'Vitamin C (mg)': 'Vitamin C',
            'Antioxidant Score': 'Antioxidant Score'
        }, inplace=True)

        # Process nutritional food facts dataset
        nutritional_food_df.rename(columns={
            'food_and_serving': 'Food and Serving',
            'calories': 'Calories',
            'protein_g': 'Protein',
            'dietary_fiber_g': 'Fiber',
            'total_carbo_hydrate_g': 'Carbohydrates',
            'sodium_g': 'Sodium',
            'potassium_g': 'Potassium',
            'food_type': 'Food Category'
        }, inplace=True)

        # Extract food name, quantity, and unit
        # Extract food name (everything before the first comma)
        nutritional_food_df['Food'] = nutritional_food_df['Food and Serving'].apply(lambda x: re.split(r',', x, 1)[0].strip())

        # Extract serving size (everything after the first comma)
        nutritional_food_df['Serving'] = nutritional_food_df['Food and Serving'].apply(lambda x: re.split(r',', x, 1)[1].strip() if ',' in x else '')

        # Convert Quantity to numeric
        # nutritional_food_df['Serving'] = pd.to_numeric(nutritional_food_df['Quantity'], errors='coerce')

        # Drop unnecessary columns
        nutritional_food_df.drop(columns=['Food and Serving'], inplace=True)

        # Merge datasets
        combined_df = pd.concat([diet_df, healthiest_food_df, nutritional_food_df], ignore_index=True)
        combined_df.dropna(subset=['Food'], inplace=True)
        combined_df.to_csv('combined_food_nutrition_dataset.csv', index=False)
        print("Combined dataset saved as 'combined_food_nutrition_dataset.csv'.")
    except Exception as e:
        print(f"Error processing datasets: {e}")

# Run the functions
if __name__ == "__main__":
    download_datasets()  # Download the datasets
    process_datasets()   # Process and combine the datasets
