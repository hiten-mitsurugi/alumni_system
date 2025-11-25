#!/usr/bin/env python
"""
Script to analyze the impact of changing privacy defaults
Run this BEFORE making any changes to understand current state
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import FieldPrivacySetting, Profile, CustomUser

print("=" * 70)
print("PRIVACY SETTINGS IMPACT ANALYSIS")
print("=" * 70)

# Check FieldPrivacySetting records
print("\n1. FIELD PRIVACY SETTINGS")
print("-" * 70)
total_field_settings = FieldPrivacySetting.objects.count()
print(f"Total FieldPrivacySetting records: {total_field_settings}")

if total_field_settings > 0:
    print("\nVisibility distribution:")
    for vis in ['everyone', 'connections_only', 'only_me']:
        count = FieldPrivacySetting.objects.filter(visibility=vis).count()
        percentage = (count / total_field_settings * 100) if total_field_settings > 0 else 0
        print(f"  {vis:20s}: {count:4d} ({percentage:5.1f}%)")
    
    # Show sample records
    print("\nSample records (first 5):")
    for setting in FieldPrivacySetting.objects.all()[:5]:
        print(f"  User {setting.user.id} ({setting.user.username}): {setting.field_name} = {setting.visibility}")
else:
    print("  ⚠️  NO EXPLICIT FIELD PRIVACY SETTINGS FOUND")
    print("  ⚠️  This means ALL fields use the default fallback value")
    print("  ⚠️  Current default: 'connections_only' (will change to 'everyone')")

# Check Profile visibility settings
print("\n2. PROFILE VISIBILITY SETTINGS")
print("-" * 70)
total_profiles = Profile.objects.count()
print(f"Total Profile records: {total_profiles}")

if total_profiles > 0:
    print("\nProfile visibility distribution:")
    for vis in ['public', 'connections_only', 'private']:
        count = Profile.objects.filter(profile_visibility=vis).count()
        percentage = (count / total_profiles * 100) if total_profiles > 0 else 0
        print(f"  {vis:20s}: {count:4d} ({percentage:5.1f}%)")
else:
    print("  ⚠️  NO PROFILES FOUND")

# Check users without explicit privacy settings
print("\n3. USERS WITHOUT EXPLICIT PRIVACY SETTINGS")
print("-" * 70)
total_users = CustomUser.objects.filter(user_type=3, is_approved=True).count()
users_with_settings = FieldPrivacySetting.objects.values('user').distinct().count()
users_without_settings = total_users - users_with_settings

print(f"Total approved alumni: {total_users}")
print(f"Users WITH explicit field privacy settings: {users_with_settings}")
print(f"Users WITHOUT explicit settings: {users_without_settings}")

if users_without_settings > 0:
    print(f"\n  ⚠️  {users_without_settings} users will be affected by default change")
    print(f"  ⚠️  Their fields currently default to 'connections_only'")
    print(f"  ⚠️  After change, they will default to 'everyone' (public)")

# Impact summary
print("\n" + "=" * 70)
print("IMPACT SUMMARY")
print("=" * 70)

print("\nCHANGES BEING MADE:")
print("  1. Profile.profile_visibility default: 'connections_only' → 'public'")
print("  2. FieldPrivacySetting fallback default: 'connections_only' → 'everyone'")
print("  3. ProfileFieldUpdateSerializer default: 'connections_only' → 'everyone'")

print("\nWHAT WILL BE AFFECTED:")
if total_field_settings == 0:
    print("  ⚠️  ALL USERS - No explicit privacy settings exist")
    print("  ⚠️  All profile fields will become PUBLIC by default")
else:
    print(f"  ✅ {users_with_settings} users have explicit settings (WILL NOT CHANGE)")
    print(f"  ⚠️  {users_without_settings} users have no explicit settings (WILL BECOME PUBLIC)")

print("\nWHAT WILL NOT BE AFFECTED:")
print("  ✅ Users who have explicitly set field privacy to 'only_me'")
print("  ✅ Users who have explicitly set field privacy to 'connections_only'")
print("  ✅ Any FieldPrivacySetting records in database (preserved as-is)")

print("\nRECOMMENDATIONS:")
if users_without_settings > 0 and users_without_settings < 10:
    print("  ✅ Safe to proceed - small number of users affected")
elif users_without_settings >= 10:
    print("  ⚠️  Consider notifying users about the change")
    print("  ⚠️  Or create explicit FieldPrivacySetting records with their preferred visibility")
else:
    print("  ✅ Safe to proceed - all users have explicit privacy settings")

print("\n" + "=" * 70)
print("Run this script again AFTER changes to verify impact")
print("=" * 70)
