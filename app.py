import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import tempfile
import os
from nutrition_calculator import NutritionCalculator
from meal_planner import MealPlanner  
from pdf_generator import PDFGenerator

# Configure page
st.set_page_config(
    page_title="Indian Nutrition Planner",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def load_components():
    calculator = NutritionCalculator()
    planner = MealPlanner()
    pdf_gen = PDFGenerator()
    return calculator, planner, pdf_gen

calculator, planner, pdf_gen = load_components()

# App Header-1
st.title("🍽️ Indian Nutrition Planner")
st.markdown("---")
st.markdown("**Generate personalized meal plans using traditional Indian foods**")

# Sidebar for user inputs
st.sidebar.header("👤 Personal Information")

# User inputs
age = st.sidebar.number_input("Age (years)", min_value=15, max_value=100, value=30)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
weight = st.sidebar.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
height = st.sidebar.number_input("Height (cm)", min_value=120.0, max_value=220.0, value=170.0, step=0.5)

activity_level = st.sidebar.selectbox(
    "Activity Level",
    [
        "Sedentary (little or no exercise)",
        "Lightly active (light exercise 1-3 days/week)",
        "Moderately active (moderate exercise 3-5 days/week)",
        "Very active (hard exercise 6-7 days a week)",
        "Extra active (very hard exercise & physical job)"
    ],
    index=2
)

goal = st.sidebar.selectbox("Goal", ["Weight Loss", "Maintenance", "Muscle Gain"], index=1)

st.sidebar.header("🥗 Food Preferences")

dietary_preference = st.sidebar.selectbox(
    "Dietary Preference",
    ["Vegetarian", "Non-Vegetarian", "Vegan"]
)

region = st.sidebar.selectbox(
    "Regional Preference", 
    ["All Regions", "North Indian", "South Indian"]
)

# Generate meal plan button
generate_plan = st.sidebar.button("🔄 Generate Meal Plan", type="primary")

# Main content area
if generate_plan or 'meal_plan' in st.session_state:
    if generate_plan:
        # Calculate nutrition requirements
        daily_calories = calculator.calculate_daily_calories(
            weight, height, age, gender, activity_level, goal
        )
        target_nutrition = calculator.calculate_macros(daily_calories)
        bmi, bmi_category = calculator.get_bmi(weight, height)
        
        # Store user info and nutrition data
        st.session_state.user_info = {
            'age': age, 'gender': gender, 'weight': weight, 'height': height,
            'activity_level': activity_level, 'goal': goal,
            'dietary_preference': dietary_preference, 'region': region,
            'bmi': bmi, 'bmi_category': bmi_category
        }
        st.session_state.target_nutrition = target_nutrition
        
        # Generate meal plan
        try:
            meal_plan = planner.generate_meal_plan(
                target_nutrition, dietary_preference, region
            )
            st.session_state.meal_plan = meal_plan
        except Exception as e:
            st.error(f"Error generating meal plan: {str(e)}")
            st.stop()
    
    # Display results
    user_info = st.session_state.user_info
    target_nutrition = st.session_state.target_nutrition
    meal_plan = st.session_state.meal_plan
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📊 Your Nutrition Summary")
        
        # Display user stats
        st.subheader("Personal Stats")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.metric("BMI", f"{user_info['bmi']}")
            st.caption(user_info['bmi_category'])
        
        with stats_col2:
            st.metric("Daily Calories", f"{target_nutrition['calories']}")
        
        with stats_col3:
            st.metric("Protein Target", f"{target_nutrition['protein']}g")
        
        with stats_col4:
            st.metric("Goal", user_info['goal'])
        
        st.markdown("---")
        
        # Nutrition comparison
        st.subheader("Target vs Actual Nutrition")
        
        comparison_data = {
            'Nutrient': ['Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)'],
            'Target': [
                target_nutrition['calories'],
                target_nutrition['protein'],
                target_nutrition['carbs'], 
                target_nutrition['fat']
            ],
            'Actual': [
                meal_plan['daily_totals']['calories'],
                meal_plan['daily_totals']['protein'],
                meal_plan['daily_totals']['carbs'],
                meal_plan['daily_totals']['fat']
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df['Difference'] = comparison_df['Actual'] - comparison_df['Target']
        
        st.dataframe(comparison_df, use_container_width=True)
    
    with col2:
        st.header("🥧 Macro Distribution")
        
        # Create pie chart
        daily_totals = meal_plan['daily_totals']
        
        # Calculate macro calories
        protein_cal = daily_totals['protein'] * 4
        carbs_cal = daily_totals['carbs'] * 4
        fat_cal = daily_totals['fat'] * 9
        
        total_macro_cal = protein_cal + carbs_cal + fat_cal
        
        if total_macro_cal > 0:
            # Calculate percentages
            protein_pct = (protein_cal / total_macro_cal) * 100
            carbs_pct = (carbs_cal / total_macro_cal) * 100
            fat_pct = (fat_cal / total_macro_cal) * 100
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            sizes = [protein_pct, carbs_pct, fat_pct]
            labels = [f'Protein\n{protein_pct:.1f}%', f'Carbs\n{carbs_pct:.1f}%', f'Fat\n{fat_pct:.1f}%']
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.set_title('Macro Distribution', fontsize=14, fontweight='bold')
            
            st.pyplot(fig)
        
        # Fiber info
        st.metric("Daily Fiber", f"{daily_totals['fiber']:.1f}g")
        st.caption("Recommended: 25-35g daily")
    
    st.markdown("---")
    
    # Detailed meal plan
    st.header("🍽️ Your Personalized Meal Plan")
    
    meal_names = {
        'breakfast': '🌅 Breakfast',
        'morning_snack': '☕ Morning Snack',
        'lunch': '🌞 Lunch',
        'evening_snack': '🍵 Evening Snack', 
        'dinner': '🌙 Dinner'
    }
    
    # Create tabs for each meal
    tab_names = [meal_names[meal_type] for meal_type in meal_plan['meals'].keys()]
    tabs = st.tabs(tab_names)
    
    for i, (meal_type, meal_data) in enumerate(meal_plan['meals'].items()):
        with tabs[i]:
            st.subheader(f"{meal_names[meal_type]} Details")
            
            # Food items
            for food in meal_data['foods']:
                with st.container():
                    food_col1, food_col2, food_col3 = st.columns([2, 1, 2])
                    
                    with food_col1:
                        st.write(f"**{food['name']}**")
                        st.write(f"Serving: {food['serving_size']:.0f}g")
                    
                    with food_col2:
                        st.metric("Calories", f"{food['calories']:.0f}")
                    
                    with food_col3:
                        st.write(f"Protein: {food['protein']:.1f}g")
                        st.write(f"Carbs: {food['carbs']:.1f}g | Fat: {food['fat']:.1f}g")
                    
                    st.markdown("---")
            
            # Meal totals
            totals = meal_data['totals']
            st.success(f"**Meal Total:** {totals['calories']:.0f} calories | "
                      f"{totals['protein']:.1f}g protein | "
                      f"{totals['carbs']:.1f}g carbs | "
                      f"{totals['fat']:.1f}g fat")
    
    st.markdown("---")
    
    # Action buttons
    st.header("📋 Actions")
    
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🔄 Generate New Variation"):
            # Generate new variation
            try:
                new_meal_plan = planner.generate_meal_plan(
                    target_nutrition, dietary_preference, region, 
                    variation=st.session_state.get('variation_count', 1) + 1
                )
                st.session_state.meal_plan = new_meal_plan
                st.session_state.variation_count = st.session_state.get('variation_count', 1) + 1
                st.rerun()
            except Exception as e:
                st.error(f"Error generating new variation: {str(e)}")
    
    with action_col2:
        if st.button("📊 Generate Multiple Variations"):
            try:
                variations = planner.get_multiple_variations(
                    target_nutrition, dietary_preference, region, num_variations=3
                )
                st.session_state.variations = variations
                st.success(f"Generated {len(variations)} variations!")
                
                # Display variations summary
                for var_data in variations:
                    var_num = var_data['variation_number']
                    var_plan = var_data['meal_plan']
                    var_totals = var_plan['daily_totals']
                    
                    st.write(f"**Variation {var_num}:** {var_totals['calories']:.0f} cal | "
                            f"{var_totals['protein']:.1f}g protein")
                            
            except Exception as e:
                st.error(f"Error generating variations: {str(e)}")
    
    with action_col3:
        if st.button("📄 Download PDF Report"):
            try:
                # Generate PDF
                with st.spinner("Generating PDF..."):
                    pdf_path = pdf_gen.generate_meal_plan_pdf(meal_plan, user_info)
                    
                    # Read PDF file
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()
                    
                    st.download_button(
                        label="📥 Download Meal Plan PDF",
                        data=pdf_data,
                        file_name="indian_nutrition_plan.pdf",
                        mime="application/pdf"
                    )
                    
                    # Clean up temporary file
                    os.unlink(pdf_path)
                    
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
    
    # Additional information
    st.markdown("---")
    st.header("ℹ️ Important Information")
    
    with st.expander("📝 Meal Plan Notes"):
        st.write("""
        **Important Guidelines:**
        - This meal plan is generated based on your inputs and general nutritional guidelines
        - Consult with a registered dietitian or healthcare provider before making significant dietary changes
        - Adjust portion sizes based on your hunger, satiety, and energy levels
        - Stay hydrated throughout the day with adequate water intake
        - Include physical activity as recommended by health guidelines
        
        **Food Preparation Tips:**
        - Use minimal oil for cooking to control fat intake
        - Include a variety of colorful vegetables for better nutrition
        - Choose whole grains over refined grains when possible
        - Practice portion control and mindful eating
        """)
    
    with st.expander("🔬 Nutritional Information"):
        st.write(f"""
        **Your Calculated Values:**
        - **BMR (Basal Metabolic Rate):** {calculator.calculate_bmr(weight, height, age, gender):.0f} calories
        - **TDEE (Total Daily Energy Expenditure):** {calculator.calculate_tdee(calculator.calculate_bmr(weight, height, age, gender), activity_level):.0f} calories
        - **Adjusted for Goal:** {target_nutrition['calories']} calories
        
        **Macro Distribution:**
        - **Protein:** 25% of total calories ({target_nutrition['protein']}g)
        - **Carbohydrates:** 45% of total calories ({target_nutrition['carbs']}g)
        - **Fat:** 30% of total calories ({target_nutrition['fat']}g)
        """)

else:
    # Welcome screen
    st.header("🙏 Welcome to Indian Nutrition Planner")
    
    st.markdown("""
    ### Generate personalized meal plans using traditional Indian foods!
    
    **Features:**
    - 🔢 **Scientific Calculations:** BMR and TDEE using Mifflin-St Jeor equation
    - 🍛 **Indian Food Database:** 50+ traditional foods with complete nutritional information
    - 🎯 **Goal-Based Planning:** Weight loss, maintenance, or muscle gain
    - 🥗 **Dietary Preferences:** Vegetarian, Non-Vegetarian, and Vegan options  
    - 🌍 **Regional Cuisines:** North Indian, South Indian, and All Regions
    - 📊 **Detailed Analytics:** Macro breakdown and nutritional analysis
    - 📄 **PDF Export:** Download your personalized meal plan
    - 🔄 **Multiple Variations:** Generate different meal plan options
    
    **How to Use:**
    1. Fill in your personal information in the sidebar
    2. Select your dietary and regional preferences
    3. Click "Generate Meal Plan" to get your personalized nutrition plan
    4. Explore different variations and download your meal plan as PDF
    
    **Food Categories Included:**
    - **Grains:** Rice, Roti, Dosa, Idli
    - **Lentils:** Dal varieties, Rajma, Chole
    - **Vegetables:** Seasonal Indian vegetables and preparations  
    - **Dairy:** Paneer, Dahi, Lassi
    - **Non-Vegetarian:** Chicken, Mutton, Fish, Egg curries
    - **Snacks & Fruits:** Traditional Indian snacks and seasonal fruits
    
    👈 **Start by entering your information in the sidebar!**
    """)
    
    # Sample nutrition facts
    st.markdown("---")
    st.subheader("🍲 Sample Indian Foods in Database")
    
    # Display sample foods
    sample_foods = [
        {"Food": "Basmati Rice (100g)", "Calories": 345, "Protein": "7.1g", "Carbs": "78.2g"},
        {"Food": "Dal Tadka (100g)", "Calories": 108, "Protein": "7.6g", "Carbs": "16.3g"},
        {"Food": "Paneer (100g)", "Calories": 265, "Protein": "18.3g", "Carbs": "1.2g"},
        {"Food": "Chicken Curry (100g)", "Calories": 165, "Protein": "25.0g", "Carbs": "2.5g"},
        {"Food": "Plain Dosa (100g)", "Calories": 86, "Protein": "1.6g", "Carbs": "17.8g"}
    ]
    
    sample_df = pd.DataFrame(sample_foods)
    st.dataframe(sample_df, use_container_width=True)
