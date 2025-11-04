# Fixed Issues Summary

## Issue 1: Reject User Fails with "Cannot read properties of null (reading 'email')"

**File:** `Frontend/src/views/Admin/PendingUserApprovalPage.vue`

**Problem:**
- When rejecting a user, an error appeared: "Cannot read properties of null (reading 'email')"
- The user was still rejected and deleted, but the success alert showed the error

**Root Cause:**
- The code called `closeModal()` which set `selectedUser.value = null`
- Then immediately after, it tried to access `selectedUser.value.email` but it was already null

**Code Before:**
```javascript
const rejectUser = async () => {
  // ... validation code ...
  try {
    const response = await api.post(`/auth/reject-user/${selectedUser.value.id}/`);
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== selectedUser.value.id);
    closeModal();  // ← Sets selectedUser to null
    
    // Then tries to access the null value:
    if (response.data.email_sent) {
      alert(`✅ User application rejected.\n📧 Notification email sent to ${selectedUser.value.email}`); // ← ERROR!
    }
  }
}
```

**Code After:**
```javascript
const rejectUser = async () => {
  // ... validation code ...
  
  // ✅ Store user details BEFORE closeModal() sets selectedUser to null
  const userEmail = selectedUser.value.email;
  const userId = selectedUser.value.id;
  
  try {
    const response = await api.post(`/auth/reject-user/${userId}/`);
    pendingUsers.value = pendingUsers.value.filter(u => u.id !== userId);
    closeModal();
    
    // ✅ Now use the stored variables instead:
    if (response.data.email_sent) {
      alert(`✅ User application rejected.\n📧 Notification email sent to ${userEmail}`);
    }
  }
}
```

**Status:** ✅ **FIXED** - Rejection now works without errors

---

## Issue 2: Profile Picture Not Displaying Correctly on MyProfile Page

**File:** `Frontend/src/views/Alumni/MyProfile.vue`

**Problem:**
- Profile picture wasn't showing the correct image on the MyProfile page
- It was showing a cached or incorrect version

**Root Cause:**
- MyProfile.vue was using `user?.profile_picture` directly
- This doesn't include:
  1. Full URL with BASE_URL (only relative path)
  2. Cache-busting parameters to force browser refresh
- AlumniNavbar.vue had the correct implementation with cache-busting

**Code Before:**
```vue
<img 
  :src="user?.profile_picture || '/default-avatar.png'" 
  alt="Profile Picture"
  class="w-32 h-32 rounded-full border-4 border-white shadow-lg object-cover"
/>
```

**Code After:**
1. Added computed property in script:
```javascript
const BASE_URL = `${window.location.protocol}//${window.location.hostname}:8000`

const profilePictureUrl = computed(() => {
  const pic = user.value?.profile_picture
  if (!pic) return '/default-avatar.png'
  
  const baseUrl = pic.startsWith('http') ? pic : `${BASE_URL}${pic}`
  // Add cache-busting parameter to force refresh when profile picture changes
  const cacheBuster = `?t=${Date.now()}`
  return `${baseUrl}${cacheBuster}`
})
```

2. Updated template to use the computed property:
```vue
<img 
  :src="profilePictureUrl" 
  alt="Profile Picture"
  class="w-32 h-32 rounded-full border-4 border-white shadow-lg object-cover"
/>
```

**How It Works:**
- Builds full URL: `http://127.0.0.1:8000/media/profile_pictures/filename.jpg`
- Adds cache-busting: `http://127.0.0.1:8000/media/profile_pictures/filename.jpg?t=1730778123456`
- The `?t=Date.now()` forces browser to always fetch fresh image (not cached)
- Same implementation as AlumniNavbar.vue, ensuring consistency

**Status:** ✅ **FIXED** - Profile picture now displays correctly with cache-busting

---

## Implementation Notes

**Best Practice:** All places that display profile pictures should use the same `profilePictureUrl` pattern:
1. Build full URL with BASE_URL
2. Add `?t=${Date.now()}` cache-buster
3. Fall back to `/default-avatar.png` if no picture

**Files Using This Pattern:**
- ✅ `AlumniNavbar.vue` (already correct)
- ✅ `MyProfile.vue` (just fixed)
- Consider checking: `UserProfile.vue`, `ProfileCard.vue`, `MessageBubble.vue` for consistency

---

## Testing

**Test Rejection Flow:**
1. Go to Admin > Pending Users
2. Click on a pending user
3. Click "Reject"
4. Confirm rejection
5. ✅ Should see success alert without error messages
6. ✅ User should be removed from list

**Test Profile Picture:**
1. Go to My Profile
2. Update profile picture
3. ✅ New picture should appear immediately (cache-busted)
4. Refresh page
5. ✅ Picture should still be the updated one

---

**Summary:** Two UI bugs fixed:
- ✅ Reject user error handling
- ✅ Profile picture display with cache-busting
