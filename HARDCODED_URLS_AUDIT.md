# Hardcoded URLs Audit - Alumni System

## 🔍 Overview
This document lists all hardcoded `localhost` URLs found in the codebase that must be replaced with environment variables before Docker containerization.

**Total Files Affected**: 8 files  
**Priority**: HIGH - Required for Docker deployment

---

## 📋 Files Requiring Updates

### 1. **Frontend/src/views/Admin/PostApprovalPage.vue**
**Line**: 7  
**Current Code**:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```
**Status**: ✅ Already using environment variable with localhost fallback  
**Action Required**: ✅ **NO CHANGE NEEDED** - This is the correct pattern

---

### 2. **Frontend/src/components/mymates/UserCard.vue**
**Line**: 106  
**Current Code**:
```javascript
const BASE_URL = 'http://localhost:8000';  // Backend server for media files
```
**Issue**: Hardcoded localhost for media files  
**Fix Required**:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
```
**Impact**: User profile pictures won't load in Docker  
**Priority**: 🔴 HIGH

---

### 3. **Frontend/src/components/alumni/messaging/CreateGroupModal.vue**
**Line**: 307  
**Current Code**:
```javascript
return `http://localhost:8000${user.profile_picture}`
```
**Issue**: Hardcoded localhost for profile pictures in group creation  
**Fix Required**:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
return `${BASE_URL}${user.profile_picture}`
```
**Impact**: Profile pictures won't show when creating groups  
**Priority**: 🔴 HIGH

---

### 4. **Frontend/src/components/alumni/messaging/ForwardModal.vue**
**Lines**: 272, 278, 351 (3 instances)  

#### Instance 1 (Line 272):
**Current Code**:
```javascript
fetch('http://localhost:8000/api/message/conversations/', {
```
**Fix Required**:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
fetch(`${BASE_URL}/api/message/conversations/`, {
```

#### Instance 2 (Line 278):
**Current Code**:
```javascript
fetch('http://localhost:8000/api/message/group/', {
```
**Fix Required**:
```javascript
fetch(`${BASE_URL}/api/message/group/`, {
```

#### Instance 3 (Line 351):
**Current Code**:
```javascript
const response = await fetch('http://localhost:8000/api/message/forward/', {
```
**Fix Required**:
```javascript
const response = await fetch(`${BASE_URL}/api/message/forward/`, {
```

**Impact**: Message forwarding won't work in Docker  
**Priority**: 🔴 HIGH

---

### 5. **Frontend/src/services/privacyService.js**
**Line**: 6  
**Current Code**:
```javascript
const API_BASE_URL = 'http://localhost:8000/api/auth'
```
**Issue**: Hardcoded localhost for privacy API  
**Fix Required**:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_BASE_URL = `${BASE_URL}/api/auth`;
```
**Impact**: Privacy settings won't work in Docker  
**Priority**: 🔴 HIGH

---

### 6. **Frontend/src/services/reportsService.js**
**Line**: 4  
**Current Code**:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
```
**Status**: ✅ Already using environment variable with localhost fallback  
**Action Required**: ✅ **NO CHANGE NEEDED** - This is the correct pattern

---

## ✅ Files Already Correct

These files were flagged but are actually using the correct pattern:

1. **PostApprovalPage.vue** - Uses `import.meta.env.VITE_API_BASE_URL`
2. **reportsService.js** - Uses `import.meta.env.VITE_API_BASE_URL`

---

## 🔧 Recommended Fix Pattern

### **Standard Pattern to Use**:
```javascript
// At the top of the file or in the setup/script section
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Then use it in your code
fetch(`${BASE_URL}/api/endpoint/`, { ... })
```

### **For Media Files**:
```javascript
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const mediaUrl = `${BASE_URL}${user.profile_picture}`;
```

---

## 📝 Summary of Required Changes

| File | Lines | Instances | Priority |
|------|-------|-----------|----------|
| UserCard.vue | 106 | 1 | 🔴 HIGH |
| CreateGroupModal.vue | 307 | 1 | 🔴 HIGH |
| ForwardModal.vue | 272, 278, 351 | 3 | 🔴 HIGH |
| privacyService.js | 6 | 1 | 🔴 HIGH |
| **TOTAL** | - | **6 instances** | - |

---

## 🐳 Docker Environment Variables

### **What Will Be Set in Docker**:

**Development**:
```env
VITE_API_BASE_URL=http://localhost:8000
```

**Production (Docker Internal)**:
```env
VITE_API_BASE_URL=http://backend:8000
```

**Production (External Access)**:
```env
VITE_API_BASE_URL=http://your-domain.com
# or
VITE_API_BASE_URL=http://your-server-ip:8000
```

---

## 🎯 Implementation Plan

### **Step 1: Fix All 6 Instances**
- [ ] UserCard.vue (1 instance)
- [ ] CreateGroupModal.vue (1 instance)
- [ ] ForwardModal.vue (3 instances)
- [ ] privacyService.js (1 instance)

### **Step 2: Test Locally**
```bash
# Test with environment variable
VITE_API_BASE_URL=http://192.168.1.19:8000 npm run dev

# Should work with different IPs
```

### **Step 3: Verify in Docker**
```bash
# Build and run with Docker Compose
docker-compose up -d

# Check that all API calls work
# Check that media files load
```

---

## ⚠️ Related Issues

### **Backend Hardcoded URLs**
The backend `.env` file currently has:
```env
DB_HOST=localhost
REDIS_HOST=127.0.0.1
```

These will be changed to Docker service names:
```env
DB_HOST=postgres
REDIS_HOST=redis
```

### **WebSocket URLs**
Already fixed in previous session:
- ✅ `stores/notifications.js` - Uses dynamic IP
- ✅ `views/Alumni/Messaging.vue` - Uses dynamic IP
- ✅ `services/websocket.js` - Uses `window.location.hostname`

---

## 🚀 Expected Impact

### **Before Fix** (Docker):
❌ Profile pictures: Broken  
❌ Group creation: Profile pictures missing  
❌ Message forwarding: 404 errors  
❌ Privacy settings: API calls fail  

### **After Fix** (Docker):
✅ Profile pictures: Working  
✅ Group creation: Profile pictures visible  
✅ Message forwarding: Fully functional  
✅ Privacy settings: API calls succeed  

---

## 📞 Testing Checklist

After implementing fixes, test these features:

- [ ] View user profiles with pictures
- [ ] Create a new group (check member pictures)
- [ ] Forward a message to conversation
- [ ] Forward a message to group
- [ ] Change privacy settings
- [ ] Upload profile picture
- [ ] View media attachments in messages

---

**Audit Date**: November 26, 2025  
**Auditor**: GitHub Copilot  
**Status**: Ready for Implementation ✅
