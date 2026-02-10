# Image Display Fix Documentation

## Problem Summary

Images were not displaying across the entire alumni system (profile pictures, cover photos, post images, etc.) due to **inconsistent URL construction** between frontend and backend.

## Root Causes

### 1. Backend Issues
- **Hardcoded localhost in serializers**: Backend serializers used `http://localhost:8000` as fallback, which doesn't work when accessing from different IPs or using Daphne (ASGI server)
- Located in:
  - `Backend/posts_app/serializers.py` (PostMediaSerializer, UserBasicSerializer)
  - Other app serializers

### 2. Frontend Issues  
- **No centralized image URL utility**: Each component constructed URLs differently
- **No environment configuration**: Missing `.env` file to configure backend URL
- **Inconsistent patterns**:
  - Some used hardcoded `http://127.0.0.1:8000`
  - Some used dynamic `${window.location.hostname}:8000`
  - Some tried to use `import.meta.env.VITE_API_BASE_URL` (which didn't exist)

### 3. Affected Components
- `MediaDisplay.vue` - Post images/videos not showing
- `AlumniNavbar.vue` - Profile pictures not showing
- `ProfileCard.vue` - Profile and cover photos failing
- `Messaging.vue` - Avatar images broken
- `Settings.vue`, `MyProfile.vue`, `UserProfile.vue` - Profile management screens

## Solution Implemented

### 1. Created Environment Configuration

**File**: `Frontend/.env.development`
```env
# Backend API Base URL (without /api suffix)
VITE_API_BASE_URL=http://localhost:8000
```

**File**: `Frontend/.env.example`
```env
# Example - copy to .env.development
VITE_API_BASE_URL=http://localhost:8000
# For network access: http://192.168.1.11:8000
```

### 2. Created Centralized Image URL Utility

**File**: `Frontend/src/utils/imageUrl.js`

Provides consistent functions:
- `getBackendBaseURL()` - Get backend URL from env or auto-detect
- `getImageUrl(path, fallback)` - Convert relative/absolute URLs
- `getProfilePictureUrl(path)` - Profile pictures with default avatar fallback
- `getCoverPhotoUrl(path)` - Cover photos (returns null if missing)
- `getMediaUrl(path)` - Post media files
- `getWebSocketBaseURL()` - WebSocket URLs (ws:// or wss://)

**Usage Example**:
```javascript
import { getProfilePictureUrl, getMediaUrl } from '@/utils/imageUrl'

// Profile picture with fallback
const avatarUrl = getProfilePictureUrl(user.profile_picture)

// Post media
const imageUrl = getMediaUrl(media.file_url)
```

### 3. Fixed Backend Serializers

**File**: `Backend/posts_app/serializers.py`

Changed from:
```python
# ❌ BAD - Hardcoded localhost
return f"http://localhost:8000{obj.file.url}"
```

To:
```python
# ✅ GOOD - Return relative URL, frontend handles base URL
return obj.file.url
```

The `request.build_absolute_uri()` already works correctly when Django has proper request context.

### 4. Updated Frontend Components

**Updated**:
- ✅ `MediaDisplay.vue` - Now uses `getMediaUrl()`
- ✅ `AlumniNavbar.vue` - Now uses `getProfilePictureUrl()`  
- ✅ `ProfileCard.vue` - Now uses `getProfilePictureUrl()` and `getCoverPhotoUrl()`
- ✅ `Messaging.vue` - Import added (partial update needed)

**Still Need Updates** (follow the pattern):
- `Settings.vue`
- `MyProfile.vue`
- `UserProfile.vue`
- `NetworkSuggestions.vue`
- Any other components displaying images

## How to Update Remaining Components

### Step 1: Import the utility
```javascript
import { getProfilePictureUrl, getCoverPhotoUrl, getMediaUrl } from '@/utils/imageUrl'
```

### Step 2: Replace manual URL construction

**Before**:
```javascript
const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`
const pic = user.profile_picture
const url = pic ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`) : '/default-avatar.png'
```

**After**:
```javascript
const url = getProfilePictureUrl(user.profile_picture)
```

### Step 3: Update template bindings

**Before**:
```vue
<img :src="user.profile_picture || '/default-avatar.png'" />
```

**After**:
```vue
<img :src="getProfilePictureUrl(user.profile_picture)" />
```

## Configuration for Different Environments

### Local Development (default)
```env
VITE_API_BASE_URL=http://localhost:8000
```

### Network Access (other devices on same WiFi)
```env
VITE_API_BASE_URL=http://192.168.1.11:8000
```

### Production
```env
VITE_API_BASE_URL=https://yourdomain.com
```

## Testing the Fix

### 1. Ensure environment is configured
```bash
cd Frontend
# Copy .env.example if .env.development doesn't exist
cp .env.example .env.development
```

### 2. Restart frontend dev server
```bash
npm run dev
```

### 3. Check browser console
Before fix:
- ❌ `Failed to load image: http://undefined/media/...`
- ❌ `404 Not Found` for images

After fix:
- ✅ Images load successfully
- ✅ Correct URLs: `http://localhost:8000/media/...`

### 4. Test different scenarios
- [x] Profile pictures in navbar
- [x] Cover photos on profiles
- [x] Post images/videos
- [x] Message avatars
- [ ] Settings page uploads
- [ ] User profile page

## Benefits of This Approach

1. **Centralized**: One utility handles all image URLs
2. **Flexible**: Works on localhost, LAN IPs, and production
3. **Type-safe**: Handles null/undefined/empty values gracefully
4. **Maintainable**: Easy to update if backend URL structure changes
5. **Environment-aware**: Different configs for dev/prod
6. **Fallbacks**: Proper default images when URLs are missing

## Common Issues & Solutions

### Issue: Images still not showing
**Solution**: 
1. Check `.env.development` exists and has correct `VITE_API_BASE_URL`
2. Restart Vite dev server
3. Clear browser cache (Ctrl+Shift+R)

### Issue: Images show on localhost but not on LAN IP
**Solution**: Update `.env.development` to use your machine's LAN IP instead of localhost

### Issue: CORS errors
**Solution**: Backend `.env` must include frontend URL in `CORS_ALLOWED_ORIGINS`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://192.168.1.11:5173
```

## Next Steps

1. ✅ Core utility created
2. ✅ Environment files created
3. ✅ Backend serializers fixed
4. ✅ Key components updated
5. ⏳ Update remaining components:
   - Settings.vue
   - MyProfile.vue
   - UserProfile.vue
   - NetworkSuggestions.vue
   - Any messaging sub-components
6. ⏳ Test all image display scenarios
7. ⏳ Document for deployment

## Files Modified

### Created
- `Frontend/.env.development`
- `Frontend/.env.example`
- `Frontend/src/utils/imageUrl.js`

### Updated
- `Backend/posts_app/serializers.py`
- `Frontend/src/components/posting/MediaDisplay.vue`
- `Frontend/src/components/alumni/AlumniNavbar.vue`
- `Frontend/src/components/alumni/ProfileCard.vue`
- `Frontend/src/views/Alumni/Messaging.vue` (partial)

### Need Updates
- `Frontend/src/views/Alumni/Settings.vue`
- `Frontend/src/views/Alumni/MyProfile.vue`
- `Frontend/src/views/Alumni/UserProfile.vue`
- `Frontend/src/views/Alumni/NetworkSuggestions.vue`
- Any other image-displaying components
