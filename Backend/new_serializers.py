class FieldPrivacySettingSerializer(serializers.ModelSerializer):
    """Serializer for field privacy settings"""
    class Meta:
        model = FieldPrivacySetting
        fields = ['field_name', 'visibility']
        
    def validate_visibility(self, value):
        """Validate visibility choices"""
        valid_choices = [choice[0] for choice in FieldPrivacySetting.VISIBILITY_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f'"{value}" is not a valid visibility choice.')
        return value


class ProfileFieldUpdateSerializer(serializers.Serializer):
    """Serializer for updating individual profile fields"""
    field_name = serializers.CharField(max_length=100)
    field_value = serializers.CharField(allow_blank=True, allow_null=True, required=False)
    visibility = serializers.ChoiceField(
        choices=FieldPrivacySetting.VISIBILITY_CHOICES, 
        required=False,
        default='alumni_only'
    )