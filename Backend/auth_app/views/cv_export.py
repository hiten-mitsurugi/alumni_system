"""
CV Export API View
Generates and downloads professional PDF CV
"""

from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from auth_app.pdf_utils.pdf_cv_generator import CVPDFGenerator


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def export_cv(request):
    """
    Export user's CV as a professional PDF document.
    
    Method: POST or GET
    Parameters:
        - include_picture (bool, optional): Include profile picture in CV. Default: True
    
    Returns:
        PDF file download with Content-Disposition header
    
    Example:
        POST /api/auth/profile/export-cv/
        Body: {"include_picture": true}
    """
    try:
        # Get parameters
        if request.method == 'POST':
            include_picture = request.data.get('include_picture', True)
        else:
            include_picture = request.GET.get('include_picture', 'true').lower() == 'true'
        
        # Get authenticated user
        user = request.user
        
        # Generate PDF
        generator = CVPDFGenerator(user=user, include_picture=include_picture)
        pdf_bytes = generator.generate()
        
        # Create response
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        
        # Set filename
        filename = f"{user.first_name}_{user.last_name}_CV.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        # Log error and return user-friendly message
        import traceback
        traceback.print_exc()
        
        return Response(
            {
                'error': 'Failed to generate CV',
                'detail': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
