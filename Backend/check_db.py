from django.conf import settings

db_config = settings.DATABASES['default']
print(f"Current Database Configuration:")
print(f"  Engine: {db_config.get('ENGINE')}")
print(f"  Name: {db_config.get('NAME')}")
print(f"  User: {db_config.get('USER')}")
print(f"  Host: {db_config.get('HOST')}")
print(f"  Port: {db_config.get('PORT')}")
