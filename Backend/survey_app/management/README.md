# Survey App Management Commands

This directory contains Django management commands for the survey app.

## Available Commands

### populate_surveys.py
Populates the database with comprehensive Alumni Tracer Survey questions.

**Usage:**
```bash
python manage.py populate_surveys
```

**Options:**
- `--admin-email`: Email of the admin user who will be set as creator (default: admin@example.com)

**What it creates:**
- 7 survey categories with comprehensive questions
- Questions covering all aspects of alumni tracking:
  - Personal Information
  - Educational Background
  - Employment History
  - Skills Assessment
  - Curriculum Feedback
  - Further Studies
  - Feedback and Suggestions

**Example:**
```bash
python manage.py populate_surveys --admin-email="admin@university.edu"
```

## Notes
- The command will create a default admin user if none exists
- Questions are based on standard alumni tracer study practices
- All questions include proper validation and help text
- The system supports 11 question types for maximum flexibility
