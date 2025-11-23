# Alumni System - Railway Deployment Guide

This guide will walk you through deploying your alumni system on Railway with automatic service detection and built-in database support.

## Prerequisites

1. **GitHub Repository**: Ensure your code is pushed to GitHub
2. **Railway Account**: Sign up at [railway.app](https://railway.app)
3. **Database**: We'll set up PostgreSQL on Railway
4. **Redis**: Railway provides built-in Redis support

## Overview

Your alumni system will be deployed as:
- **Frontend**: Vue.js application (automatically detected)
- **Backend**: Django REST API (automatically detected)
- **Database**: PostgreSQL database
- **Cache/Sessions**: Railway Redis instance

---

## Step 1: Create Railway Project

1. **Login to Railway Dashboard**
   - Go to [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"

2. **Connect GitHub Repository**
   - Select your `alumni_system` repository
   - Railway will automatically detect both Frontend and Backend services
   - Click "Deploy Now"

3. **Railway Auto-Detection**
   - Railway automatically detects:
     - Django backend (from `requirements.txt` and `manage.py`)
     - Vue.js frontend (from `package.json`)
   - Both services will be created automatically

---

## Step 2: Add Database and Redis

1. **Add PostgreSQL Database**
   - In your Railway project dashboard
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway automatically creates and configures the database
   - Database variables are automatically added to your services

2. **Add Redis (Optional)**
   - Click "+ New" → "Database" → "Add Redis"
   - Railway automatically configures Redis connection
   - Redis variables are automatically available to your services

3. **Connection Details**
   - Railway automatically provides environment variables:
     - `DATABASE_URL`: PostgreSQL connection string
     - `REDIS_URL`: Redis connection string (if added)

---

## Step 3: Configure Backend Service

1. **Access Backend Service**
   - Railway automatically created your backend service
   - Click on the Django service in your project dashboard
   - Railway automatically detects it's a Django app

2. **Configure Backend Settings**
   - Railway automatically sets:
     - **Root Directory**: `Backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: Railway detects from `start.sh` or uses default Django commands
   - **Branch**: Defaults to your main branch

3. **Set Environment Variables**
   Click "Variables" tab and add these variables:

   ```bash
   # Django Settings
   DJANGO_SETTINGS_MODULE=alumni_system.settings
   DEBUG=False
   
   # Security
   SECRET_KEY=your-super-secret-django-key-here-make-it-long-and-random
   
   # JWT Settings
   JWT_SECRET_KEY=another-secret-key-for-jwt-tokens
   
   # File Storage
   USE_S3=False
   
   # Email Settings (optional)
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

   **Note**: `DATABASE_URL`, `REDIS_URL`, and `ALLOWED_HOSTS` are automatically configured by Railway!

4. **Backend Deployment**
   - Railway automatically deploys on every push to your repository
   - Monitor the build logs in the Railway dashboard
   - Note your backend URL: `https://your-backend-service.railway.app`

---

## Step 4: Configure Frontend Service

1. **Access Frontend Service**
   - Railway automatically created your frontend service
   - Click on the Vue.js service in your project dashboard
   - Railway automatically detects it's a Node.js/Vue application

2. **Configure Frontend Settings**
   - Railway automatically sets:
     - **Root Directory**: `Frontend`
     - **Build Command**: `npm ci && npm run build`
     - **Start Command**: `npm run start` or serves the built files
   - **Branch**: Defaults to your main branch

3. **Set Environment Variables**
   Click "Variables" tab and add:

   ```bash
   # Backend API URL (use your backend service URL)
   VITE_API_BASE_URL=${{Django.RAILWAY_PUBLIC_DOMAIN}}
   
   # Node version (optional)
   NODE_VERSION=18
   ```

   **Note**: Railway's `${{Django.RAILWAY_PUBLIC_DOMAIN}}` automatically references your backend service URL!

4. **Frontend Deployment**
   - Railway automatically builds and deploys your frontend
   - Monitor the build logs for any errors
   - Note your frontend URL: `https://your-frontend-service.railway.app`

---

## Step 5: Configure Service Communication

1. **Update Backend Environment Variables**
   - Go to your Django service → "Variables" tab
   - Add the `CORS_ALLOWED_ORIGINS` variable:
   ```bash
   CORS_ALLOWED_ORIGINS=${{Frontend.RAILWAY_PUBLIC_DOMAIN}},http://localhost:3000
   ```

2. **Railway Auto-Configuration**
   - Railway automatically configures `ALLOWED_HOSTS` to include your service domain
   - No manual `ALLOWED_HOSTS` configuration needed!
   - Railway's internal networking handles service-to-service communication

3. **Automatic Redeployment**
   - Railway automatically redeploys when environment variables change
   - Services can reference each other using Railway's variable system

---

## Step 6: Initialize Database

1. **Access Railway Terminal**
   - Go to your Django service dashboard
   - Click "Connect" → "Terminal" to open Railway's web terminal
   - Or use Railway CLI: `railway connect` then `railway shell`

2. **Run Migrations**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

3. **Create Superuser** (Optional)
   ```bash
   python manage.py createsuperuser
   ```

4. **Load Sample Data** (Optional)
   If you have fixtures or sample data:
   ```bash
   python manage.py loaddata your_fixture_file.json
   ```

**Note**: Railway automatically runs these commands if you add them to a `railway.toml` file or startup script!

---

## Step 7: Test Your Deployment

1. **Test Backend API**
   - Visit: `https://your-django-service.railway.app/admin/` for Django admin
   - Or test your API endpoints: `https://your-django-service.railway.app/api/`

2. **Test Frontend**
   - Visit: `https://your-frontend-service.railway.app`
   - Try logging in and using the application features

3. **Test Integration**
   - Verify that frontend can communicate with backend
   - Check browser developer tools for any CORS or API errors
   - Railway's automatic service discovery should handle internal communication

4. **Check Service Logs**
   - Click on each service in Railway dashboard to view real-time logs
   - Monitor for any startup errors or runtime issues

---

## Step 8: Configure Custom Domain (Optional)

1. **Backend Custom Domain**
   - In Django service → "Settings" → "Domains"
   - Click "+ Custom Domain"
   - Add your domain (e.g., `api.youralumni.com`)
   - Configure your DNS provider with Railway's CNAME

2. **Frontend Custom Domain**
   - In Frontend service → "Settings" → "Domains"
   - Click "+ Custom Domain"
   - Add your domain (e.g., `youralumni.com`)
   - Configure your DNS provider with Railway's CNAME

3. **Update Environment Variables**
   - Update `CORS_ALLOWED_ORIGINS` with your new frontend domain
   - Update `VITE_API_BASE_URL` with your new backend domain
   - Railway automatically handles SSL certificates for custom domains!

---

## Troubleshooting

### Common Issues and Solutions

1. **Build Failures**
   ```bash
   # Check build logs in Railway dashboard
   # Ensure all dependencies are in requirements.txt (Backend) or package.json (Frontend)
   # Verify Python/Node versions in railway.toml or environment variables
   # Railway auto-detects most configurations
   ```

2. **Database Connection Errors**
   ```bash
   # Railway automatically provides DATABASE_URL
   # Check if PostgreSQL service is running in Railway dashboard
   # Ensure migrations have been run using Railway terminal
   # Verify database service is connected to your Django service
   ```

3. **CORS Errors**
   ```bash
   # Use Railway's service reference variables: ${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
   # Check that frontend is making requests to correct backend URL
   # Ensure no trailing slashes in URLs
   # Railway handles internal service communication automatically
   ```

4. **Static Files Not Loading**
   ```bash
   # Run: python manage.py collectstatic --noinput in Railway terminal
   # Check STATIC_URL and STATIC_ROOT settings
   # Verify whitenoise is configured correctly
   # Railway serves static files automatically for Django
   ```

5. **Service Communication Issues**
   ```bash
   # Use Railway's internal networking with service variables
   # Check service logs in Railway dashboard
   # Ensure services are in the same Railway project
   # Railway provides automatic service discovery
   ```

6. **Environment Variable Issues**
   ```bash
   # Use Railway's Variables tab for each service
   # Reference other services: ${{ServiceName.RAILWAY_PUBLIC_DOMAIN}}
   # Check variable syntax and spelling
   # Railway automatically injects database connection strings
   ```

---

## Monitoring and Maintenance

### Health Checks
- Monitor service status on Railway dashboard
- Real-time logs available for each service
- Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- Railway provides built-in metrics and monitoring

### Scaling
- **Starter Plan ($5/month)**:
  - 512MB RAM, shared CPU
  - No sleep time (always-on)
  - 500GB bandwidth
- **Pro Plan ($20/month)**:
  - 8GB RAM, dedicated CPU
  - Unlimited bandwidth
  - Priority support
- **Auto-scaling**: Railway automatically handles traffic spikes

### Backups
- **Database**: Railway provides automatic daily backups
- **Point-in-time recovery**: Available for PostgreSQL
- **Media Files**: Consider using cloud storage (AWS S3, Cloudinary) for production
- **Code**: Automatic backups through GitHub integration

---

## Environment Variables Reference

### Backend (Django)
```bash
# Required (you set these)
DJANGO_SETTINGS_MODULE=alumni_system.settings
DEBUG=False
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=jwt-secret
CORS_ALLOWED_ORIGINS=${{Frontend.RAILWAY_PUBLIC_DOMAIN}}

# Automatically provided by Railway
DATABASE_URL=postgresql://... (auto-generated)
REDIS_URL=redis://... (auto-generated if Redis added)
RAILWAY_ENVIRONMENT=production
PORT=8000 (auto-assigned)

# Optional
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
USE_S3=False
```

### Frontend (Vue.js)
```bash
# Required
VITE_API_BASE_URL=${{Django.RAILWAY_PUBLIC_DOMAIN}}

# Optional
NODE_VERSION=18

# Automatically provided by Railway
RAILWAY_ENVIRONMENT=production
PORT=3000 (auto-assigned)
```

### Railway-Specific Variables
```bash
# Service References (Railway automatically provides these)
${{ServiceName.RAILWAY_PUBLIC_DOMAIN}} - Public URL of a service
${{ServiceName.RAILWAY_PRIVATE_DOMAIN}} - Private URL for internal communication
RAILWAY_GIT_COMMIT_SHA - Current deployment commit
RAILWAY_ENVIRONMENT - Current environment (production/staging)
```

---

## Support

If you encounter issues:

1. **Check Railway Logs**: Each service has real-time logs in the dashboard
2. **Review Django Logs**: Backend logs will show Python/Django errors
3. **Check Browser Console**: Frontend errors appear in browser dev tools
4. **Railway Documentation**: [docs.railway.app](https://docs.railway.app)
5. **Railway Discord**: Very active community support at [railway.app/discord](https://railway.app/discord)
6. **Railway CLI**: Install `railway` CLI for local debugging and deployment
7. **Service Metrics**: Built-in monitoring and alerting in Railway dashboard

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Railway automatically configures `ALLOWED_HOSTS`
- [ ] CORS settings use Railway service variables
- [ ] Database credentials automatically secured by Railway
- [ ] Environment variables are private to your project
- [ ] HTTPS enforced automatically (Railway provides SSL certificates)
- [ ] Use Railway's service-to-service communication for internal APIs
- [ ] Enable Railway's built-in monitoring and alerts

---

## Railway Advantages

✅ **Automatic Configuration**: Railway detects and configures most settings automatically

✅ **Built-in Services**: PostgreSQL, Redis, and other databases included

✅ **Service Discovery**: Services can reference each other automatically

✅ **Real-time Logs**: Live log streaming and monitoring

✅ **GitHub Integration**: Automatic deployments on every push

✅ **No Sleep Time**: Services stay awake on paid plans

✅ **Generous Free Tier**: $5 monthly credit for testing

---

Congratulations! Your alumni system should now be live on Railway. Railway's automatic detection and configuration makes deployment much simpler than traditional platforms. Remember to test all functionality thoroughly and monitor the services using Railway's built-in dashboard.