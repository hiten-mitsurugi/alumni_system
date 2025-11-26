# 🧪 Docker Testing Checklist

## Pre-Flight Check

### 1. Docker Installation
- [ ] Docker Desktop installed and running
- [ ] Docker version: `docker --version` (should show v20+)
- [ ] Docker Compose version: `docker-compose --version` (should show v2.0+)
- [ ] At least 8GB RAM allocated to Docker
- [ ] At least 20GB disk space available

### 2. Environment Configuration
- [ ] `.env` file exists (copied from `.env.example`)
- [ ] `POSTGRES_PASSWORD` set (not default)
- [ ] `SECRET_KEY` set (not default)
- [ ] `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` set
- [ ] `CRYPTOGRAPHY_SALT` set

---

## First-Time Setup Testing

### Step 1: Build and Start Services
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Expected Output**:
- [ ] Creating network "alumni_system_alumni_network"
- [ ] Creating volume "alumni_system_postgres_data"
- [ ] Creating volume "alumni_system_redis_data"
- [ ] Creating volume "alumni_system_media_files"
- [ ] Creating volume "alumni_system_static_files"
- [ ] Building backend... (may take 2-5 minutes first time)
- [ ] Building frontend... (may take 2-5 minutes first time)
- [ ] All containers started successfully

### Step 2: Verify Services Running
```bash
docker-compose ps
```

**Expected Status** (wait up to 60 seconds):
- [ ] alumni_postgres: Up (healthy)
- [ ] alumni_redis: Up (healthy)
- [ ] alumni_backend: Up
- [ ] alumni_celery: Up
- [ ] alumni_frontend: Up

**If any service is not "Up"**:
```bash
# Check logs
docker-compose logs [service-name]
```

### Step 3: Check Logs for Errors
```bash
# Backend logs
docker-compose logs backend | grep -i error

# Frontend logs
docker-compose logs frontend | grep -i error
```

**Expected**:
- [ ] No critical errors
- [ ] Backend: "✅ PostgreSQL is ready!"
- [ ] Backend: "✅ Redis is ready!"
- [ ] Backend: "🚀 Starting Daphne ASGI server..."
- [ ] Frontend: "VITE v[version] ready in [time]ms"

### Step 4: Run Database Migrations
```bash
docker-compose exec backend python manage.py migrate
```

**Expected**:
- [ ] Migrations applied successfully
- [ ] No errors about missing tables
- [ ] Output shows all apps migrated

### Step 5: Create Superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```

**Test**:
- [ ] Prompts for username
- [ ] Prompts for email
- [ ] Prompts for password
- [ ] Superuser created successfully

### Step 6: Collect Static Files
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

**Expected**:
- [ ] Static files collected
- [ ] No errors

---

## Application Testing

### Frontend Access
**URL**: http://localhost:5173

- [ ] Page loads (no 404 or 500 errors)
- [ ] Alumni System logo/title visible
- [ ] Login form displays correctly
- [ ] Registration link works
- [ ] No console errors in browser dev tools (F12)
- [ ] Network tab shows API calls to `http://localhost:8000`

### Backend Access
**URL**: http://localhost:8000/admin/

- [ ] Django admin login page loads
- [ ] Can log in with superuser credentials
- [ ] Admin dashboard displays
- [ ] Can see all registered models
- [ ] No errors in page

### API Testing
**URL**: http://localhost:8000/api/

- [ ] API root page displays
- [ ] Shows available endpoints
- [ ] JWT authentication endpoints visible
- [ ] No 500 errors

---

## Feature Testing

### 1. Authentication ✅
- [ ] **Register new user**:
  - Go to registration page
  - Fill in all required fields
  - Submit form
  - User created successfully

- [ ] **Login**:
  - Use registered credentials
  - Login successful
  - Redirected to dashboard/home
  - Token stored in localStorage

- [ ] **Logout**:
  - Click logout
  - Redirected to login page
  - Token cleared

### 2. Profile Management ✅
- [ ] **View profile**:
  - Navigate to profile page
  - Profile information displays
  - Profile picture shows (if set)

- [ ] **Upload profile picture**:
  - Click upload/change picture
  - Select image file
  - Upload successful
  - Image displays immediately
  - Check `Backend/media/profile_pictures/` in volume

- [ ] **Edit profile**:
  - Click edit button
  - Modify information
  - Save changes
  - Changes persist after refresh

### 3. Real-Time Messaging ✅
- [ ] **Open messaging page**:
  - Messaging interface loads
  - WebSocket connection established (check browser console)
  - Console shows: "✅ Notifications WebSocket connected"

- [ ] **Send message**:
  - Select conversation or create new
  - Type message
  - Send
  - Message appears in chat instantly
  - No page refresh needed

- [ ] **Receive message** (test with 2 browser windows):
  - Open app in 2 different browsers/tabs
  - Send message from browser 1
  - Message appears in browser 2 instantly
  - No refresh needed

- [ ] **Group messaging**:
  - Create group
  - Add members
  - Send message to group
  - All members see message

### 4. Real-Time Notifications ✅
- [ ] **Notification system**:
  - Perform action that triggers notification (like, comment, etc.)
  - Notification badge updates instantly
  - Click notification icon
  - Notifications list displays
  - Can mark as read

- [ ] **Cross-device notifications** (test on LAN):
  - Update `.env` with your IP address
  - Restart containers
  - Access from mobile device
  - Trigger notification from PC
  - Notification appears on mobile instantly

### 5. Posts ✅
- [ ] **Create post**:
  - Click create post
  - Add text content
  - Add image (optional)
  - Publish
  - Post appears in feed

- [ ] **Like post**:
  - Click like button
  - Like count increases
  - Icon changes to "liked" state

- [ ] **Comment on post**:
  - Click comment
  - Type comment
  - Submit
  - Comment appears under post

- [ ] **Post privacy**:
  - Set post to private
  - Verify only intended audience sees it

### 6. Survey System ✅
- [ ] **View surveys**:
  - Navigate to surveys
  - Survey list displays
  - Can open survey

- [ ] **Complete survey**:
  - Select survey
  - Answer questions
  - Submit
  - Completion recorded

- [ ] **View analytics** (admin):
  - Go to admin survey analytics
  - Charts and graphs display
  - Data accurate

### 7. File Uploads ✅
- [ ] **Profile picture**: ✅ (tested above)
- [ ] **Post media**:
  - Create post with image
  - Image uploads
  - Image displays in post
- [ ] **Achievements**:
  - Upload achievement document
  - File saved
  - File accessible
- [ ] **Chat attachments**:
  - Send file in chat
  - File uploads
  - Recipient can download

### 8. Privacy Settings ✅
- [ ] **Field privacy**:
  - Go to privacy settings
  - Change field visibility (email, phone, etc.)
  - Save
  - Verify changes take effect

- [ ] **Profile visibility**:
  - Set profile to private/public
  - Test from different user account
  - Visibility changes work

---

## WebSocket Testing

### Backend WebSocket Logs
```bash
docker-compose logs backend | grep -i websocket
```

**Expected**:
- [ ] "WebSocket connected to notifications"
- [ ] "Connection established" messages
- [ ] No connection refused errors

### Browser Console (F12)
**Expected in console**:
- [ ] "🌐 Connecting to notifications WebSocket: ws://localhost:8000/ws/notifications/"
- [ ] "✅ Notifications WebSocket connected"
- [ ] No WebSocket connection errors
- [ ] No 403 Forbidden errors

### Test WebSocket URL
**Open browser console and run**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/notifications/?token=' + localStorage.getItem('access_token'))
ws.onopen = () => console.log('✅ Connected')
ws.onerror = (e) => console.error('❌ Error:', e)
```

**Expected**:
- [ ] "✅ Connected" appears in console
- [ ] No errors

---

## Performance Testing

### Load Times
- [ ] Frontend loads in < 3 seconds
- [ ] Backend API responds in < 500ms
- [ ] Images load quickly
- [ ] No slow queries (check backend logs)

### Resource Usage
```bash
docker stats
```

**Expected**:
- [ ] Backend: < 500MB RAM
- [ ] Frontend: < 200MB RAM
- [ ] PostgreSQL: < 200MB RAM
- [ ] Redis: < 50MB RAM
- [ ] Total: < 1GB RAM

---

## LAN Access Testing

### Step 1: Find IP Address
**Windows**:
```bash
ipconfig
```
**Mac/Linux**:
```bash
ifconfig
```

**Record your IP**: ________________

### Step 2: Update Environment
Edit `.env`:
```env
VITE_API_BASE_URL=http://YOUR_IP:8000
VITE_API_URL=http://YOUR_IP:8000/api
VITE_WS_URL=ws://YOUR_IP:8000/ws/notifications/
```

### Step 3: Restart
```bash
docker-compose down
docker-compose up -d
```

### Step 4: Test from Mobile
**On mobile device** (same WiFi):
- [ ] Navigate to: http://YOUR_IP:5173
- [ ] Page loads
- [ ] Can login
- [ ] Can send messages
- [ ] Notifications work
- [ ] All features functional

---

## Production Build Testing

### Step 1: Build for Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

**Expected**:
- [ ] Frontend builds successfully (2-5 minutes)
- [ ] Backend builds successfully (2-5 minutes)
- [ ] No build errors

### Step 2: Start Production
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Expected**:
- [ ] All services start
- [ ] Nginx proxy running

### Step 3: Access via Nginx
**URL**: http://localhost (port 80)

- [ ] Frontend loads
- [ ] All features work
- [ ] Static files cached
- [ ] API calls proxied correctly
- [ ] WebSocket upgrade works

### Step 4: Check Nginx Logs
```bash
docker-compose logs nginx
```

**Expected**:
- [ ] Requests logged
- [ ] No 502 Bad Gateway errors
- [ ] WebSocket upgrades successful

---

## Database Testing

### PostgreSQL Connection
```bash
docker-compose exec postgres psql -U postgres -d thesis_db
```

**Test queries**:
```sql
-- Check tables exist
\dt

-- Check user count
SELECT COUNT(*) FROM auth_app_customuser;

-- Check posts
SELECT COUNT(*) FROM posts_app_post;

-- Exit
\q
```

**Expected**:
- [ ] Can connect to database
- [ ] All tables exist
- [ ] Data persists after restart

### Redis Connection
```bash
docker-compose exec redis redis-cli
```

**Test commands**:
```bash
PING
# Should return: PONG

KEYS *
# Should show some keys

INFO server
# Should show Redis info

EXIT
```

**Expected**:
- [ ] Can connect to Redis
- [ ] PING returns PONG
- [ ] Keys exist if caching is active

---

## Volume Persistence Testing

### Step 1: Create Test Data
- [ ] Create a post
- [ ] Upload a profile picture
- [ ] Send a message

### Step 2: Stop Containers
```bash
docker-compose down
```

### Step 3: Start Containers
```bash
docker-compose up -d
```

### Step 4: Verify Data Persists
- [ ] Post still exists
- [ ] Profile picture still shows
- [ ] Message history intact
- [ ] User still logged in (if token valid)

### Step 5: Check Volumes
```bash
docker volume ls
```

**Expected volumes**:
- [ ] alumni_system_postgres_data
- [ ] alumni_system_redis_data
- [ ] alumni_system_media_files
- [ ] alumni_system_static_files

---

## Error Recovery Testing

### Test 1: Database Connection Loss
```bash
# Stop PostgreSQL
docker-compose stop postgres

# Wait 10 seconds

# Check backend logs
docker-compose logs backend
```

**Expected**:
- [ ] Backend shows connection errors
- [ ] Frontend shows loading/error states

```bash
# Restart PostgreSQL
docker-compose start postgres
```

**Expected**:
- [ ] Backend reconnects automatically
- [ ] Application resumes normal operation

### Test 2: Redis Connection Loss
```bash
# Stop Redis
docker-compose stop redis

# Check backend logs
docker-compose logs backend
```

**Expected**:
- [ ] Backend continues working (uses in-memory fallback)
- [ ] WebSockets may disconnect

```bash
# Restart Redis
docker-compose start redis
```

**Expected**:
- [ ] Backend reconnects
- [ ] Caching resumes

### Test 3: Container Crash Recovery
```bash
# Force kill backend
docker-compose kill backend

# Check status
docker-compose ps
```

**Expected with `restart: unless-stopped`**:
- [ ] Container restarts automatically
- [ ] Service recovers within 10 seconds

---

## Security Testing

### Environment Variables
```bash
docker-compose exec backend env | grep -E "SECRET|PASSWORD"
```

**Expected**:
- [ ] `SECRET_KEY` is set (not default)
- [ ] `DB_PASSWORD` is set
- [ ] Sensitive values not exposed in logs

### Debug Mode
```bash
docker-compose exec backend python manage.py check --deploy
```

**Expected**:
- [ ] No critical warnings in production
- [ ] `DEBUG=False` in production
- [ ] Security middleware enabled

### CORS Configuration
```bash
curl -I http://localhost:8000/api/
```

**Expected**:
- [ ] CORS headers present
- [ ] Allowed origins configured

---

## Final Checklist

### Documentation
- [ ] README_DOCKER.md reviewed
- [ ] QUICK_START_DOCKER.md reviewed
- [ ] DOCKER_IMPLEMENTATION_SUMMARY.md reviewed

### All Features Working
- [ ] Authentication ✅
- [ ] Real-time messaging ✅
- [ ] Real-time notifications ✅
- [ ] File uploads ✅
- [ ] Posts & comments ✅
- [ ] Survey system ✅
- [ ] Privacy settings ✅
- [ ] Admin panel ✅

### Performance
- [ ] Page load < 3 seconds
- [ ] API response < 500ms
- [ ] No memory leaks
- [ ] CPU usage reasonable

### Deployment Ready
- [ ] Production build works
- [ ] Nginx proxy configured
- [ ] Environment variables set
- [ ] Volumes persist data
- [ ] Health checks enabled
- [ ] Restart policies set

---

## ✅ Sign-Off

**Tested By**: _________________

**Date**: _________________

**All Tests Passed**: ☐ Yes ☐ No

**Issues Found**: _________________

**Notes**: _________________

---

## 🆘 If Tests Fail

### Common Issues:

1. **Port already in use**:
   ```bash
   # Find process using port
   netstat -ano | findstr :8000
   # Kill process or change port in docker-compose.yml
   ```

2. **Build fails**:
   ```bash
   # Clear Docker cache
   docker system prune -a
   # Rebuild
   docker-compose build --no-cache
   ```

3. **Database migration errors**:
   ```bash
   # Drop and recreate
   docker-compose down -v
   docker-compose up -d
   docker-compose exec backend python manage.py migrate
   ```

4. **WebSocket not connecting**:
   - Check browser console for errors
   - Verify token is valid
   - Check backend logs: `docker-compose logs backend | grep -i websocket`
   - Ensure VITE_WS_URL matches backend URL

5. **File uploads fail**:
   ```bash
   # Check media volume
   docker volume inspect alumni_system_media_files
   # Check permissions
   docker-compose exec backend ls -la /app/media
   ```

---

**Testing Date**: November 26, 2025
**Version**: 1.0.0
**Status**: Ready for Testing 🧪
