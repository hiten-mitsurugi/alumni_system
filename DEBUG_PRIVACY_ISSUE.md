# Privacy Filtering Debug Guide

## Issue Detected
User profile showing empty data even though the user has information.

## Root Cause Analysis

### Backend Privacy Logic (`EnhancedUserDetailSerializer`)
The backend filters items based on:
1. **`visibility == 'everyone'`** → Always visible
2. **`visibility == 'only_me'`** → Never visible to others
3. **`visibility == 'connections_only'`** → Visible only if:
   - Requesting user is authenticated (not anonymous)
   - **AND** Following relationship exists with:
     - `follower = requesting_user`
     - `following = target_user`
     - **`is_mutual = True`** ← KEY REQUIREMENT
     - **`status = 'accepted'`** ← KEY REQUIREMENT

### Frontend Connection Check
The frontend checks `isFollowing` by looking at the `/auth/connections/` endpoint and checking if the user is in the `following` list. However:
- This only checks if **you are following them**
- It does NOT check if the relationship is **mutual** and **accepted**

## Why Data is Empty

### Scenario 1: Not Connected
- `isFollowing = false`
- Backend filters out all items with `visibility = 'connections_only'`
- Only items with `visibility = 'everyone'` are shown
- **Result**: Empty profile if all items are set to `connections_only`

### Scenario 2: Following but Not Mutual
- `isFollowing = true` (you follow them)
- Backend checks: `is_mutual = True` → **FAILS**
- Backend filters out all items with `visibility = 'connections_only'`
- **Result**: Empty profile despite "following" them

### Scenario 3: Privacy Not Set
- Items without explicit privacy settings default to `connections_only`
- Backend filters them out unless you're mutually connected
- **Result**: Empty profile for non-connected users

## Debugging Steps

### Step 1: Check Backend Logs
Look for these messages in the Django runserver terminal:
```
🔒 Filtering privacy for user X, viewed by user Y
🚫 Hiding education N (visibility: connections_only)
🚫 Hiding work experience M (visibility: connections_only)
... etc
```

### Step 2: Check Frontend Console
The new logs will show:
```
🔐 Privacy filtering - Current user: X Viewing user: Y
🔐 Connection status (isFollowing): false
🔐 Raw data from backend: { education: 0, work_histories: 0, ... }
⚠️ No items visible - User might have all privacy set to "connections_only" and you are not connected
💡 To see this user's profile, try connecting with them first
```

### Step 3: Check Connection Status in Database
Open Django shell or database:
```sql
SELECT * FROM auth_app_following 
WHERE follower_id = <your_user_id> 
  AND following_id = <target_user_id>;
```

Check:
- Does a record exist?
- `is_mutual` = True or False?
- `status` = 'accepted', 'pending', or 'rejected'?

### Step 4: Check Privacy Settings
```sql
SELECT * FROM auth_app_fieldprivacysetting 
WHERE user_id = <target_user_id>;
```

Check:
- Are there privacy settings defined?
- What are the `visibility` values? ('everyone', 'connections_only', 'only_me')
- Are items defaulting to `connections_only`?

## Solutions

### Option 1: Set Items to "Everyone" (User Action)
The target user needs to:
1. Go to their profile
2. Edit privacy settings for each item
3. Change visibility from "connections_only" to "everyone"

### Option 2: Connect with the User (Viewer Action)
You need to:
1. Send a connection request
2. Wait for them to accept
3. Ensure the relationship becomes **mutual** and **accepted**

### Option 3: Modify Default Privacy (Development)
Change the default privacy setting from `connections_only` to `everyone`:

**Backend**: In `FieldPrivacySetting.get_user_field_visibility()`:
```python
# Current default
return getattr(setting, 'visibility', 'connections_only')

# Change to:
return getattr(setting, 'visibility', 'everyone')
```

### Option 4: Show Placeholder When Empty (UX Improvement)
Add a message in UserProfile when all data is filtered:

```vue
<div v-if="totalVisibleItems === 0 && !isOwnProfile" class="text-center py-8">
  <p class="text-gray-600">
    <template v-if="!isFollowing">
      Connect with {{ user?.first_name }} to view their profile information.
    </template>
    <template v-else>
      This user hasn't added any information yet, or their privacy settings restrict visibility.
    </template>
  </p>
  <button 
    v-if="!isFollowing"
    @click="connectUser" 
    class="mt-4 px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700"
  >
    Send Connection Request
  </button>
</div>
```

## Testing the Fix

### Test 1: Verify Backend Filtering
1. Open backend terminal (Django runserver)
2. Navigate to a user profile in the frontend
3. Check backend logs for:
   ```
   🔒 Filtering privacy for user X, viewed by user Y
   🚫 Hiding education 1 (visibility: connections_only)
   ```
4. This confirms backend is filtering correctly

### Test 2: Verify Frontend Receives Filtered Data
1. Open browser console (F12)
2. Navigate to a user profile
3. Check logs:
   ```
   🔐 Raw data from backend: { education: 0, work_histories: 0, ... }
   ```
4. If all zeros, backend is filtering everything out
5. Check the helpful warning message explaining why

### Test 3: Connect and Retest
1. Send a connection request to the user
2. Have them accept (or accept if testing with your own accounts)
3. Refresh the user profile
4. Check backend logs - items should now be visible:
   ```
   🔒 Filtering privacy for user X, viewed by user Y
   ✅ Education 1 visible (is_mutual=True, status=accepted)
   ```

### Test 4: Change Privacy Settings
1. As the target user, go to MyProfile
2. Edit an item (e.g., education)
3. Change privacy to "everyone"
4. As the viewer, refresh their profile
5. The item should now be visible even without connection

## Expected Behavior (After Fix)

### When NOT Connected:
- Frontend shows: "Connect with [User] to view their profile information"
- Backend logs: "🚫 Hiding..." for all `connections_only` items
- Frontend logs: "⚠️ No items visible - not connected"
- Only items with `visibility='everyone'` are shown

### When Connected (Mutual + Accepted):
- Backend logs: "✅ Showing..." for `connections_only` items
- Frontend shows all visible items
- Privacy settings respected

### When Viewing Own Profile:
- Backend logs: "🔓 Own profile - returning all data"
- Frontend shows everything
- No filtering applied

## Quick Fix Checklist

- [ ] Backend logs show privacy filtering is working
- [ ] Frontend logs show helpful debug information
- [ ] Frontend displays connection prompt when data is empty
- [ ] Connecting with user reveals their profile data
- [ ] Own profile always shows all data
- [ ] Privacy settings are respected (everyone vs connections_only)

## Database Queries for Manual Check

```sql
-- Check if users are connected
SELECT 
    f.id,
    f.follower_id,
    f.following_id,
    f.is_mutual,
    f.status,
    u1.username as follower_username,
    u2.username as following_username
FROM auth_app_following f
JOIN auth_app_customuser u1 ON f.follower_id = u1.id
JOIN auth_app_customuser u2 ON f.following_id = u2.id
WHERE (f.follower_id = <user1_id> AND f.following_id = <user2_id>)
   OR (f.follower_id = <user2_id> AND f.following_id = <user1_id>);

-- Check privacy settings for a user
SELECT 
    field_name,
    visibility,
    updated_at
FROM auth_app_fieldprivacysetting
WHERE user_id = <target_user_id>
ORDER BY updated_at DESC;

-- Check user's data existence
SELECT 
    (SELECT COUNT(*) FROM auth_app_education WHERE user_id = <user_id>) as education_count,
    (SELECT COUNT(*) FROM auth_app_workhistory WHERE user_id = <user_id>) as work_count,
    (SELECT COUNT(*) FROM auth_app_achievement WHERE user_id = <user_id>) as achievement_count,
    (SELECT COUNT(*) FROM auth_app_userskill WHERE user_id = <user_id>) as skill_count;
```

---

**Summary**: The privacy filtering is working as designed. Empty profiles occur when:
1. User hasn't added information, OR
2. All items are set to `connections_only` and viewer is not connected (mutual + accepted)

The fix improves debugging and user experience by adding clear logging and helpful messages.
