# Normal clinical ranges (simplified but realistic)
NORMAL_RANGES = {
    "HGB": (12, 16),     # Hemoglobin
    "SGP": (70, 140),    # Glucose
    "TCP": (125, 200),   # Total Cholesterol
    "HDP": (40, 60),     # HDL
    "LCP": (0, 130),     # LDL
    "TGP": (0, 150),     # Triglycerides
    "VAP": (20, 60),     # Vitamin A
    "VEP": (5, 20),      # Vitamin E
    "VCP": (0.2, 1.2),   # Vitamin C
    "FEP": (12, 300),    # Iron/Ferritin
}

# Foods to fix deficiencies
FOOD_RECO = {
    "HGB": ["Spinach", "Beetroot", "Chicken", "Eggs"],
    "SGP": ["Whole grains", "Green vegetables", "Nuts"],
    "TCP": ["Oats", "Almonds", "Avocado"],
    "HDP": ["Olive oil", "Fish", "Walnuts"],
    "LCP": ["Green tea", "Oats", "Fruits"],
    "TGP": ["Seeds", "Leafy greens", "Whole grains"],
    "VAP": ["Carrots", "Sweet potato"],
    "VEP": ["Nuts", "Seeds", "Vegetable oils"],
    "VCP": ["Citrus fruits", "Strawberries"],
    "FEP": ["Spinach", "Beans", "Red meat"],
}


def analyze_biomarkers(values):
    """
    values = {"HGB":12, "SGP":90, ...}
    """
    report = []
    deficiencies = []

    for test, (low, high) in NORMAL_RANGES.items():

        if test not in values or values[test] is None:
            continue

        val = values[test]

        if val < low:
            report.append(f"{test}: LOW")
            deficiencies.append(test)

        elif val > high:
            report.append(f"{test}: HIGH")

        else:
            report.append(f"{test}: Normal")

    return report, deficiencies


def recommend_foods(def_list):
    final = []
    for d in def_list:
        if d in FOOD_RECO:
            final.append(f"{d}: Eat → {', '.join(FOOD_RECO[d])}")
    return final


def generate_pdf(report_dict, filename="nutrition_report.pdf"):
    """Generate a simple PDF report from a dict.
    report_dict = {"biomarkers": {}, "recommendations": [], "calories": 0, "macros": {}}
    Returns the file path.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from datetime import datetime

        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("Personalized Nutrition Report", styles['Heading1']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 18))

        story.append(Paragraph(f"Daily Calories: <b>{report_dict.get('calories', 0)} kcal</b>", styles['Heading2']))
        macros = report_dict.get('macros', {})
        story.append(Paragraph(f"Macro split: Carbs {macros.get('carbs',0.5)*100:.0f}% • Protein {macros.get('protein',0.2)*100:.0f}% • Fat {macros.get('fat',0.3)*100:.0f}%", styles['Normal']))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Recommendations", styles['Heading2']))
        for r in report_dict.get('recommendations', []):
            story.append(Paragraph(f"• {r}", styles['Normal']))

        doc.build(story)
        return filename
    except Exception as e:
        print(f"PDF generation failed: {e}")
        return None
