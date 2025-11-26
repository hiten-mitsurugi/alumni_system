# 🚀 Quick Start - Docker Edition

## For Absolute Beginners

### Step 1: Install Docker Desktop
1. Go to https://www.docker.com/products/docker-desktop/
2. Download for your OS (Windows/Mac/Linux)
3. Install and start Docker Desktop
4. Wait for it to say "Docker is running"

### Step 2: Open Terminal
- **Windows**: PowerShell (right-click Start → Windows PowerShell)
- **Mac/Linux**: Terminal

### Step 3: Navigate to Project
```bash
cd path/to/alumni_system
```

### Step 4: Start Everything (One Command!)
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Wait 1-2 minutes for everything to start...

### Step 5: Setup Database (First Time Only)
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### Step 6: Open Browser
- Frontend: http://localhost:5173
- Admin: http://localhost:8000/admin

## ✅ That's It!

Everything is running:
- ✅ Database (PostgreSQL)
- ✅ Cache (Redis)
- ✅ Backend (Django)
- ✅ Frontend (Vue.js)
- ✅ Background Tasks (Celery)

## 🛑 To Stop
```bash
docker-compose down
```

## 🔄 To Restart
```bash
docker-compose up -d
```

## 📊 Check Status
```bash
docker-compose ps
```

## 📝 View Logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🆘 If Something Goes Wrong
1. Stop everything: `docker-compose down`
2. Remove volumes: `docker-compose down -v`
3. Start fresh: `docker-compose up -d`
4. Check logs: `docker-compose logs`

## 🌐 Access from Phone/Tablet
1. Find your computer's IP:
   - Windows: Run `ipconfig` in PowerShell
   - Mac: Run `ifconfig` in Terminal
   - Look for something like `192.168.1.100`

2. Update `.env` file:
   ```env
   VITE_API_BASE_URL=http://192.168.1.100:8000
   ```

3. Restart:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. Access from phone: http://192.168.1.100:5173

## 💡 Pro Tips
- Frontend code changes = instant reload (HMR)
- Backend code changes = automatic reload
- No need to restart containers when coding
- Database data persists between restarts

## 📚 Need More Help?
Read the full guide: [README_DOCKER.md](./README_DOCKER.md)
