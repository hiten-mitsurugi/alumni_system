import re
from django.core.exceptions import ValidationError

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one capital letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one small letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character.")

    def get_help_text(self):
        return "Password must contain at least one capital letter, one small letter, one number, and one special character."