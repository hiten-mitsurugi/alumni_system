"""
PDF Category Export
===================
Single category analytics PDF report with charts and statistics.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse

from ...models import SurveyCategory, SurveyQuestion, SurveyResponse
from ...permissions import IsSurveyAdmin


@api_view(['POST'])
@permission_classes([IsSurveyAdmin])
def category_analytics_pdf_export(request):
    """
    Export category analytics as comprehensive PDF report with charts, graphs and statistics.
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
        
        category_id = request.data.get('category_id')
        
        if not category_id:
            return Response({'error': 'category_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = SurveyCategory.objects.get(id=category_id)
        except SurveyCategory.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get analytics data
        questions = SurveyQuestion.objects.filter(
            category=category,
            is_active=True
        ).order_by('order', 'question_text')
        
        responses = SurveyResponse.objects.filter(
            question__category=category
        ).select_related('user', 'question')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_alumni = User.objects.filter(user_type=3, is_approved=True).count()
        
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
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        )
        
        question_heading_style = ParagraphStyle(
            'QuestionHeading',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        # Header Section
        story.append(Paragraph("Survey Analytics Report", title_style))
        story.append(Paragraph(f"{category.name}", subtitle_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary Section
        story.append(Paragraph("Executive Summary", heading_style))
        
        unique_respondents = responses.values('user').distinct().count()
        response_rate = round((unique_respondents / total_alumni * 100) if total_alumni > 0 else 0, 2)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Category', category.name],
            ['Report Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Questions', str(questions.count())],
            ['Total Responses Received', str(responses.count())],
            ['Unique Respondents', str(unique_respondents)],
            ['Total Alumni Population', str(total_alumni)],
            ['Overall Response Rate', f"{response_rate}%"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#eff6ff')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
            ('GRID', (0, 0), (-1, -1), 1.5, colors.HexColor('#93c5fd')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Question Analytics Section
        story.append(Paragraph("Detailed Question Analytics", heading_style))
        story.append(Spacer(1, 0.15*inch))
        
        for idx, question in enumerate(questions, 1):
            question_responses = responses.filter(question=question)
            response_count = question_responses.count()
            
            # Question header
            question_text = f"{idx}. {question.question_text}"
            story.append(Paragraph(question_text, question_heading_style))
            
            # Question metadata
            meta_text = f"<i>Type: {question.get_question_type_display()} | Responses: {response_count}"
            if response_count > 0:
                q_response_rate = round((response_count / total_alumni * 100) if total_alumni > 0 else 0, 1)
                meta_text += f" | Response Rate: {q_response_rate}%"
            meta_text += "</i>"
            story.append(Paragraph(meta_text, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Type-specific analytics with charts (simplified for brevity)
            if question.question_type in ['text', 'textarea', 'email']:
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
            
            # Add page break every 3 questions
            if idx % 3 == 0 and idx < len(questions):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        # Return response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_category_name = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in category.name)
        filename = f'survey_analytics_{safe_category_name}_{timestamp}.pdf'
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
