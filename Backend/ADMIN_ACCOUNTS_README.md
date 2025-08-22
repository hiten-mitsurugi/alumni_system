# Alumni System - Administrative Account Management

This document explains how to create and manage administrative accounts in the Alumni System.

## 🚀 Quick Start

### Create Default Admin Accounts
```bash
# Create superadmin and admin accounts with secure defaults
python manage.py create_admin_accounts

# Force recreate accounts if they already exist  
python manage.py create_admin_accounts --force

# Custom passwords and usernames (password must meet requirements)
python manage.py create_admin_accounts --superadmin-username mysuperadmin --admin-username myadmin --password "MySecure@123"
```

**Login Credentials Created:**
- 📧 **Super Admin**: `superadmin@alumni.system` / `Admin@123`
- 📧 **Admin**: `admin@alumni.system` / `Admin@123`

### Initialize Complete System
```bash
# Create admin accounts + sample data
python manage.py init_system

# Create only admin accounts (skip sample alumni)
python manage.py init_system --skip-alumni

# Force recreate everything
python manage.py init_system --force
```

## 📋 Account Management Commands

### List All Administrative Accounts
```bash
# Show only admin accounts
python manage.py list_admin_accounts

# Show all users including alumni
python manage.py list_admin_accounts --all
```

### Reset Admin Passwords
```bash
# Reset password (will prompt for password)
python manage.py admin_password --username superadmin

# Reset with specific password
python manage.py admin_password --username admin --password newpassword123
```

### Create New Admin Accounts
```bash
# Create new admin account
python manage.py admin_password --username newadmin --password admin123 --create

# Create new superuser account
python manage.py admin_password --username newsuperadmin --password admin123 --create --superuser
```

## 🔐 Default Accounts Created

After running `create_admin_accounts`, you'll have:

| Account Type | Email (for login) | Username | Password | Permissions |
|-------------|------------------|----------|----------|------------|
| Super Admin | superadmin@alumni.system | superadmin | Admin@123 | Full system access |
| Admin | admin@alumni.system | admin | Admin@123 | Admin panel access |

## 🚨 IMPORTANT: Authentication Method

**The system uses EMAIL + PASSWORD for login, NOT username + password!**

- ✅ **Correct Login**: Use `superadmin@alumni.system` + `Admin@123`  
- ❌ **Wrong Login**: Using `superadmin` + `Admin@123` will fail

## 🔒 Password Requirements

All passwords must meet these requirements:
- ✅ **Minimum 8 characters**
- ✅ **At least one uppercase letter** (A-Z)
- ✅ **At least one lowercase letter** (a-z)  
- ✅ **At least one number** (0-9)
- ✅ **At least one special character** (!@#$%^&*(),.?":{}|<>)

**Default password `Admin@123` meets all requirements.**

## 🛡️ User Type Levels

The system uses exactly 3 user types as defined in the model:

- **Level 1 (Super Admin)**: 👑 Full system control, can manage everything
- **Level 2 (Admin)**: 🛡️ Administrative access, can manage users and content  
- **Level 3 (Alumni)**: 🎓 Regular users, can use the alumni features

## 🔧 Technical Details

### School ID Format
- **Admin accounts**: `ADM{user_type}{random_4_digits}` (e.g., ADM11234, ADM22567)
- **Alumni accounts**: `ALM{random_5_digits}` (e.g., ALM12345)

### Required Fields
All accounts are created with default values for required fields:
- Birth date: 1990-01-01
- Program: Administration (for admin accounts)
- Contact number: Auto-generated
- Addresses: Default values
- Parents info: Default values

### Account Features
- ✅ Automatically approved and activated
- 📧 Email format: `{username}@alumni.system`
- 🔐 Profile created with online status
- 📊 Ready for immediate use

## 🚨 Security Notes

1. **Change default passwords** immediately in production
2. **Use strong passwords** for all administrative accounts
3. **Limit superadmin accounts** to only necessary personnel
4. **Regular password rotation** is recommended
5. **Monitor admin account access** through logs

## 📖 Usage Examples

### Development Setup
```bash
# Quick development setup
python manage.py init_system --skip-alumni
python manage.py runserver
```

### Production Setup
```bash
# Create admin accounts with custom credentials
python manage.py create_admin_accounts --password YOUR_SECURE_PASSWORD
# Change passwords immediately after first login
```

### Adding New Admin
```bash
# Create new content moderator
python manage.py admin_password --username content_mod --password secure123 --create

# Create new super admin
python manage.py admin_password --username backup_admin --password secure123 --create --superuser
```

## 🔍 Troubleshooting

### Account Already Exists
```bash
# Use --force to recreate
python manage.py create_admin_accounts --force
```

### Password Reset Not Working
```bash
# Verify username exists first
python manage.py list_admin_accounts
# Then reset
python manage.py admin_password --username correct_username --password newpassword
```

### Permission Issues
- Ensure the account has `is_staff=True` for admin panel access
- Superusers need `is_superuser=True` for full access
- Check `user_type` level (1 for Super Admin, 2 for Admin)

## 📝 Command Reference

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `create_admin_accounts` | Create basic admin accounts | `--force`, `--password` |
| `init_system` | Full system initialization | `--skip-alumni`, `--force` |
| `list_admin_accounts` | List admin accounts | `--all` |
| `admin_password` | Password management | `--create`, `--superuser` |

---

**Note**: Always test these commands in a development environment first before using in production!
