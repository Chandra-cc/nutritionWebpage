import os
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = "supersecretkey"

CSV_FILE = "combined_food_nutrition_dataset.csv"

# Load processed dataset
def load_dataset():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    else:
        print("Error: Processed dataset not found.")
        exit(1)

df = load_dataset()

# Get all matching food items
def get_nutrition_info(food_name):
    food_name = food_name.strip().lower()  # Clean up the input food name
    # Search for the food name in the 'Food' column using case-insensitive partial matching
    food_entries = df[df['Food'].str.lower().str.contains(food_name, na=False)]

    if food_entries.empty:
        return {"error": f"No nutrition data found for '{food_name}'."}
    
    # Extract the nutrition data for all matches
    columns_to_display = [
        'Food', 'Serving', 'Calories', 'Protein', 'Carbohydrates', 'Fat', 'Fiber', 
        'Sodium', 'Potassium', 'Sugar', 'Vitamin A', 'Vitamin C', 'Calcium', 'Iron'
    ]
    results = []
    for _, food_entry in food_entries.iterrows():
        nutrition = {col: food_entry[col] for col in columns_to_display if col in df.columns}
        results.append(nutrition)
    
    return {"results": results}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    food_query = request.form.get('food_query')
    
    if not food_query:
        return render_template('results.html', result={"error": "Please enter a valid food name."})

    result = get_nutrition_info(food_query)
    
    return render_template('results.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
