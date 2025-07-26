# 🎓 Alumni Management System

A full-stack alumni management system using Django for the backend and Vue.js for the frontend.

To set up and run this project, just follow the steps below — everything is here in one place.

```

cd Frontend
npm install
npm install @eslint/js\@9.28.0 @vitejs/plugin-vue\@5.2.4 axios\@1.9.0 eslint-plugin-vue\@10.0.1 eslint\@9.28.0 globals\@16.2.0 lucide-vue-next\@0.514.0 pinia-plugin-persistedstate\@4.3.0 pinia\@3.0.3 vite-plugin-vue-devtools\@7.7.6 vite\@6.3.5 vue-router\@4.5.1 vue\@3.5.16
npm install tailwindcss @tailwindcss/vite
npm run build
npm run dev

```

Open a new terminal and run the backend:

```

cd Backend
python -m venv env
source venv/Scripts/activate
pip install -r requirements.txt


```
make a db in your postgres example "alumni_syste"
configure backend in .env
example: 
# Django Settings
SECRET_KEY=***"in your settings.py"**
DEBUG=True

# Database Settings
DB_NAME=alumni_system
DB_USER=postgres
DB_PASSWORD=1031
DB_HOST=localhost
DB_PORT=5432

# Redis Settings
export REDIS_URL=redis://:foobared@127.0.0.1:6379/0
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
export REDIS_PASSWORD=foobared
export REDIS_USE_SSL=False

# Email Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=**youremail**
EMAIL_HOST_PASSWORD=**yourapppassowrd Go to https://myaccount.google.com/security***
DEFAULT_FROM_EMAIL=**youremail**

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:8000,http://localhost:8080,http://localhost:5173


```

python mange.py makemigrations
python mange.py migrate


```

in postgres:
insert this for the Alumni Directory:
INSERT INTO auth_app_alumnidirectory 
(first_name, middle_name, last_name, birth_date, school_id, program, year_graduated, gender)
VALUES 
('John', 'Michael', 'Doe', '1995-05-15', '221-00001', 'Computer Science', 2018, 'male');


```

daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application

```



Frontend will run at:  
`http://localhost:5173`

Backend will run at:  
`http://127.0.0.1:8000`


<!-- # Import the necessary models
from auth_app.models import CustomUser
from django.contrib.auth.hashers import make_password

# 1. Create Super Admin (user 3)
superadmin = CustomUser.objects.create(
    username='johnantigo',
    email='johnantigo@example.com',
    password=make_password('!John2004'),
    first_name='John',
    middle_name='Diaz',
    last_name='Antigo',
    user_type=1,  # 1 = Super Admin
    is_staff=True,
    is_superuser=True,
    is_approved=True,
    school_id='221-00003',
    program='BS in Computer Science',
    year_graduated=2020,
    gender='male'
)

# 2. Create Admin (user 2)
admin = CustomUser.objects.create(
    username='shainasumanda',
    email='shainasumanda@example.com',
    password=make_password('!Shaina2003'),
    first_name='Shaina',
    middle_name='Mortiz',
    last_name='Sumanda',
    user_type=2,  # 2 = Admin
    is_staff=True,
    is_superuser=False,
    is_approved=True,
    school_id='221-00002',
    program='BS in Computer Science',
    year_graduated=2019,
    gender='female'
)

# 3. Create Regular User (user 1)
user = CustomUser.objects.create(
    username='kianmabandos',
    email='kianmabandos@example.com',
    password=make_password('!Kian2009'),
    first_name='Kian',
    middle_name='Carangue',
    last_name='Mabandos',
    user_type=3,  # 3 = Alumni
    is_staff=False,
    is_superuser=False,
    is_approved=True,
    school_id='221-00001',
    program='BS in Computer Science',
    year_graduated=2018,
    gender='male'
)

# Verify the users were created
print(f"Created users: {CustomUser.objects.count()}")



 -->
