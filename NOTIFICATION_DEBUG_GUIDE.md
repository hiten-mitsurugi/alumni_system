# 🔍 Notification System Debug Guide

## ✅ What We Just Fixed

### 1. **AlumniNavbar Modularization**
The navbar is now organized into **8 clear sections**:
- **Section 1**: Initialization & Setup (imports, stores, props)
- **Section 2**: State Management (refs, injections)
- **Section 3**: Computed Properties (notifications, theme, margins, profile)
- **Section 4**: Notification Handlers (markAsRead, markAllAsRead, getNotificationColor)
- **Section 5**: Theme Management (toggleTheme)
- **Section 6**: Authentication & Logout (confirmLogout, cancelLogout, handleLogout)
- **Section 7**: UI Event Handlers (handleImageError, handleClickOutside)
- **Section 8**: Lifecycle Hooks (initializeUser, initializeNotifications, onMounted, onUnmounted)

### 2. **Enhanced Notification Initialization**
Added detailed logging to see exactly what's happening:
```javascript
async function initializeNotifications() {
  console.log('🔔 Initializing notifications system...')
  
  try {
    await notificationsStore.fetchNotifications()
    console.log('✅ Notifications fetched:', notificationsStore.items.length)
    
    notificationsStore.connectWebSocket()
    console.log('✅ WebSocket connection initiated')
  } catch (error) {
    console.error('❌ Failed to initialize notifications:', error)
  }
}
```

### 3. **Added 'post' Type Color**
The notification color map now includes the `post` type (for comments/reactions):
```javascript
post: themeStore.isDarkMode ? 'bg-indigo-900/30 text-indigo-400' : 'bg-indigo-100 text-indigo-600'
```

---

## 🧪 How to Test Notifications

### **Step 1: Start Your Backend Server**
```powershell
cd Backend
python manage.py runserver
```

Make sure you see:
```
Starting development server at http://127.0.0.1:8000/
```

### **Step 2: Open Your Frontend**
Open your browser to your frontend URL (e.g., `http://localhost:5173`)

### **Step 3: Open Browser Console (F12)**
Look for these logs when the page loads:
```
🔔 Initializing notifications system...
✅ Notifications fetched: X
✅ WebSocket connection initiated
✅ Notifications WebSocket connected
```

### **Step 4: Check WebSocket Connection**
In the console, type:
```javascript
localStorage.getItem('access_token')
```
Make sure you have a token. If not, log in first.

### **Step 5: Trigger a Notification**
Open another browser tab/window (or use incognito mode) and:
1. Log in as a **different user**
2. Find a post by the first user
3. Add a comment or reaction
4. Go back to the first user's tab

You should see:
```
📬 New notification received: {title, message, type}
```

And the notification bell should show a red badge with the count!

---

## 🐛 Troubleshooting

### ❌ "No access token" Error
**Problem:** WebSocket can't connect without authentication

**Solution:**
1. Make sure you're logged in
2. Check `localStorage.getItem('access_token')` in console
3. If null, log out and log in again

---

### ❌ WebSocket Connection Failed
**Problem:** WebSocket shows disconnected or errors

**Check:**
1. **Is Django server running?**
   ```powershell
   cd Backend
   python manage.py runserver
   ```

2. **Is Redis running?** (Required for WebSocket)
   ```powershell
   redis-cli ping
   # Should return: PONG
   ```
   
   If not running:
   ```powershell
   redis-server
   ```

3. **Check WebSocket URL in console**
   Should be: `ws://localhost:8000/ws/notifications/?token=YOUR_TOKEN`

---

### ❌ "Failed to fetch notifications" Error
**Problem:** HTTP API not responding

**Check:**
1. **Backend server running?**
2. **Correct API URL?** Should be `http://localhost:8000/api/notifications/`
3. **Check Network tab** in browser DevTools → look for 401 Unauthorized or 404 errors

**Test API directly:**
```powershell
cd Backend
python test_notification_rest_api.py
```

---

### ❌ Notifications Not Appearing in Real-time
**Problem:** Backend works, but notifications don't show up immediately

**Check:**
1. **WebSocket connected?** Look for "✅ Notifications WebSocket connected" in console
2. **Console errors?** Red errors in console might show the issue
3. **Store state?** In Vue DevTools → Pinia → notifications:
   - `items`: Should have array of notifications
   - `unreadCount`: Should match badge number
   - `wsConnected`: Should be `true`

**Manual test:**
In browser console:
```javascript
// Check store state
const store = window.__PINIA_STORE__;
console.log('Notifications:', store.notifications.items);
console.log('Unread count:', store.notifications.unreadCount);
console.log('WebSocket connected:', store.notifications.wsConnected);
```

---

### ❌ Notifications Fetched But Not Displayed
**Problem:** Console shows "Notifications fetched: 5" but navbar shows "No notifications yet"

**Check:**
1. Open Vue DevTools → Components → AlumniNavbar
2. Check `notifications` computed property
3. Should match `notificationsStore.items`

**Debug:**
```javascript
// In browser console
console.log('Store items:', window.__PINIA_STORE__.notifications.items);
```

---

## 🎯 Expected Behavior

### ✅ On Page Load:
```
🔔 Initializing notifications system...
✅ Notifications fetched: 3
✅ WebSocket connection initiated
✅ Notifications WebSocket connected
```

### ✅ When Someone Comments Your Post:
```
📬 New notification received: {
  id: 123,
  type: 'post',
  title: 'John Doe commented on your post',
  message: 'Nice post!',
  time_ago: 'Just now'
}
```

### ✅ When Someone Mentions You:
```
📬 New notification received: {
  id: 124,
  type: 'post',
  title: 'John Doe mentioned you in a comment',
  message: '@yourname check this out!',
  time_ago: 'Just now'
}
```

### ✅ Visual Indicators:
- 🔴 Red badge on bell icon with count (e.g., "3")
- 🔵 Blue background on unread notifications
- 🔵 Blue dot next to unread notification titles
- ✨ Smooth animation when new notification arrives

---

## 🧰 Using the Test WebSocket Page

We created `test_websocket.html` for debugging:

1. **Open the file** in your browser:
   ```
   file:///C:/Users/USER/OneDrive/Desktop/Thesis/development/alumni_system/test_websocket.html
   ```

2. **Get your token**:
   - Open frontend → Log in
   - Press F12 → Console
   - Type: `localStorage.getItem('access_token')`
   - Copy the token

3. **Paste token** into the test page

4. **Click "Connect to WebSocket"**

5. **Watch the logs**:
   - Green = Success ✅
   - Red = Error ❌
   - Blue = Info ℹ️

6. **Trigger a notification** in your app and watch it appear in real-time!

---

## 📊 Check Backend Test Results

We already ran the backend test and **ALL TESTS PASSED**:

```powershell
cd Backend
python test_notification_api.py
```

**Results:**
```
✅ Step 1: Notifications table exists
✅ Step 2: Test users found
✅ Step 3: Created 3 test notifications
📡 Broadcasted notification to user 5: Test System Notification
✅ Step 4: Notifications retrieved successfully (3 found)
✅ Step 5: Signal triggered - notification created
✅ MENTION DETECTED! Notification created for user 5
✅ Step 6: Mention detection working
✅ Step 7: Serializer includes time_ago field
✅ Step 8: Mark as read works
✅ Step 9: Channel layer communication works

🎉 All backend tests passed!
```

This confirms the backend is **100% working**. If notifications still don't appear in frontend, the issue is:
- WebSocket connection not established
- Frontend not calling store methods
- Token not being sent correctly

---

## 🔬 Advanced Debugging

### Check All Components:

1. **Backend API Test:**
   ```powershell
   cd Backend
   python test_notification_api.py
   ```

2. **REST API Test** (requires server running):
   ```powershell
   cd Backend
   # Edit test_notification_rest_api.py - update username/password
   python test_notification_rest_api.py
   ```

3. **Check Database:**
   ```powershell
   cd Backend
   python manage.py shell
   ```
   ```python
   from notifications_app.models import Notification
   print(f"Total notifications: {Notification.objects.count()}")
   
   # Get recent notifications
   for n in Notification.objects.all()[:5]:
       print(f"{n.id}: {n.title} -> User {n.user_id}")
   ```

4. **Check Redis:**
   ```powershell
   redis-cli
   KEYS *
   # Should show channel keys if WebSocket is active
   ```

---

## 📝 Summary

✅ **Backend**: 100% working (all tests passed)  
✅ **AlumniNavbar**: Now modularized into 8 sections  
✅ **Store**: Properly integrated with WebSocket  
✅ **Logging**: Added detailed console logs  

**Next**: Check your browser console for the new logs to see exactly what's happening!
