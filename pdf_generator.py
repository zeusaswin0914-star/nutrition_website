"""PDF report generation for nutrition recommendations."""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from datetime import datetime
import os


def generate_pdf_report(user_name, age_category, assessments, recommendations, health_conditions, output_path):
    """
    Generate a comprehensive PDF nutrition report.
    
    Args:
        user_name: Name of the user
        age_category: Age category (toddler, child, teen, adult, senior)
        assessments: List of lab assessments
        recommendations: Recommendation dictionary from recommendation_engine
        health_conditions: User's health conditions
        output_path: Path to save the PDF file
        
    Returns:
        Path to the generated PDF
    """
    
    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        title=f"Nutrition Report - {user_name}"
    )
    
    # Container for PDF elements
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2E5090'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2E5090'),
        spaceAfter=12,
        spaceBefore=12,
        borderColor=colors.HexColor('#2E5090'),
        borderWidth=1,
        borderPadding=6
    )
    
    subheading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=10,
        leading=14
    )
    
    # Title Section
    elements.append(Paragraph("Personalized Nutrition Report", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # User Information Section
    user_info = f"<b>Name:</b> {user_name} | <b>Age Category:</b> {age_category.title()} | <b>Report Date:</b> {datetime.now().strftime('%B %d, %Y')}"
    elements.append(Paragraph(user_info, body_style))
    
    if health_conditions:
        health_str = f"<b>Health Conditions:</b> {health_conditions}"
        elements.append(Paragraph(health_str, body_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Lab Assessment Section
    if assessments:
        elements.append(Paragraph("Blood Test Assessment", heading_style))
        
        # Create assessment table
        assessment_data = [['Test Name', 'Value', 'Normal Range', 'Status']]
        for assessment in assessments:
            status_color = 'Green' if assessment['status'] == 'NORMAL' else 'Red'
            assessment_data.append([
                assessment['test'],
                f"{assessment['value']} {assessment['unit']}",
                assessment['normal_range'],
                f"<font color='{status_color}'><b>{assessment['status']}</b></font>"
            ])
        
        assessment_table = Table(assessment_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.2*inch])
        assessment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E5090')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
        ]))
        
        elements.append(assessment_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Recommendations Section
    if recommendations.get('test_recommendations'):
        elements.append(Paragraph("Personalized Recommendations", heading_style))
        
        for reco in recommendations['test_recommendations']:
            elements.append(Paragraph(f"<b>{reco['test']} - {reco['status']}</b>", subheading_style))
            elements.append(Paragraph(reco['issue'], body_style))
            
            # Recommended Foods
            if reco['foods']:
                foods_str = ', '.join(reco['foods'][:6])
                elements.append(Paragraph(f"<b>Recommended Foods:</b> {foods_str}", body_style))
            
            # Supplements
            if reco['supplements']:
                supps_str = ', '.join(reco['supplements'])
                elements.append(Paragraph(f"<b>Supplements to Consider:</b> {supps_str}", body_style))
            
            # Actions
            if reco['actions']:
                actions_str = ' | '.join(reco['actions'][:3])
                elements.append(Paragraph(f"<b>Action Steps:</b> {actions_str}", body_style))
            
            elements.append(Spacer(1, 0.15*inch))
        
        elements.append(Spacer(1, 0.2*inch))
    
    # Age-Specific Guidance
    if recommendations.get('age_guidance'):
        elements.append(PageBreak())
        elements.append(Paragraph(f"Age-Specific Guidance ({age_category.title()})", heading_style))
        
        guidance = recommendations['age_guidance']
        elements.append(Paragraph(f"<b>Focus:</b> {guidance['focus']}", body_style))
        elements.append(Paragraph(f"<b>Key Nutrients:</b> {', '.join(guidance['key_nutrients'])}", body_style))
        elements.append(Paragraph(f"<b>Daily Meals:</b> {guidance['daily_meals']}", body_style))
        
        elements.append(Paragraph("<b>Tips:</b>", subheading_style))
        for tip in guidance['tips']:
            elements.append(Paragraph(f"• {tip}", body_style))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # General Tips
    if recommendations.get('general_tips'):
        elements.append(Paragraph("General Nutrition Tips", heading_style))
        for tip in recommendations['general_tips']:
            elements.append(Paragraph(f"• {tip}", body_style))
        
        elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    footer_text = recommendations.get('follow_up', 'Please consult with a healthcare provider for personalized medical advice.')
    elements.append(Paragraph(f"<i><b>Important:</b> {footer_text}</i>", body_style))
    
    elements.append(Spacer(1, 0.15*inch))
    elements.append(Paragraph(f"<i>Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>", body_style))
    
    # Build PDF
    try:
        doc.build(elements)
        return output_path
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None


def generate_sample_report(report_id, user_name, age_category):
    """Generate a sample report for demonstration."""
    
    sample_assessments = [
        {
            'test': 'Hemoglobin',
            'value': 12.5,
            'unit': 'g/dL',
            'normal_range': '12.0-16.0',
            'status': 'NORMAL',
            'severity': 'ok'
        },
        {
            'test': 'Vitamin D',
            'value': 22.5,
            'unit': 'ng/mL',
            'normal_range': '30-100',
            'status': 'LOW',
            'severity': 'concern'
        }
    ]
    
    sample_recommendations = {
        'test_recommendations': [
            {
                'test': 'Vitamin D',
                'status': 'LOW',
                'issue': 'Low vitamin D affects bone health and immunity',
                'foods': ['Fatty fish (salmon)', 'Egg yolks', 'Fortified milk'],
                'supplements': ['Vitamin D3 supplement'],
                'actions': ['Increase sun exposure', 'Consume fortified dairy']
            }
        ],
        'age_guidance': {
            'focus': f'Nutrition for {age_category}',
            'key_nutrients': ['Calcium', 'Vitamin D', 'Protein'],
            'daily_meals': '3 meals + snacks',
            'tips': ['Include calcium-rich foods', 'Get adequate sunlight', 'Stay hydrated']
        },
        'general_tips': [
            'Eat a variety of colorful fruits and vegetables',
            'Include protein sources at each meal',
            'Drink adequate water throughout the day'
        ],
        'follow_up': 'Consult with a healthcare provider for personalized medical advice.'
    }
    
    return sample_assessments, sample_recommendations
