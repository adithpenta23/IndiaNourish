import numpy as np
import pandas as pd
from typing import Dict, Tuple

class NutritionCalculator:
    """Handles BMR calculation and nutritional requirements."""
    
    def __init__(self):
        self.activity_multipliers = {
            'Sedentary (little or no exercise)': 1.2,
            'Lightly active (light exercise 1-3 days/week)': 1.375,
            'Moderately active (moderate exercise 3-5 days/week)': 1.55,
            'Very active (hard exercise 6-7 days a week)': 1.725,
            'Extra active (very hard exercise & physical job)': 1.9
        }
        
        self.goal_adjustments = {
            'Weight Loss': -0.2,  # 20% deficits
            'Maintenance': 0.0,
            'Muscle Gain': 0.15   # 15% surplus
        }
    
    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.
        
        Args:
            weight: Weight in kg
            height: Height in cm
            age: Age in years
            gender: 'Male' or 'Female'
            
        Returns:
            BMR in calories
        """
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:  # female
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure.
        
        Args:
            bmr: Basal Metabolic Rate
            activity_level: Activity level string
            
        Returns:
            TDEE in calories
        """
        multiplier = self.activity_multipliers.get(activity_level, 1.2)
        return bmr * multiplier
    
    def calculate_daily_calories(self, weight: float, height: float, age: int, 
                               gender: str, activity_level: str, goal: str) -> int:
        """
        Calculate daily calorie requirements based on user inputs.
        
        Returns:
            Daily calorie requirement
        """
        bmr = self.calculate_bmr(weight, height, age, gender)
        tdee = self.calculate_tdee(bmr, activity_level)
        
        # Apply goal adjustment
        goal_adjustment = self.goal_adjustments.get(goal, 0.0)
        daily_calories = tdee * (1 + goal_adjustment)
        
        return int(daily_calories)
    
    def calculate_macros(self, daily_calories: int) -> Dict[str, int]:
        """
        Calculate macro distribution (protein, carbs, fat).
        Standard distribution: 25% protein, 45% carbs, 30% fat
        
        Args:
            daily_calories: Daily calorie requirement
            
        Returns:
            Dictionary with macro targets in grams
        """
        protein_calories = daily_calories * 0.25
        carb_calories = daily_calories * 0.45
        fat_calories = daily_calories * 0.30
        
        # Convert calories to grams (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
        protein_g = int(protein_calories / 4)
        carbs_g = int(carb_calories / 4)
        fat_g = int(fat_calories / 9)
        
        return {
            'calories': daily_calories,
            'protein': protein_g,
            'carbs': carbs_g,
            'fat': fat_g
        }
    
    def get_bmi(self, weight: float, height: float) -> Tuple[float, str]:
        """
        Calculate BMI and category.
        
        Args:
            weight: Weight in kg
            height: Height in cm
            
        Returns:
            BMI value and category string
        """
        height_m = height / 100  # convert cm to meters
        bmi = weight / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal weight"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
            
        return round(bmi, 1), category
