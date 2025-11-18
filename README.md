# 🎓 Alumni Management System

A **full-stack alumni management system** built with **Django (Backend)** and **Vue.js (Frontend)**.

This guide provides a complete setup process for both backend and frontend environments.

---

## 🚀 Project Setup

### ⚙️ Frontend Setup  Backend Setup (Django)

cd Backend
python -m venv env
source env/Scripts/activate  # On Windows PowerShell use: env\Scripts\activate
pip install django




CREATE DATABASE alumni_system;
# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True

# Database Settings
DB_NAME=alumni_system
DB_USER=postgres
DB_PASSWORD=1031
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
REDIS_URL=redis://:foobared@127.0.0.1:6379/0
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=foobared
REDIS_USE_SSL=False

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=youremail@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=youremail@gmail.com

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://localhost:8080,http://localhost:5173

python manage.py makemigrations
python manage.py migrate

daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application
python manage.py runserver 0.0.0.0:8000


### ⚙️ Frontend Setup (Vue.js + Vite + TailwindCSS)

```bash
cd Frontend
npm install
npm install @vitejs/plugin-vue@5.2.4 axios@1.9.0 globals@16.2.0 lucide-vue-next@0.514.0 pinia-plugin-persistedstate@4.3.0 pinia@3.0.3 vite-plugin-vue-devtools@7.7.6 vite@6.3.5 vue-router@4.5.1 vue@3.5.16
npm install tailwindcss @tailwindcss/vite
npm install lodash
npm install @heroicons/vue
npm install chart.js vue-chartjs
npm run build
npm run dev
npm run dev -- --host 0.0.0.0

python manage.py create_admin_accounts
python manage.py populate_from_tracer --tracer-file="../tracer.txt"


or you can directly run 

if you are still starting from scratch: setup_and_run_full.bat
if dependencies and directly run the files: run_servers_only.bat