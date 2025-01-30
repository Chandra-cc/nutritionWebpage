import os
import pandas as pd
from flask import Flask, render_template, request
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSV_FILE = "combined_food_nutrition_dataset.csv"

# Load the dataset
def load_dataset():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        print("Error: Processed dataset not found.")
        exit(1)

df = load_dataset()

# Pre-process the food names to strip spaces and convert to lowercase
df['Food'] = df['Food'].str.strip().str.lower()

# Fuzzy string matching function to find the most similar food item
def get_closest_food_name(food_query):
    food_query = food_query.strip().lower()  # Strip spaces and make the query lowercase
    food_list = df['Food'].tolist()  # List of food items in the dataset
    
    # Perform fuzzy matching on the food name
    closest_match = process.extractOne(food_query, food_list, scorer=fuzz.token_sort_ratio)
    return closest_match

# Get nutrition info based on the matched food name

def get_nutrition_info(food_name):
    # Use fuzzy matching to find the best matches in the dataset
    food_list = df['Food'].tolist()
    matched_foods = process.extract(food_name, food_list, limit=5)  # Get top 5 matches

    # If no matches are found, return an error
    if not matched_foods:
        return {"error": f"No matching food item found for '{food_name}'."}

    results = []
    for match in matched_foods:
        food_name_matched = match[0]
        similarity_score = match[1]

        # Only consider matches with a score of 80 or above (this is adjustable)
        if similarity_score < 80:
            continue
        
        food_entry = df[df['Food'] == food_name_matched]
        
        if not food_entry.empty:
            food_entry = food_entry.iloc[0]
            # List of expected columns
            expected_columns = ['Food', 'Serving', 'Calories', 'Protein', 'Carbohydrates', 'Fat', 'Fiber', 'Sodium', 'Potassium', 'Sugar', 'Vitamin A', 'Vitamin C', 'Calcium', 'Iron']
            
            # Use a dictionary comprehension to get only the columns that exist in the dataframe
            nutrition_info = {col: food_entry.get(col, 'N/A') for col in expected_columns}
            
            results.append({
                "food": food_name_matched,
                "similarity_score": similarity_score,
                "nutrition": nutrition_info
            })

    if not results:
        return {"error": f"No sufficiently similar food items found for '{food_name}'."}

    return {
        "food": food_name,
        "results": results
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    food_query = request.form.get('food_query')
    if not food_query:
        return render_template('results_v2.html', result={"error": "Please enter a valid food name."})

    result = get_nutrition_info(food_query)

    return render_template('results_v2.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
