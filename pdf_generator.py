from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io
import base64
from typing import Dict, List, Optional
import tempfile
import os

class PDFGenerator:
    """Generates PDF reports for meal plan."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for the PDF."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.darkblue,
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='MealTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.darkgreen,
            spaceAfter=10,
            spaceBefore=15,
            leftIndent=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='FoodItem',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=40,
            spaceAfter=3
        ))
        
        self.styles.add(ParagraphStyle(
            name='NutritionSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.darkblue,
            spaceAfter=5,
            leftIndent=20
        ))
    
    def create_macro_chart(self, nutrition_data: Dict) -> str:
        """
        Create a pie chart for macro distribution.
        
        Args:
            nutrition_data: Dictionary with calories, protein, carbs, fat
            
        Returns:
            Base64 encoded image string
        """
        # Calculate macro calories
        protein_cal = nutrition_data['protein'] * 4
        carbs_cal = nutrition_data['carbs'] * 4  
        fat_cal = nutrition_data['fat'] * 9
        
        total_macro_cal = protein_cal + carbs_cal + fat_cal
        
        if total_macro_cal == 0:
            return ""
        
        # Calculate percentages
        protein_pct = (protein_cal / total_macro_cal) * 100
        carbs_pct = (carbs_cal / total_macro_cal) * 100
        fat_pct = (fat_cal / total_macro_cal) * 100
        
        # Create pie chart
        fig, ax = plt.subplots(figsize=(8, 8))
        
        sizes = [protein_pct, carbs_pct, fat_pct]
        labels = [f'Protein\n{protein_pct:.1f}%\n({nutrition_data["protein"]}g)',
                 f'Carbs\n{carbs_pct:.1f}%\n({nutrition_data["carbs"]}g)',
                 f'Fat\n{fat_pct:.1f}%\n({nutrition_data["fat"]}g)']
        colors_list = ['#ff9999', '#66b3ff', '#99ff99']
        
        wedges, texts = ax.pie(sizes, labels=labels, colors=colors_list,
                              autopct=None, startangle=90, textprops={'fontsize': 12})
        
        ax.set_title('Macro Distribution', fontsize=16, fontweight='bold', pad=20)
        
        # Save to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        plt.close()
        return image_base64
    
    def generate_meal_plan_pdf(self, meal_plan: Dict, user_info: Dict, 
                             output_path: Optional[str] = None) -> str:
        """
        Generate a comprehensive PDF meal plan report.
        
        Args:
            meal_plan: Complete meal plan dictionary
            user_info: User information dictionary
            output_path: Output file path (if None, creates temporary file)
            
        Returns:
            Path to generated PDF file
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.pdf')
        
        # Create document
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title = Paragraph("Personalized Indian Nutrition Plan", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # User Information Section
        story.append(Paragraph("User Profile", self.styles['Heading2']))
        
        user_data = [
            ['Age:', f"{user_info.get('age', 'N/A')} years"],
            ['Gender:', user_info.get('gender', 'N/A')],
            ['Weight:', f"{user_info.get('weight', 'N/A')} kg"],
            ['Height:', f"{user_info.get('height', 'N/A')} cm"],
            ['Activity Level:', user_info.get('activity_level', 'N/A')],
            ['Goal:', user_info.get('goal', 'N/A')],
            ['Dietary Preference:', user_info.get('dietary_preference', 'N/A')],
            ['Regional Preference:', user_info.get('region', 'N/A')]
        ]
        
        if 'bmi' in user_info and 'bmi_category' in user_info:
            user_data.append(['BMI:', f"{user_info['bmi']} ({user_info['bmi_category']})"])
        
        user_table = Table(user_data, colWidths=[2*inch, 3*inch])
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(user_table)
        story.append(Spacer(1, 30))
        
        # Nutrition Summary
        story.append(Paragraph("Daily Nutrition Summary", self.styles['Heading2']))
        
        daily_totals = meal_plan['daily_totals']
        target_nutrition = meal_plan['target_nutrition']
        
        nutrition_data = [
            ['Nutrient', 'Target', 'Actual', 'Difference'],
            ['Calories', f"{target_nutrition['calories']}", 
             f"{daily_totals['calories']:.0f}", 
             f"{daily_totals['calories'] - target_nutrition['calories']:+.0f}"],
            ['Protein (g)', f"{target_nutrition['protein']}", 
             f"{daily_totals['protein']:.1f}", 
             f"{daily_totals['protein'] - target_nutrition['protein']:+.1f}"],
            ['Carbs (g)', f"{target_nutrition['carbs']}", 
             f"{daily_totals['carbs']:.1f}", 
             f"{daily_totals['carbs'] - target_nutrition['carbs']:+.1f}"],
            ['Fat (g)', f"{target_nutrition['fat']}", 
             f"{daily_totals['fat']:.1f}", 
             f"{daily_totals['fat'] - target_nutrition['fat']:+.1f}"]
        ]
        
        nutrition_table = Table(nutrition_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
        nutrition_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(nutrition_table)
        story.append(Spacer(1, 30))
        
        # Meal Plan Details
        story.append(Paragraph("Detailed Meal Plan", self.styles['Heading2']))
        
        meal_names = {
            'breakfast': 'Breakfast',
            'morning_snack': 'Morning Snack',
            'lunch': 'Lunch', 
            'evening_snack': 'Evening Snack',
            'dinner': 'Dinner'
        }
        
        for meal_type, meal_data in meal_plan['meals'].items():
            # Meal title
            story.append(Paragraph(meal_names.get(meal_type, meal_type.title()), 
                                 self.styles['MealTitle']))
            
            # Food items
            for food in meal_data['foods']:
                food_text = (f"• {food['name']} - {food['serving_size']:.0f}g "
                           f"({food['calories']:.0f} cal, {food['protein']:.1f}g protein, "
                           f"{food['carbs']:.1f}g carbs, {food['fat']:.1f}g fat)")
                story.append(Paragraph(food_text, self.styles['FoodItem']))
            
            # Meal totals
            totals = meal_data['totals']
            total_text = (f"<b>Meal Total:</b> {totals['calories']:.0f} calories, "
                         f"{totals['protein']:.1f}g protein, {totals['carbs']:.1f}g carbs, "
                         f"{totals['fat']:.1f}g fat")
            story.append(Paragraph(total_text, self.styles['NutritionSummary']))
            story.append(Spacer(1, 15))
        
        # Additional Notes
        story.append(Spacer(1, 30))
        story.append(Paragraph("Important Notes", self.styles['Heading2']))
        
        notes = [
            "• This meal plan is generated based on your inputs and general nutritional guidelines.",
            "• Consult with a registered dietitian or healthcare provider before making significant dietary changes.",
            "• Adjust portion sizes based on your hunger, satiety, and energy levels.",
            "• Stay hydrated throughout the day with adequate water intake.",
            "• Include physical activity as recommended by health guidelines."
        ]
        
        for note in notes:
            story.append(Paragraph(note, self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def generate_comparison_pdf(self, variations: List[Dict], user_info: Dict,
                              output_path: Optional[str] = None) -> str:
        """
        Generate a PDF comparing multiple meal plan variations.
        
        Args:
            variations: List of meal plan variations
            user_info: User information
            output_path: Output file path
            
        Returns:
            Path to generated PDF file
        """
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.pdf')
        
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        # Title
        title = Paragraph("Indian Nutrition Plan - Multiple Variations", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 30))
        
        # Generate each variation
        for i, variation_data in enumerate(variations):
            if i > 0:
                story.append(PageBreak())
            
            variation_num = variation_data['variation_number']
            meal_plan = variation_data['meal_plan']
            
            # Variation header
            var_title = Paragraph(f"Variation {variation_num}", self.styles['Heading1'])
            story.append(var_title)
            story.append(Spacer(1, 20))
            
            # Add meal plan content (similar to single plan but condensed)
            self._add_condensed_meal_plan(story, meal_plan)
        
        doc.build(story)
        return output_path
    
    def _add_condensed_meal_plan(self, story: List, meal_plan: Dict):
        """Add a condensed version of meal plan to the story."""
        meal_names = {
            'breakfast': 'Breakfast',
            'morning_snack': 'Morning Snack', 
            'lunch': 'Lunch',
            'evening_snack': 'Evening Snack',
            'dinner': 'Dinner'
        }
        
        for meal_type, meal_data in meal_plan['meals'].items():
            story.append(Paragraph(meal_names.get(meal_type, meal_type.title()),
                                 self.styles['MealTitle']))
            
            # Condensed food list
            food_names = [food['name'] for food in meal_data['foods']]
            food_text = " • ".join(food_names)
            story.append(Paragraph(food_text, self.styles['FoodItem']))
            
            # Meal totals
            totals = meal_data['totals']
            total_text = f"Total: {totals['calories']:.0f} cal"
            story.append(Paragraph(total_text, self.styles['NutritionSummary']))
            story.append(Spacer(1, 10))
