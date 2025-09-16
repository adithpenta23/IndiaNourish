import pandas as pd
import numpy as np
import random
from typing import Dict, List, Tuple, Optional

class MealPlanner:
    """Generates personalized Indian meal plans based on user preference."""
    
    def __init__(self, foods_csv_path: str = 'foods.csv'):
        self.foods_df = pd.read_csv(foods_csv_path)
        self.meal_structure = {
            'breakfast': {'calories_pct': 0.25, 'foods_count': 2},
            'morning_snack': {'calories_pct': 0.10, 'foods_count': 1},
            'lunch': {'calories_pct': 0.35, 'foods_count': 3},
            'evening_snack': {'calories_pct': 0.10, 'foods_count': 1},
            'dinner': {'calories_pct': 0.20, 'foods_count': 2}
        }
    
    def filter_foods(self, dietary_preference: str, region: str) -> pd.DataFrame:
        """
        Filter foods based on dietary preferences and regional cuisine.
        
        Args:
            dietary_preference: 'Vegetarian', 'Non-Vegetarian', or 'Vegan'
            region: 'North Indian', 'South Indian', 'All Regions'
            
        Returns:
            Filtered DataFrame
        """
        filtered_df: pd.DataFrame = self.foods_df.copy()
        
        # Filter by dietary preference
        if dietary_preference == 'Vegetarian':
            filtered_df = filtered_df.loc[filtered_df['vegetarian'] == True].copy()
        elif dietary_preference == 'Vegan':
            filtered_df = filtered_df.loc[filtered_df['vegan'] == True].copy()
        # Non-vegetarian includes all foods
        
        # Filter by region
        if region != 'All Regions':
            region_key = region.split()[0].lower()  # 'North' or 'South'
            filtered_df = filtered_df.loc[
                (filtered_df['region'] == region_key.capitalize()) | 
                (filtered_df['region'] == 'All')
            ].copy()
        
        return filtered_df
    
    def select_foods_for_meal(self, available_foods: pd.DataFrame, 
                            target_calories: int, foods_count: int,
                            meal_type: str) -> List[Dict]:
        """
        Select foods for a specific meal to meet calorie target.
        
        Args:
            available_foods: Filtered foods DataFrame
            target_calories: Target calories for this meal
            foods_count: Number of food items to select
            meal_type: Type of meal (breakfast, lunch, etc.)
            
        Returns:
            List of selected foods with serving sizes
        """
        selected_foods = []
        remaining_calories = target_calories
        
        # Define meal-appropriate food categories
        meal_categories = {
            'breakfast': ['Grains', 'South Indian', 'Dairy', 'Fruits', 'Beverages'],
            'morning_snack': ['Fruits', 'Nuts', 'Snacks', 'Beverages'],
            'lunch': ['Grains', 'Lentils', 'Vegetables', 'Dairy', 'Non-Veg'],
            'evening_snack': ['Snacks', 'Fruits', 'Nuts', 'Beverages'],
            'dinner': ['Grains', 'Lentils', 'Vegetables', 'South Indian', 'Non-Veg']
        }
        
        appropriate_categories = meal_categories.get(meal_type, available_foods['category'].dropna().astype(str).unique().tolist())
        meal_foods: pd.DataFrame = available_foods.loc[available_foods['category'].isin(appropriate_categories)].copy()
        
        if meal_foods.empty:
            meal_foods = available_foods.copy()
        
        for i in range(foods_count):
            if meal_foods.empty:
                break
                
            # Select random food from appropriate categories
            food_row = meal_foods.sample(n=1).iloc[0]
            
            # Calculate serving size to contribute to remaining calories
            calories_per_100g = food_row['calories_per_100g']
            if calories_per_100g == 0:
                serving_size = 100  # Default serving
            else:
                # Aim for equal distribution of remaining calories
                target_food_calories = remaining_calories / (foods_count - i)
                serving_size = max(25, min(200, (target_food_calories / calories_per_100g) * 100))
            
            # Calculate actual nutritional values for this serving
            actual_calories = (calories_per_100g * serving_size) / 100
            actual_protein = (food_row['protein_g'] * serving_size) / 100
            actual_carbs = (food_row['carbs_g'] * serving_size) / 100
            actual_fat = (food_row['fat_g'] * serving_size) / 100
            actual_fiber = (food_row['fiber_g'] * serving_size) / 100
            
            selected_foods.append({
                'name': food_row['name'],
                'category': food_row['category'],
                'serving_size': round(serving_size, 0),
                'calories': round(actual_calories, 1),
                'protein': round(actual_protein, 1),
                'carbs': round(actual_carbs, 1),
                'fat': round(actual_fat, 1),
                'fiber': round(actual_fiber, 1)
            })
            
            remaining_calories -= actual_calories
            
            # Remove selected food to avoid repetition
            meal_foods = meal_foods[meal_foods['name'] != food_row['name']]
        
        return selected_foods
    
    def generate_meal_plan(self, target_nutrition: Dict, dietary_preference: str, 
                          region: str, variation: int = 1) -> Dict:
        """
        Generate a complete meal plan for one day.
        
        Args:
            target_nutrition: Target calories and macros
            dietary_preference: Vegetarian/Non-Vegetarian/Vegan
            region: Regional preference
            variation: Variation number for randomization
            
        Returns:
            Complete meal plan dictionary
        """
        # Set random seed for variation
        random.seed(variation * 42)
        np.random.seed(variation * 42)
        
        # Filter foods based on preferences
        available_foods = self.filter_foods(dietary_preference, region)
        
        if available_foods.empty:
            raise ValueError("No foods available for the selected preferences")
        
        meal_plan = {}
        total_nutrition = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
        
        target_calories = target_nutrition['calories']
        
        # Generate each meal
        for meal_type, meal_config in self.meal_structure.items():
            meal_calories = int(target_calories * meal_config['calories_pct'])
            foods_count = meal_config['foods_count']
            
            selected_foods = self.select_foods_for_meal(
                available_foods, meal_calories, foods_count, meal_type
            )
            
            # Calculate meal totals
            meal_totals = {
                'calories': sum(food['calories'] for food in selected_foods),
                'protein': sum(food['protein'] for food in selected_foods),
                'carbs': sum(food['carbs'] for food in selected_foods),
                'fat': sum(food['fat'] for food in selected_foods),
                'fiber': sum(food['fiber'] for food in selected_foods)
            }
            
            # Update total nutrition
            for nutrient in total_nutrition:
                total_nutrition[nutrient] += meal_totals[nutrient]
            
            meal_plan[meal_type] = {
                'foods': selected_foods,
                'totals': meal_totals
            }
        
        # Round total nutrition values
        for nutrient in total_nutrition:
            total_nutrition[nutrient] = round(total_nutrition[nutrient], 1)
        
        return {
            'meals': meal_plan,
            'daily_totals': total_nutrition,
            'target_nutrition': target_nutrition
        }
    
    def get_multiple_variations(self, target_nutrition: Dict, dietary_preference: str,
                              region: str, num_variations: int = 3) -> List[Dict]:
        """
        Generate multiple meal plan variations.
        
        Args:
            target_nutrition: Target nutrition values
            dietary_preference: Dietary preference
            region: Regional preference
            num_variations: Number of variations to generate
            
        Returns:
            List of meal plan variations
        """
        variations = []
        
        for i in range(1, num_variations + 1):
            try:
                meal_plan = self.generate_meal_plan(
                    target_nutrition, dietary_preference, region, variation=i
                )
                variations.append({
                    'variation_number': i,
                    'meal_plan': meal_plan
                })
            except Exception as e:
                print(f"Error generating variation {i}: {str(e)}")
                continue
        
        return variations
