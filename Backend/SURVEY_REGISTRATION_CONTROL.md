# Survey Registration Control Feature

## Overview
This feature allows you to control which survey categories appear on the public registration form. By default, new survey categories are **NOT** included in registration, giving you full control.

## What Changed

### 1. New Field: `include_in_registration`
Every `SurveyCategory` now has a boolean field `include_in_registration`:
- **Default**: `False` (new surveys won't appear in registration)
- **Purpose**: Explicitly control which surveys are part of the registration process

### 2. Updated Registration Endpoint
The public registration endpoint (`/survey/registration-questions/`) now only returns categories where:
- `is_active=True` AND
- `include_in_registration=True`

### 3. Admin Interface
The Django admin now shows the `include_in_registration` toggle:
- **List view**: Shows checkbox status for each category
- **Edit form**: Toggle to include/exclude from registration
- **Filtering**: Filter categories by registration inclusion status

## How to Use

### Creating a New Survey (Not for Registration)
1. Go to Django Admin → Survey Categories → Add Category
2. Fill in name, description, order, etc.
3. **Leave `include_in_registration` unchecked** (default)
4. Set `is_active=True`
5. Save

**Result**: This survey will be available for manual assignment to alumni but won't appear during registration.

### Creating a Registration Survey
1. Go to Django Admin → Survey Categories → Add Category
2. Fill in all fields
3. **Check `include_in_registration`**
4. Set `is_active=True`
5. Save

**Result**: This survey will appear in the public registration form.

### Converting Existing Survey
1. Find the category in Django Admin
2. Edit it
3. Toggle `include_in_registration` as needed
4. Save

### Via API (for frontend admin)
When creating/updating categories via the API:
```json
{
  "name": "Tracer Survey 2025",
  "description": "Annual alumni tracer study",
  "is_active": true,
  "include_in_registration": false,  // Set to true for registration surveys
  "order": 10
}
```

## Migration Notes

### What the Migration Did
The migration automatically:
1. Added the `include_in_registration` field (default `False`)
2. Set `include_in_registration=True` for categories that were previously shown in registration
3. Set `include_in_registration=False` for categories that were previously excluded

### Zero Existing Categories
If you saw "Set include_in_registration=True for 0 existing categories", it means you currently have no survey categories in your database. This is normal for a fresh installation.

## Best Practices

### Tracer Surveys
- Create tracer survey categories with `include_in_registration=False`
- Manually send survey links to alumni
- Track responses separately from registration

### Registration Surveys
- Only include essential categories in registration
- Keep registration surveys short to improve completion rates
- Common registration categories:
  - Educational Background
  - Employment Information
  - Contact Details

### General/Ad-hoc Surveys
- Set `include_in_registration=False`
- Use for specific research, feedback, or time-limited surveys
- Can be activated/deactivated independently of registration

## API Endpoints

### Get Registration Questions (Public)
```
GET /survey/registration-questions/
```
Returns only categories with `include_in_registration=True`

### Get All Active Questions (Authenticated)
```
GET /survey/active-questions/
```
Returns all active categories (for alumni dashboard)

### Admin: Create/Update Category
```
POST/PUT /survey/admin/categories/
{
  "include_in_registration": true/false
}
```

## Frontend Integration

### No Changes Required
The frontend registration component (`RegisterDynamic.vue`) continues to work as before:
- It calls `/survey/registration-questions/`
- The backend now filters categories automatically
- Only intended registration categories are returned

### Admin UI
The frontend admin interface automatically shows the `include_in_registration` toggle when managing categories (no code changes needed, it uses the serializer).

## Tracer Population Script

The `populate_from_tracer.py` management command has been updated to set `include_in_registration=False` for all tracer categories it creates, ensuring tracer surveys don't accidentally appear in registration.

## Troubleshooting

### Category Not Showing in Registration
Check:
1. `is_active=True`
2. `include_in_registration=True`
3. Category has at least one active question

### Category Showing in Registration (Shouldn't Be)
1. Edit the category in admin
2. Uncheck `include_in_registration`
3. Save

### Need to Bulk Update Categories
Use Django shell:
```python
from survey_app.models import SurveyCategory

# Include all active categories in registration
SurveyCategory.objects.filter(is_active=True).update(include_in_registration=True)

# Exclude all tracer categories
SurveyCategory.objects.filter(name__icontains='tracer').update(include_in_registration=False)
```

## Security Notes
- The registration endpoint is public (no authentication required)
- Only include non-sensitive categories in registration
- Admin-only categories should have `include_in_registration=False`
- Sensitive alumni data should be collected post-registration

## Future Enhancements
Consider these potential improvements:
- Survey templates with predefined category groups
- Scheduled survey activation/deactivation
- Multiple registration templates for different programs
- Survey versioning and historical tracking
