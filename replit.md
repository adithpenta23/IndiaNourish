# Overview

The Indian Nutrition Planner is a Streamlit-based web application that generates personalized meal plans using traditional Indian foods. The application calculates users' nutritional requirements based on their personal information (age, gender, weight, height, activity level) and creates customized meal plans that align with dietary preferences and regional cuisine choices. The system includes functionality for nutritional analysis, meal planning, and PDF report generation.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: Streamlit web framework for rapid prototyping and deployment
- **UI Structure**: Single-page application with sidebar navigation for user inputs
- **State Management**: Streamlit's built-in session state and caching mechanisms
- **Visualization**: Matplotlib integration for nutritional charts and graphs

## Backend Architecture
- **Modular Design**: Component-based architecture with separate modules for distinct functionalities
- **Core Components**:
  - `NutritionCalculator`: Handles BMR (Basal Metabolic Rate) and TDEE (Total Daily Energy Expenditure) calculations using Mifflin-St Jeor equation
  - `MealPlanner`: Manages meal selection algorithms and dietary filtering logic
  - `PDFGenerator`: Creates formatted PDF reports using ReportLab library
- **Data Processing**: Pandas-based data manipulation for food database and nutritional calculations

## Data Storage
- **Food Database**: CSV file (`foods.csv`) containing Indian food items with nutritional information
- **Data Structure**: Structured data includes calories, macronutrients, dietary classifications (vegetarian/vegan), and regional categorization
- **No Persistent Storage**: Application operates in stateless mode with session-based data handling

## Calculation Engine
- **BMR Calculation**: Gender-specific formulas for metabolic rate estimation
- **Activity Multipliers**: Predefined factors for different activity levels (sedentary to extra active)
- **Goal Adjustments**: Caloric modifications for weight loss, maintenance, or muscle gain objectives
- **Meal Distribution**: Percentage-based calorie allocation across five daily meals (breakfast, morning snack, lunch, evening snack, dinner)

## Filtering and Selection Logic
- **Dietary Preferences**: Multi-tier filtering for vegetarian, vegan, and non-vegetarian options
- **Regional Cuisine**: North Indian, South Indian, and combined regional food selection
- **Algorithmic Selection**: Random selection with nutritional constraint satisfaction for meal variety

# External Dependencies

## Python Libraries
- **Streamlit**: Web application framework for user interface and deployment
- **Pandas**: Data manipulation and analysis for food database operations
- **NumPy**: Numerical computing for mathematical calculations
- **Matplotlib**: Data visualization for nutritional charts and graphs
- **ReportLab**: PDF generation library for meal plan reports

## Data Dependencies
- **foods.csv**: External CSV file containing Indian food nutritional database
- **Temporary File System**: OS-level temporary file handling for PDF generation and downloads

## System Requirements
- **Python Runtime**: Compatible with standard Python package management
- **File System Access**: Required for CSV data loading and temporary file operations
- **Memory Management**: Streamlit caching for performance optimization of component initialization