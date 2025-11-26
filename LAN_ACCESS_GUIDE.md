# 🌐 LAN Access Guide - Alumni System

## Quick Start

### Windows Users:
Simply double-click `start-lan.bat` - it will:
- ✅ Auto-detect your current IP address
- ✅ Start backend on `0.0.0.0:8000` (accessible from network)
- ✅ Start frontend on `0.0.0.0:5173` with dynamic backend connection
- ✅ Show you the URL to share with others

### Mac/Linux Users:
```bash
chmod +x start-lan.sh
./start-lan.sh
```

---

## How It Works

### The Magic: Auto-Detection
Every time you run `npm run dev` in the Frontend, it:
1. Detects your **current IP address** (works at home, school, anywhere!)
2. Updates `.env` file automatically with the correct backend URL
3. Frontend connects to backend using your current network IP

### What Changed:

**Frontend/package.json:**
```json
"dev": "node generate-env.js && vite --host 0.0.0.0"
```
- Runs IP detection script first
- Then starts Vite with network access

**Frontend/generate-env.js:**
- New file that auto-detects IP
- Updates `.env` with correct URLs

**Backend/.env:**
```
CORS_ALLOWED_ORIGINS=*
```
- Allows requests from any IP (safe for LAN)

**Backend Settings:**
- `CORS_ALLOW_ALL_ORIGINS = True` already enabled
- `ALLOWED_HOSTS = ['*']` already set

---

## Different Networks = Same Process

### At Home (WiFi: 192.168.1.19):
```
npm run dev → Detects 192.168.1.19 → Updates .env → Works! ✅
```

### At School (WiFi: 10.0.5.42):
```
npm run dev → Detects 10.0.5.42 → Updates .env → Works! ✅
```

### At Coffee Shop (WiFi: 172.16.8.99):
```
npm run dev → Detects 172.16.8.99 → Updates .env → Works! ✅
```

**No manual changes needed!** 🎉

---

## Manual Start (If you prefer):

### Backend:
```bash
cd Backend
python manage.py runserver 0.0.0.0:8000
```

### Frontend:
```bash
cd Frontend
npm run dev
```
(The `npm run dev` command now automatically detects IP)

---

## Testing from Other Devices

1. Make sure both devices are on **same WiFi**
2. Start the system using `start-lan.bat` (or manually)
3. Note the IP shown (e.g., `192.168.1.19`)
4. On other device, open browser and go to: `http://192.168.1.19:5173`

---

## Troubleshooting

**Q: Other device can't connect?**
- Make sure both on same WiFi network
- Check Windows Firewall (may need to allow port 8000 and 5173)
- Verify backend is running with `0.0.0.0:8000` (not `localhost:8000`)

**Q: Frontend loads but can't login?**
- Check `Frontend/.env` - should show your network IP, not localhost
- Run `node generate-env.js` manually in Frontend folder
- Restart frontend

**Q: What if I want to use localhost only?**
Edit `Frontend/.env` manually and set:
```
VITE_API_URL=http://localhost:8000/api
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws/notifications/
```

---

## Security Note

This configuration (`CORS_ALLOW_ALL_ORIGINS = True`) is **safe for local network testing** but should be changed for production deployment. For production, specify exact allowed origins.

---

## Current Configuration Status

✅ Backend accepts connections from network  
✅ Frontend auto-detects IP on startup  
✅ CORS configured for cross-origin requests  
✅ WebSocket configured for network access  
✅ Works on any network (home, school, etc.)  

**Your system is now fully dynamic and network-ready!** 🚀
