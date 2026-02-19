"""
PDF Report Generator V2

Generates a comprehensive, colorful PDF report including:
- Patient Details
- Health Status & BMI
- Lab Analysis Summary
- 7-Day Diet Chart
- Food Recommendations
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PIL import Image as PILImage
import os
from datetime import datetime
import io

class PDFReportGenerator:
    def __init__(self, buffer):
        self.buffer = buffer
        self.styles = getSampleStyleSheet()
        self.width, self.height = A4
        self._create_custom_styles()

    def _create_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='Header1',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0d4c6b'),
            alignment=1, # Center
            spaceAfter=20
        ))
        self.styles.add(ParagraphStyle(
            name='Header2',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#0d4c6b'),
            spaceBefore=15,
            spaceAfter=10,
            borderPadding=(0, 0, 5, 0),
            borderWidth=0,
            borderColor=colors.HexColor('#0d4c6b')
        ))
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6
        ))
        self.styles.add(ParagraphStyle(
            name='StatusNormal',
            parent=self.styles['Normal'],
            textColor=colors.green,
            fontSize=12,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='StatusWarning',
            parent=self.styles['Normal'],
            textColor=colors.orange,
            fontSize=12,
            fontName='Helvetica-Bold'
        ))
        self.styles.add(ParagraphStyle(
            name='StatusAlert',
            parent=self.styles['Normal'],
            textColor=colors.red,
            fontSize=12,
            fontName='Helvetica-Bold'
        ))

    def generate(self, user_data, lab_results, health_status, diet_plan, deficiencies, diet_charts=None, recommendation_table_data=None):
        elements = []

        # -- Title Page --
        elements.append(Paragraph("Personalized Nutrition Report", self.styles['Header1']))
        elements.append(Spacer(1, 0.2 * inch))
        
        # User Info Table (Unchanged)
        data = [
            ["Name:", user_data.get('name', 'Valued Patient'), "Date:", datetime.now().strftime("%Y-%m-%d")],
            ["Age:", str(user_data.get('age', 'N/A')), "Gender:", "Male" if user_data.get('gender') == 1 else "Female"],
            ["Weight:", f"{user_data.get('weight', 'N/A')} kg", "Height:", f"{user_data.get('height', 'N/A')} cm"],
            ["BMI:", f"{user_data.get('bmi', 'N/A'):.1f}", "Goal:", user_data.get('goal', 'Health')]
        ]
        
        t = Table(data, colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.aliceblue),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.white),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3 * inch))

        # -- Section 2: Health Analysis --
        elements.append(Paragraph("Health Analysis Summary", self.styles['Header2']))
        
        status_style = self.styles['StatusNormal']
        if health_status == 'At Risk': status_style = self.styles['StatusWarning']
        elif health_status == 'Action Needed': status_style = self.styles['StatusAlert']
        
        elements.append(Paragraph(f"Overall Health Data Status: <font color='{status_style.textColor}'>{health_status}</font>", self.styles['Normal']))
        elements.append(Spacer(1, 0.1 * inch))
        
        if deficiencies:
            elements.append(Paragraph("<b>Identified Concerns:</b>", self.styles['NormalText']))
            for d in deficiencies:
                elements.append(Paragraph(f"• {d}", self.styles['NormalText']))
        else:
            elements.append(Paragraph("No significant deficiencies detected based on provided values.", self.styles['NormalText']))
            
        elements.append(Spacer(1, 0.2 * inch))
        
        # -- Charts (Macros) --
        if diet_charts and diet_charts.get('macronutrient_chart'):
            try:
                # Decode base64
                img_data = base64.b64decode(diet_charts['macronutrient_chart'].split(',')[1])
                img_stream = io.BytesIO(img_data)
                img = Image(img_stream, width=4*inch, height=3*inch)
                elements.append(Paragraph("Macronutrient Distribution", self.styles['Header2']))
                elements.append(img)
                elements.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                pass

        # -- Section 3: AI Food Recommendations Table --
        if recommendation_table_data:
            elements.append(Paragraph("AI Food Recommendations", self.styles['Header2']))
            
            rec_headers = ["Nutrient", "Value", "Status", "Recommended Foods"]
            rec_data = [rec_headers]
            
            for item in recommendation_table_data:
                rec_data.append([
                    item.get('nutrient', ''),
                    item.get('value', ''),
                    item.get('status', ''),
                    item.get('food', '')
                ])
                
            rt = Table(rec_data, colWidths=[1.5*inch, 1*inch, 1*inch, 3.5*inch])
            rt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0d4c6b')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.whitesmoke]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('WORDWRAP', (0,0), (-1,-1), True)
            ]))
            elements.append(rt)
            elements.append(Spacer(1, 0.3 * inch))

        elements.append(PageBreak())

        # -- Section 4: Diet Plan --
        elements.append(Paragraph("7-Day Personalized Diet Chart", self.styles['Header1']))
        elements.append(Spacer(1, 0.1 * inch))

        if isinstance(diet_plan, dict):
            # User Requested Order: Day | Breakfast | Lunch | Snacks | Dinner
            headers = ["Day", "Breakfast", "Lunch", "Snacks", "Dinner"]
            diet_data = [headers]
            
            days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            for day in days_order:
                day_meals = diet_plan.get(day, {})
                row = [
                    day,
                    day_meals.get('Breakfast', '-'),
                    day_meals.get('Lunch', '-'),
                    day_meals.get('Snacks', '-'), # Swapped order
                    day_meals.get('Dinner', '-')
                ]
                diet_data.append(row)

            dt = Table(diet_data, colWidths=[0.8*inch, 1.7*inch, 1.7*inch, 1.7*inch, 1.7*inch])
            dt.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1a6b8f')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0f9ff')]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#0d4c6b')),
                ('LEFTPADDING', (0,0), (-1,-1), 4),
                ('RIGHTPADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(dt)
        else:
             elements.append(Paragraph("Diet plan format not supported for PDF table generation.", self.styles['NormalText']))

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("<b>Note:</b> This diet plan is computer-generated based on your profile. Consult a nutritionist before making drastic changes.", self.styles['NormalText']))

        # Build
        doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        doc.build(elements)
        
        return self.buffer

def generate_pdf_v2(user_data, lab_results, health_status, diet_plan, deficiencies, diet_charts=None, recommendation_table_data=None):
    buffer = io.BytesIO()
    report = PDFReportGenerator(buffer)
    report.generate(user_data, lab_results, health_status, diet_plan, deficiencies, diet_charts, recommendation_table_data)
    buffer.seek(0)
    return buffer
