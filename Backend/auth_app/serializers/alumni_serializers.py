"""
Alumni verification and directory serializers.
Contains AlumniDirectoryCheckSerializer for verifying alumni records.
"""
from rest_framework import serializers
from ..models import AlumniDirectory, CustomUser


class AlumniDirectoryCheckSerializer(serializers.Serializer):
    """Serializer for checking and verifying alumni directory records"""
    first_name = serializers.CharField(required=True)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=True)
    program = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=True)
    year_graduated = serializers.IntegerField(required=True)
    sex = serializers.ChoiceField(choices=CustomUser.SEX_CHOICES, required=True)

    def validate_sex(self, value):
        valid_choices = [choice[0] for choice in CustomUser.SEX_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f'"{value}" is not a valid choice.')
        return value

    def validate(self, data):
        try:
            query = {
                'first_name__iexact': data['first_name'],
                'last_name__iexact': data['last_name'],
                'birth_date': data['birth_date'],
                'program__iexact': data['program'],
                'year_graduated': data['year_graduated'],
                'sex__iexact': data['sex']  # Changed to case insensitive
            }
            
            if data.get('middle_name') and data['middle_name'].strip():
                query['middle_name__iexact'] = data['middle_name'].strip()
            else:
                # Check for both null and empty string
                query_null = query.copy()
                query_null['middle_name__isnull'] = True
                query_empty = query.copy()
                query_empty['middle_name__exact'] = ''
                
                # Try both queries
                try:
                    alumni = AlumniDirectory.objects.get(**query_null)
                    return {'exists': True, 'alumni': alumni}
                except AlumniDirectory.DoesNotExist:
                    try:
                        alumni = AlumniDirectory.objects.get(**query_empty)
                        return {'exists': True, 'alumni': alumni}
                    except AlumniDirectory.DoesNotExist:
                        pass
                raise AlumniDirectory.DoesNotExist("No match found for empty/null middle name")
            
            alumni = AlumniDirectory.objects.get(**query)
            return {'exists': True, 'alumni': alumni}
        except AlumniDirectory.DoesNotExist:
            raise serializers.ValidationError("Not an existing alumni. Please contact the Alumni Relations Office.")
