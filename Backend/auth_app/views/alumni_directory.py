from .base import *


class CheckAlumniDirectoryView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AlumniDirectoryCheckSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'exists': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            
            # Valid programs (from your model)
            valid_programs = [
                'BA in Sociology',
                'Bachelor of Agricultural Technology',
                'Bachelor of Elementary Education',
                'Bachelor of Secondary Education Major in English',
                'Bachelor of Secondary Education Major in Filipino',
                'Bachelor of Secondary Education Major in Mathematics',
                'Bachelor of Secondary Education Major in Science',
                'BS in Agroforestry',
                'BS in Agricultural and Biosystems Engineering',
                'BS in Agriculture',
                'BS in Agriculture, Major in Agribusiness Management',
                'BS in Agriculture, Major in Agricultural Economics',
                'BS in Agriculture, Major in Agronomy',
                'BS in Agriculture, Major in Animal Science',
                'BS in Agriculture, Major in Crop Protection',
                'BS in Agriculture, Major in Horticulture',
                'BS in Agriculture, Major in Soil Science',
                'BS in Applied Mathematics',
                'BS in Biology',
                'BS in Chemistry',
                'BS in Civil Engineering',
                'BS in Computer Science',
                'BS in Electronics Engineering',
                'BS in Environmental Science',
                'BS in Forestry',
                'BS in Geodetic Engineering',
                'BS in Geology',
                'BS in Information Systems',
                'BS in Information Technology',
                'BS in Mathematics',
                'BS in Mining Engineering',
                'BS in Physics',
                'BS in Psychology',
                'BS in Social Work'
            ]
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Clean and validate data
                        first_name = str(row['first_name']).strip()
                        middle_name = str(row.get('middle_name', '')).strip() if pd.notna(row.get('middle_name', '')) else ''
                        last_name = str(row['last_name']).strip()
                        program = str(row['program']).strip()
                        sex = str(row['sex']).strip().lower()
                        
                        # Validate required fields
                        if not first_name or not last_name:
                            errors.append(f'Row {index + 2}: Missing required fields')
                            error_count += 1
                            continue
                        
                        # Validate program
                        if program not in valid_programs:
                            errors.append(f'Row {index + 2}: Invalid program "{program}"')
                            error_count += 1
                            continue
                        
                        # Validate sex
                        if sex not in ['male', 'female', 'prefer_not_to_say']:
                            errors.append(f'Row {index + 2}: Sex must be male, female, or prefer_not_to_say')
                            error_count += 1
                            continue
                        
                        # Parse birth_date
                        try:
                            if pd.notna(row['birth_date']):
                                birth_date = pd.to_datetime(row['birth_date']).date()
                            else:
                                errors.append(f'Row {index + 2}: Birth date is required')
                                error_count += 1
                                continue
                        except:
                            errors.append(f'Row {index + 2}: Invalid birth date format')
                            error_count += 1
                            continue
                        
                        # Parse year_graduated
                        try:
                            year_graduated = int(row['year_graduated'])
                            if year_graduated < 1900 or year_graduated > 2030:
                                errors.append(f'Row {index + 2}: Year graduated must be between 1900 and 2030')
                                error_count += 1
                                continue
                        except:
                            errors.append(f'Row {index + 2}: Invalid year graduated')
                            error_count += 1
                            continue
                        
                        # Check for duplicates by combination of fields (since school_id is removed)
                        if AlumniDirectory.objects.filter(
                            first_name__iexact=first_name,
                            last_name__iexact=last_name,
                            birth_date=birth_date,
                            program__iexact=program,
                            year_graduated=year_graduated
                        ).exists():
                            errors.append(f'Row {index + 2}: Alumni record with same details already exists')
                            error_count += 1
                            continue
                        
                        # Create alumni record
                        AlumniDirectory.objects.create(
                            first_name=first_name,
                            middle_name=middle_name,
                            last_name=last_name,
                            birth_date=birth_date,
                            program=program,
                            year_graduated=year_graduated,
                            sex=sex
                        )
                        
                        success_count += 1
                        
                    except Exception as e:
                        errors.append(f'Row {index + 2}: {str(e)}')
                        error_count += 1
            
            return Response({
                'message': 'Import completed',
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors[:10],  # Limit to first 10 errors
                'total_errors': len(errors)
            })
            
        except Exception as e:
            logger.error(f"Alumni import error: {str(e)}")
            return Response(
                {'error': f'Import failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )