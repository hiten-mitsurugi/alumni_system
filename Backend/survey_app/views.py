"""
Survey App Views - Modularized Structure
=========================================
This file serves as a backward-compatibility redirect.
All views have been modularized into the 'views/' directory for better organization.

Original 2,744-line file has been split into 5 focused modules:
- views/utils.py          : Helper functions (53 lines)
- views/admin_views.py    : Admin CRUD operations (242 lines)
- views/alumni_views.py   : Alumni-facing views (307 lines)
- views/analytics_views.py: Analytics & reporting (541 lines)
- views/export_views.py   : Excel & PDF exports (721 lines)

Import all views from the modular structure to maintain existing URL patterns.
"""

# Import all views from the modular structure
from .views import *

# This ensures all view classes and functions remain accessible
# exactly as they were before modularization, maintaining 100% backward compatibility.
# Django's URL routing will continue to work without any changes.
