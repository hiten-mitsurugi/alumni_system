# 🐳 Alumni System - Docker Setup Guide

## 📋 Quick Start

### Prerequisites
- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop/))
- Git (for cloning the repository)
- 8GB RAM minimum, 16GB recommended
- 20GB free disk space

### One-Command Setup

**Development Mode** (with hot reload):
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Production Mode**:
```bash
docker-compose up -d
```

**Access the Application**:
- Frontend: http://localhost:5173 (dev) or http://localhost (prod)
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

---

## 🎯 What's Included

### 6 Docker Containers

1. **PostgreSQL** - Database (port 5432)
2. **Redis** - Cache & Message Broker (port 6379)
3. **Backend** - Django + Channels + Daphne (port 8000)
4. **Celery** - Background task worker
5. **Frontend** - Vue.js + Vite (port 5173/80)
6. **Nginx** - Reverse proxy (production only)

---

## 🚀 Setup Instructions

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/alumni_system.git
cd alumni_system
```

### Step 2: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and update these values:
# - POSTGRES_PASSWORD (use a strong password)
# - SECRET_KEY (generate a new one)
# - EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
```

### Step 3: Start Services

**For Development**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**For Production**:
```bash
docker-compose up -d
```

### Step 4: Initialize Database
```bash
# Wait for containers to be healthy (30-60 seconds)
docker-compose ps

# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Load sample data (optional)
docker-compose exec backend python manage.py loaddata sample_data.json
```

### Step 5: Access Application
- **Frontend**: http://localhost:5173 (dev) or http://localhost (prod)
- **Backend Admin**: http://localhost:8000/admin/
- **API Docs**: http://localhost:8000/api/

---

## 📁 Project Structure

```
alumni_system/
├── docker-compose.yml          # Main orchestration
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.prod.yml     # Production overrides
├── .env                        # Environment variables
├── .dockerignore               # Exclude from builds
│
├── Backend/
│   ├── Dockerfile              # Production backend
│   ├── Dockerfile.dev          # Development backend
│   ├── entrypoint.sh           # Startup script
│   └── .dockerignore
│
├── Frontend/
│   ├── Dockerfile              # Production frontend
│   ├── Dockerfile.dev          # Development frontend
│   ├── nginx.conf              # Nginx config
│   └── .dockerignore
│
└── nginx/
    ├── nginx.conf              # Main Nginx config
    └── default.conf            # Routing rules
```

---

## 🛠️ Common Commands

### Container Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check status
docker-compose ps
```

### Development Workflow
```bash
# Backend - Run migrations
docker-compose exec backend python manage.py migrate

# Backend - Create superuser
docker-compose exec backend python manage.py createsuperuser

# Backend - Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Backend - Django shell
docker-compose exec backend python manage.py shell

# Frontend - Install new package
docker-compose exec frontend npm install package-name

# Database - Access PostgreSQL
docker-compose exec postgres psql -U postgres -d thesis_db

# Redis - Access Redis CLI
docker-compose exec redis redis-cli
```

### Rebuilding
```bash
# Rebuild specific service
docker-compose build backend

# Rebuild all services
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

### Clean Up
```bash
# Stop and remove containers (keeps volumes)
docker-compose down

# Remove containers and volumes (fresh start)
docker-compose down -v

# Remove unused images
docker image prune -a
```

---

## 🔧 Configuration

### Environment Variables

**Database**:
- `POSTGRES_DB` - Database name (default: thesis_db)
- `POSTGRES_USER` - Database user (default: postgres)
- `POSTGRES_PASSWORD` - Database password
- `DB_HOST` - Database host (default: postgres)
- `DB_PORT` - Database port (default: 5432)

**Django**:
- `SECRET_KEY` - Django secret key (required)
- `DEBUG` - Debug mode (default: False)
- `ALLOWED_HOSTS` - Allowed hosts (default: localhost,127.0.0.1)
- `CORS_ALLOWED_ORIGINS` - CORS origins (default: *)

**Redis**:
- `REDIS_HOST` - Redis host (default: redis)
- `REDIS_PORT` - Redis port (default: 6379)
- `REDIS_PASSWORD` - Redis password (optional)

**Frontend**:
- `VITE_API_BASE_URL` - Backend URL (default: http://localhost:8000)
- `VITE_API_URL` - API URL (default: http://localhost:8000/api)
- `VITE_WS_URL` - WebSocket URL (default: ws://localhost:8000/ws/notifications/)

**Email**:
- `EMAIL_HOST` - SMTP server (default: smtp.gmail.com)
- `EMAIL_PORT` - SMTP port (default: 587)
- `EMAIL_HOST_USER` - Email address
- `EMAIL_HOST_PASSWORD` - Email password or app password

---

## 🌐 Accessing from Other Devices (LAN)

### Step 1: Find Your IP Address

**Windows**:
```bash
ipconfig
# Look for IPv4 Address (e.g., 192.168.1.100)
```

**macOS/Linux**:
```bash
ifconfig
# or
ip addr show
```

### Step 2: Update Environment Variables
```env
# In .env file, update these:
VITE_API_BASE_URL=http://YOUR_IP_ADDRESS:8000
VITE_API_URL=http://YOUR_IP_ADDRESS:8000/api
VITE_WS_URL=ws://YOUR_IP_ADDRESS:8000/ws/notifications/
```

### Step 3: Restart Containers
```bash
docker-compose down
docker-compose up -d
```

### Step 4: Access from Other Devices
From mobile or other computers on the same network:
- Frontend: http://YOUR_IP_ADDRESS:5173 (dev) or http://YOUR_IP_ADDRESS (prod)
- Backend: http://YOUR_IP_ADDRESS:8000

---

## 🐛 Troubleshooting

### Containers Won't Start

**Check logs**:
```bash
docker-compose logs backend
docker-compose logs postgres
```

**Common issues**:
- Port already in use: Stop existing services or change ports
- Insufficient memory: Allocate more RAM to Docker Desktop
- Database not ready: Wait 30 seconds and retry

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Verify environment variables
docker-compose exec backend env | grep DB_

# Test database connection
docker-compose exec backend python manage.py dbshell
```

### WebSocket Not Working

**Check backend is running**:
```bash
docker-compose logs backend | grep -i websocket
```

**Verify WebSocket URL**:
- Development: `ws://localhost:8000/ws/notifications/`
- Production: Use your server's domain/IP

**Check browser console** for WebSocket connection errors

### Frontend Not Loading

```bash
# Check if frontend container is running
docker-compose ps frontend

# View frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### File Upload Issues

```bash
# Check media volume permissions
docker-compose exec backend ls -la /app/media

# Recreate media volume
docker-compose down -v
docker volume create alumni_system_media_files
docker-compose up -d
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Check backend can connect to Redis
docker-compose exec backend python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"
```

---

## 🔒 Security Best Practices

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY` (generate new one)
- [ ] Use strong `POSTGRES_PASSWORD`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Set up SSL/HTTPS (use Let's Encrypt)
- [ ] Configure firewall rules
- [ ] Enable Redis password
- [ ] Regular backups of volumes
- [ ] Keep Docker images updated

### Generate Secure Keys
```bash
# Generate Django SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate random password
openssl rand -base64 32
```

---

## 📊 Monitoring

### Health Checks
```bash
# Check all services
docker-compose ps

# Backend health
curl http://localhost:8000/api/

# Frontend health
curl http://localhost:5173/

# Database health
docker-compose exec postgres pg_isready -U postgres

# Redis health
docker-compose exec redis redis-cli ping
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend

# With timestamps
docker-compose logs -f -t backend
```

### Resource Usage
```bash
# View container stats
docker stats

# View disk usage
docker system df

# View volume sizes
docker volume ls
```

---

## 🔄 Backup & Restore

### Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres thesis_db > backup_$(date +%Y%m%d).sql

# Or using docker cp
docker-compose exec -T postgres pg_dump -U postgres thesis_db > backup.sql
```

### Restore Database
```bash
# Restore from backup
docker-compose exec -T postgres psql -U postgres thesis_db < backup.sql
```

### Backup Volumes
```bash
# Backup media files
docker run --rm -v alumni_system_media_files:/data -v $(pwd):/backup alpine tar czf /backup/media_backup.tar.gz /data

# Restore media files
docker run --rm -v alumni_system_media_files:/data -v $(pwd):/backup alpine tar xzf /backup/media_backup.tar.gz -C /
```

---

## 🚀 Deployment

### Deploy to Production Server

1. **Copy files to server**:
```bash
scp -r alumni_system user@server:/var/www/
```

2. **SSH to server**:
```bash
ssh user@server
cd /var/www/alumni_system
```

3. **Configure environment**:
```bash
cp .env.example .env
nano .env  # Update production values
```

4. **Start services**:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

5. **Initialize database**:
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --noinput
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

## ❓ FAQ

### Q: Do I need to install Python, Node.js, PostgreSQL, Redis?
**A**: No! Docker handles all dependencies. Just install Docker Desktop.

### Q: Will this work on Windows/Mac/Linux?
**A**: Yes! Docker works on all platforms.

### Q: Can I still develop without Docker?
**A**: Yes! The existing setup still works. Docker is optional but recommended.

### Q: How do I update the code?
**A**: Just edit files normally. Development mode has hot reload.

### Q: Where are my files stored?
**A**: Database and media files are in Docker volumes. Use `docker volume ls` to see them.

### Q: How do I stop everything?
**A**: Run `docker-compose down`

### Q: How much disk space does Docker use?
**A**: Around 2-5GB for images, plus your data in volumes.

---

## 🎓 What Changed vs Original Setup?

### Before Docker:
- ❌ Manual PostgreSQL installation
- ❌ Manual Redis installation
- ❌ Python virtual environment setup
- ❌ Node.js installation
- ❌ Multiple terminal windows
- ❌ Platform-specific scripts (.bat for Windows)

### With Docker:
- ✅ Everything automated
- ✅ One command to start
- ✅ Works on any platform
- ✅ Isolated environments
- ✅ Easy to deploy
- ✅ Professional setup

### UI/UX Changes:
- ✅ **NO CHANGES!** Everything looks and works exactly the same
- ✅ All features work identically
- ✅ Same URLs (localhost:5173, localhost:8000)
- ✅ Same login, messaging, notifications, etc.

---

**🎉 Congratulations! Your Alumni System is now containerized!**

For questions or issues, refer to the troubleshooting section or check container logs.
