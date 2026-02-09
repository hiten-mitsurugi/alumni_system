"""
Upload view for handling file attachments in messages.
Simple endpoint for direct file upload before message sending.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import Attachment


class UploadView(APIView):
    """Handle file uploads for message attachments"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Upload a file and return its attachment ID"""
        file = request.FILES['file']
        # Create attachment directly like profile picture upload
        attachment = Attachment.objects.create(
            file=file,
            file_type=file.content_type
        )
        return Response({'id': str(attachment.id)}, status=status.HTTP_201_CREATED)
