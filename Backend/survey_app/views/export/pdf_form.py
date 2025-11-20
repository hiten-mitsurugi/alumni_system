"""
PDF Form Export - Complete Analytics
=====================================
Complete form analytics PDF with ALL charts, graphs, and statistics for all question types.
Includes form title from template and multi-category support.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from ...models import SurveyCategory, SurveyQuestion, SurveyResponse, SurveyTemplate
from ...permissions import IsSurveyAdmin
from .pdf_helpers import extract_value_for_pdf


@api_view(['POST'])
@permission_classes([IsSurveyAdmin])
def form_analytics_pdf_export(request):
    """
    Export complete form analytics (all categories) as comprehensive PDF report with charts, graphs and statistics.
    Accepts category_ids array to specify which categories to include.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
        from reportlab.graphics.charts.piecharts import Pie
        from reportlab.lib.enums import TA_CENTER
        from datetime import datetime
        import io
        
        # Get category_ids from request
        category_ids = request.data.get('category_ids', [])
        programs = request.data.get('programs', [])  # Filter by programs
        graduation_years = request.data.get('graduation_years', [])  # Filter by graduation years
        
        # Try to find the template/form name from categories
        form_title = "Survey Analytics Report"
        if category_ids:
            # Find template that contains these categories
            template = SurveyTemplate.objects.filter(
                categories__id__in=category_ids,
                is_active=True
            ).first()
            if template:
                form_title = template.name
            
            categories = SurveyCategory.objects.filter(
                id__in=category_ids,
                is_active=True
            ).order_by('order', 'created_at')
        else:
            # Default to registration survey categories
            template = SurveyTemplate.objects.filter(is_default=True, is_active=True).first()
            if template:
                form_title = template.name
            
            categories = SurveyCategory.objects.filter(
                include_in_registration=True,
                is_active=True
            ).order_by('order', 'created_at')
        
        if not categories.exists():
            return Response({'error': 'No categories found for export'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all questions from selected categories
        category_ids = [cat.id for cat in categories]
        questions = SurveyQuestion.objects.filter(
            category_id__in=category_ids,
            is_active=True
        ).select_related('category').order_by('category__order', 'order', 'question_text')
        
        # Get all responses for these questions
        responses = SurveyResponse.objects.filter(
            question__category_id__in=category_ids
        ).select_related('user', 'question')
        
        # Apply program filter
        if programs:
            program_list = programs if isinstance(programs, list) else [p.strip() for p in programs.split(',') if p.strip()]
            if program_list:
                responses = responses.filter(user__program__in=program_list)
        
        # Apply graduation year filter
        if graduation_years:
            if isinstance(graduation_years, list):
                year_list = [int(y) for y in graduation_years if str(y).strip()]
            else:
                try:
                    year_list = [int(y.strip()) for y in str(graduation_years).split(',') if y.strip()]
                except (ValueError, TypeError):
                    year_list = []
            if year_list:
                responses = responses.filter(user__year_graduated__in=year_list)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_alumni_queryset = User.objects.filter(user_type=3, is_approved=True)
        
        # Apply same filters to total alumni count
        if programs:
            program_list = programs if isinstance(programs, list) else [p.strip() for p in programs.split(',') if p.strip()]
            if program_list:
                total_alumni_queryset = total_alumni_queryset.filter(program__in=program_list)
        
        if graduation_years:
            if isinstance(graduation_years, list):
                year_list = [int(y) for y in graduation_years if str(y).strip()]
            else:
                try:
                    year_list = [int(y.strip()) for y in str(graduation_years).split(',') if y.strip()]
                except (ValueError, TypeError):
                    year_list = []
            if year_list:
                total_alumni_queryset = total_alumni_queryset.filter(year_graduated__in=year_list)
        
        total_alumni = total_alumni_queryset.count()
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            topMargin=0.5*inch, 
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=26,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#1e40af'),
            spaceBefore=6,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        section_heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#7c3aed'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        question_heading_style = ParagraphStyle(
            'QuestionHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        # Build story
        story = []
        
        # Title - Use the form name
        story.append(Paragraph(form_title, title_style))
        story.append(Paragraph(f"Complete Analytics Report", subtitle_style))
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        story.append(Paragraph(f"<i>Generated on {timestamp}</i>", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        total_responses = responses.values('user').distinct().count()
        response_rate = round((total_responses / total_alumni * 100) if total_alumni > 0 else 0, 1)
        total_questions = questions.count()
        total_categories = categories.count()
        
        story.append(Paragraph("Executive Summary", heading_style))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Categories', str(total_categories)],
            ['Total Questions', str(total_questions)],
            ['Total Responses', str(total_responses)],
            ['Total Alumni (Filtered)', str(total_alumni)],
            ['Overall Response Rate', f"{response_rate}%"],
        ]
        
        # Add filter information if present
        if programs:
            program_names = programs if isinstance(programs, list) else programs.split(',')
            summary_data.append(['Program Filter', ', '.join(program_names)])
        if graduation_years:
            year_names = graduation_years if isinstance(graduation_years, list) else graduation_years.split(',')
            summary_data.append(['Graduation Year Filter', ', '.join(map(str, year_names))])
        
        summary_data.append(['Report Date', datetime.now().strftime('%Y-%m-%d')])
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2.7*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eff6ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#60a5fa')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(PageBreak())
        
        # Process each category and its questions
        for cat_idx, category in enumerate(categories, 1):
            # Category header
            story.append(Paragraph(f"Category {cat_idx}: {category.name}", section_heading_style))
            if category.description:
                story.append(Paragraph(f"<i>{category.description}</i>", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Get questions for this category
            category_questions = questions.filter(category=category)
            
            for q_idx, question in enumerate(category_questions, 1):
                question_responses = responses.filter(question=question)
                response_count = question_responses.count()
                
                # Question header
                question_text = f"{cat_idx}.{q_idx}. {question.question_text}"
                story.append(Paragraph(question_text, question_heading_style))
                
                # Question metadata
                meta_text = f"<i>Type: {question.get_question_type_display()} | Responses: {response_count}"
                if response_count > 0 and total_alumni > 0:
                    q_response_rate = round((response_count / total_alumni * 100), 1)
                    meta_text += f" | Response Rate: {q_response_rate}%"
                meta_text += "</i>"
                story.append(Paragraph(meta_text, styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                
                # Process based on question type
                if question.question_type == 'checkbox':
                    # Checkbox - HORIZONTAL BAR CHART
                    distribution = {}
                    for response in question_responses:
                        values = extract_value_for_pdf(response.response_data)
                        if isinstance(values, list):
                            for val in values:
                                distribution[str(val)] = distribution.get(str(val), 0) + 1
                        elif values:
                            distribution[str(values)] = distribution.get(str(values), 0) + 1
                    
                    # Include all options even with 0 count
                    options = question.get_options_list()
                    for option in options:
                        if str(option) not in distribution:
                            distribution[str(option)] = 0
                    
                    if distribution:
                        sorted_dist = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
                        
                        chart_height = max(150, len(sorted_dist) * 30)
                        drawing = Drawing(500, chart_height)
                        chart = HorizontalBarChart()
                        chart.x = 120
                        chart.y = 20
                        chart.height = chart_height - 40
                        chart.width = 350
                        
                        chart.data = [[item[1] for item in sorted_dist]]
                        chart.categoryAxis.categoryNames = [item[0] for item in sorted_dist]
                        
                        chart.bars[0].fillColor = colors.HexColor('#3b82f6')
                        chart.valueAxis.valueMin = 0
                        chart.categoryAxis.labels.fontSize = 8
                        chart.valueAxis.labels.fontSize = 8
                        
                        drawing.add(chart)
                        story.append(drawing)
                        story.append(Spacer(1, 0.1*inch))
                        
                        dist_data = [['Option', 'Count', 'Percentage']]
                        for option, count in sorted_dist:
                            percentage = round((count / response_count * 100), 1) if response_count > 0 else 0
                            dist_data.append([option, str(count), f"{percentage}%"])
                        
                        dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.7*inch])
                        dist_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#60a5fa')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
                        ]))
                        story.append(dist_table)
                
                elif question.question_type in ['radio', 'select']:
                    # Radio/Select - PIE CHART
                    distribution = {}
                    for response in question_responses:
                        value = extract_value_for_pdf(response.response_data)
                        if value:
                            distribution[str(value)] = distribution.get(str(value), 0) + 1
                    
                    options = question.get_options_list()
                    for option in options:
                        if str(option) not in distribution:
                            distribution[str(option)] = 0
                    
                    if distribution and response_count > 0:
                        drawing = Drawing(450, 200)
                        pie = Pie()
                        pie.x = 100
                        pie.y = 20
                        pie.width = 150
                        pie.height = 150
                        
                        pie.data = list(distribution.values())
                        pie.labels = [f"{k}: {v}" for k, v in distribution.items()]
                        
                        color_palette = [
                            colors.HexColor('#a855f7'), colors.HexColor('#ec4899'),
                            colors.HexColor('#f97316'), colors.HexColor('#eab308'),
                            colors.HexColor('#84cc16'), colors.HexColor('#22c55e'),
                            colors.HexColor('#14b8a6'), colors.HexColor('#06b6d4'),
                            colors.HexColor('#3b82f6'), colors.HexColor('#6366f1'),
                        ]
                        for i, slice_color in enumerate(color_palette[:len(pie.data)]):
                            pie.slices[i].fillColor = slice_color
                        
                        drawing.add(pie)
                        story.append(drawing)
                        story.append(Spacer(1, 0.1*inch))
                        
                        dist_data = [['Option', 'Count', 'Percentage']]
                        for option, count in distribution.items():
                            percentage = round((count / response_count * 100), 1)
                            dist_data.append([option, str(count), f"{percentage}%"])
                        
                        dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.7*inch])
                        dist_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#60a5fa')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
                        ]))
                        story.append(dist_table)
                
                elif question.question_type == 'yes_no':
                    # Yes/No - PIE CHART with green/red colors
                    distribution = {'Yes': 0, 'No': 0}
                    for response in question_responses:
                        value = extract_value_for_pdf(response.response_data)
                        if value in ['Yes', 'yes', True, 'true', '1', 1]:
                            distribution['Yes'] += 1
                        elif value in ['No', 'no', False, 'false', '0', 0]:
                            distribution['No'] += 1
                    
                    if response_count > 0:
                        drawing = Drawing(450, 200)
                        pie = Pie()
                        pie.x = 150
                        pie.y = 20
                        pie.width = 150
                        pie.height = 150
                        
                        pie.data = [distribution['Yes'], distribution['No']]
                        pie.labels = [f"Yes: {distribution['Yes']}", f"No: {distribution['No']}"]
                        
                        pie.slices[0].fillColor = colors.HexColor('#22c55e')
                        pie.slices[1].fillColor = colors.HexColor('#ef4444')
                        
                        drawing.add(pie)
                        story.append(drawing)
                        story.append(Spacer(1, 0.1*inch))
                        
                        dist_data = [
                            ['Response', 'Count', 'Percentage'],
                            ['Yes', str(distribution['Yes']), f"{round(distribution['Yes']/response_count*100, 1)}%"],
                            ['No', str(distribution['No']), f"{round(distribution['No']/response_count*100, 1)}%"]
                        ]
                        
                        dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.7*inch])
                        dist_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#60a5fa')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
                        ]))
                        story.append(dist_table)
                
                elif question.question_type == 'rating':
                    # Rating scale - BAR CHART with average
                    values = []
                    distribution = {}
                    
                    for response in question_responses:
                        value = extract_value_for_pdf(response.response_data)
                        if value is not None:
                            try:
                                numeric_value = float(value)
                                values.append(numeric_value)
                                rating_key = int(numeric_value)
                                distribution[rating_key] = distribution.get(rating_key, 0) + 1
                            except (ValueError, TypeError):
                                pass
                    
                    if values:
                        avg = round(sum(values) / len(values), 2)
                        min_val = question.min_value or 1
                        max_val = question.max_value or 5
                        
                        avg_data = [[f'Average Rating: {avg} out of {max_val}']]
                        avg_table = Table(avg_data, colWidths=[5.7*inch])
                        avg_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef3c7')),
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#92400e')),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 14),
                            ('TOPPADDING', (0, 0), (-1, -1), 12),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#fbbf24')),
                        ]))
                        story.append(avg_table)
                        story.append(Spacer(1, 0.15*inch))
                        
                        for rating in range(min_val, max_val + 1):
                            if rating not in distribution:
                                distribution[rating] = 0
                        
                        drawing = Drawing(500, 200)
                        chart = VerticalBarChart()
                        chart.x = 50
                        chart.y = 20
                        chart.height = 150
                        chart.width = 400
                        
                        sorted_ratings = sorted(distribution.items())
                        chart.data = [[item[1] for item in sorted_ratings]]
                        chart.categoryAxis.categoryNames = [f"{item[0]} {'star' if item[0] == 1 else 'stars'}" for item in sorted_ratings]
                        
                        chart.bars[0].fillColor = colors.HexColor('#fbbf24')
                        chart.valueAxis.valueMin = 0
                        chart.categoryAxis.labels.angle = 0
                        chart.categoryAxis.labels.fontSize = 8
                        chart.valueAxis.labels.fontSize = 8
                        
                        drawing.add(chart)
                        story.append(drawing)
                        story.append(Spacer(1, 0.1*inch))
                        
                        dist_data = [['Rating', 'Count', 'Percentage']]
                        for rating, count in sorted_ratings:
                            percentage = round((count / len(values) * 100), 1)
                            dist_data.append([f"{rating} {'star' if rating == 1 else 'stars'}", str(count), f"{percentage}%"])
                        dist_data.append(['Average', str(avg), ''])
                        
                        dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.7*inch])
                        dist_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#60a5fa')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fef3c7')),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#eff6ff')]),
                        ]))
                        story.append(dist_table)
                
                elif question.question_type == 'number':
                    # Number questions - BAR CHART with statistics
                    values = []
                    distribution = {}
                    
                    for response in question_responses:
                        value = extract_value_for_pdf(response.response_data)
                        if value is not None:
                            try:
                                num_value = float(value)
                                values.append(num_value)
                                distribution[num_value] = distribution.get(num_value, 0) + 1
                            except (ValueError, TypeError):
                                pass
                    
                    if values:
                        avg = round(sum(values) / len(values), 2)
                        min_val = round(min(values), 2)
                        max_val = round(max(values), 2)
                        
                        stats_data = [
                            ['Average', 'Minimum', 'Maximum'],
                            [str(avg), str(min_val), str(max_val)]
                        ]
                        stats_table = Table(stats_data, colWidths=[1.9*inch, 1.9*inch, 1.9*inch])
                        stats_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#14b8a6')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ccfbf1')),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 11),
                            ('TOPPADDING', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#14b8a6')),
                        ]))
                        story.append(stats_table)
                        story.append(Spacer(1, 0.15*inch))
                        
                        if len(distribution) <= 15:
                            drawing = Drawing(500, 200)
                            chart = VerticalBarChart()
                            chart.x = 50
                            chart.y = 20
                            chart.height = 150
                            chart.width = 400
                            
                            sorted_dist = sorted(distribution.items())
                            chart.data = [[item[1] for item in sorted_dist]]
                            chart.categoryAxis.categoryNames = [str(item[0]) for item in sorted_dist]
                            
                            chart.bars[0].fillColor = colors.HexColor('#14b8a6')
                            chart.valueAxis.valueMin = 0
                            chart.categoryAxis.labels.angle = 45
                            chart.categoryAxis.labels.fontSize = 7
                            chart.valueAxis.labels.fontSize = 8
                            
                            drawing.add(chart)
                            story.append(drawing)
                            story.append(Spacer(1, 0.1*inch))
                            
                            dist_data = [['Value', 'Count', 'Percentage']]
                            for value, count in sorted_dist:
                                percentage = round((count / len(values) * 100), 1)
                                dist_data.append([str(value), str(count), f"{percentage}%"])
                            
                            dist_table = Table(dist_data, colWidths=[2*inch, 1.5*inch, 2.2*inch])
                            dist_table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#60a5fa')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, -1), 9),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
                            ]))
                            story.append(dist_table)
                
                elif question.question_type == 'year':
                    # Year questions - BAR CHART
                    distribution = {}
                    
                    for response in question_responses:
                        value = extract_value_for_pdf(response.response_data)
                        if value:
                            distribution[str(value)] = distribution.get(str(value), 0) + 1
                    
                    if distribution:
                        sorted_years = sorted(distribution.items(), key=lambda x: x[0], reverse=True)
                        
                        drawing = Drawing(500, 200)
                        chart = VerticalBarChart()
                        chart.x = 50
                        chart.y = 20
                        chart.height = 150
                        chart.width = 400
                        
                        chart.data = [[item[1] for item in sorted_years]]
                        chart.categoryAxis.categoryNames = [item[0] for item in sorted_years]
                        
                        chart.bars[0].fillColor = colors.HexColor('#10b981')
                        chart.valueAxis.valueMin = 0
                        chart.categoryAxis.labels.angle = 45
                        chart.categoryAxis.labels.fontSize = 8
                        chart.valueAxis.labels.fontSize = 8
                        
                        drawing.add(chart)
                        story.append(drawing)
                        story.append(Spacer(1, 0.1*inch))
                        
                        dist_data = [['Year', 'Count', 'Percentage']]
                        for year, count in sorted_years:
                            percentage = round((count / response_count * 100), 1)
                            dist_data.append([year, str(count), f"{percentage}%"])
                        
                        dist_table = Table(dist_data, colWidths=[2.5*inch, 1.5*inch, 1.7*inch])
                        dist_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#60a5fa')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 9),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eff6ff')]),
                        ]))
                        story.append(dist_table)
                
                elif question.question_type in ['text', 'textarea', 'email']:
                    # Text responses - show response count only (privacy)
                    count_data = [[f'{response_count} text responses received']]
                    count_table = Table(count_data, colWidths=[5.7*inch])
                    count_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#dbeafe')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1e40af')),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('TOPPADDING', (0, 0), (-1, -1), 15),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#60a5fa')),
                    ]))
                    story.append(count_table)
                    story.append(Paragraph("<i>Individual responses are protected for privacy</i>", styles['Normal']))
                
                story.append(Spacer(1, 0.25*inch))
            
            # Add page break after each category except the last
            if cat_idx < len(categories):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        # Return response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Use form title in filename
        safe_form_name = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in form_title)
        filename = f'{safe_form_name}_Complete_Analytics_{timestamp}.pdf'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except ImportError:
        return Response({
            'error': 'ReportLab library not installed. Run: pip install reportlab'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': f'PDF export failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
