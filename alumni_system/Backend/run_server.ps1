# Alumni System Backend Startup Script
Set-Location $PSScriptRoot
.\env\Scripts\Activate.ps1
python manage.py runserver 8000