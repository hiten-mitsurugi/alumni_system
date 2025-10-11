"""
Alumni Directory Views - CRUD operations for alumni directory management
"""
from .base_imports import *

class AlumniDirectoryListCreateView(ListCreateAPIView):
    """
    List all alumni directory entries and create new ones.
    SuperAdmin only access.
    """
    serializer_class = AlumniDirectorySerializer
    permission_classes = [IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        return AlumniDirectory.objects.all().order_by('last_name', 'first_name')
    
    def perform_create(self, serializer):
        serializer.save()


class AlumniDirectoryDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete an alumni directory entry.
    SuperAdmin only access.
    """
    serializer_class = AlumniDirectorySerializer
    permission_classes = [IsAdminOrSuperAdmin]
    queryset = AlumniDirectory.objects.all()
    lookup_field = 'id'


class AlumniDirectoryImportView(APIView):
    """
    Import alumni data from CSV, Excel, or Text file.
    SuperAdmin only access.
    """
    permission_classes = [IsAdminOrSuperAdmin]
    
    def post(self, request):
        try:
            file = request.FILES.get('file')
            if not file:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                return Response(
                    {'error': 'File size too large (max 10MB)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Read file based on extension
            file_name = file.name.lower()
            
            try:
                if file_name.endswith('.csv'):
                    df = pd.read_csv(io.BytesIO(file.read()))
                elif file_name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(io.BytesIO(file.read()))
                elif file_name.endswith('.txt'):
                    content = file.read().decode('utf-8')
                    # Assume tab-separated values for text files
                    df = pd.read_csv(io.StringIO(content), sep='\t')
                else:
                    return Response(
                        {'error': 'Unsupported file format. Please use CSV, Excel, or TXT files.'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as e:
                return Response(
                    {'error': f'Error reading file: {str(e)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate required columns
            required_columns = ['first_name', 'last_name', 'birth_date', 'program', 'year_graduated', 'sex']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response(
                    {'error': f'Missing required columns: {", ".join(missing_columns)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process data
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Parse birth date
                    birth_date = pd.to_datetime(row['birth_date']).date()
                    
                    # Create or update alumni directory entry
                    alumni_data = {
                        'first_name': str(row['first_name']).strip(),
                        'last_name': str(row['last_name']).strip(),
                        'birth_date': birth_date,
                        'program': str(row['program']).strip(),
                        'year_graduated': int(row['year_graduated']),
                        'sex': str(row['sex']).strip().lower()
                    }
                    
                    # Check for optional fields
                    optional_fields = ['middle_name', 'student_id', 'address', 'phone', 'email']
                    for field in optional_fields:
                        if field in row and pd.notna(row[field]):
                            alumni_data[field] = str(row[field]).strip()
                    
                    # Create or update entry
                    alumni_entry, created = AlumniDirectory.objects.update_or_create(
                        first_name=alumni_data['first_name'],
                        last_name=alumni_data['last_name'],
                        birth_date=alumni_data['birth_date'],
                        defaults=alumni_data
                    )
                    
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 1}: {str(e)}")
                    
            return Response({
                'message': f'Import completed. {success_count} records processed successfully, {error_count} errors.',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10]  # Limit error messages to prevent large responses
            })
            
        except Exception as e:
            logger.error(f"Alumni import error: {str(e)}")
            return Response(
                {'error': f'Import failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CheckAlumniDirectoryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AlumniDirectoryCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'exists': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
