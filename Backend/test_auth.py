from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

# Test authentication with email (correct method)
email = 'superadmin@alumni.system'
password = 'Admin@123'
user = authenticate(username=email, password=password)

print('=== AUTHENTICATION TEST ===')
print(f'Email: {email}')
print(f'Password: {password}')
print(f'Authentication Result: {"SUCCESS" if user else "FAILED"}')

if user:
    print(f'User Type: {user.get_user_type_display()}')
    print(f'Is Staff: {user.is_staff}')
    print(f'Is Superuser: {user.is_superuser}')
    print(f'Is Approved: {user.is_approved}')
    print(f'Email Field: {user.email}')
    print(f'Username Field: {user.username}')
else:
    print('Authentication failed - check credentials or password requirements')

print('========================')
