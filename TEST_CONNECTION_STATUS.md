# Connection Status Testing Guide

## Problem
Even after accepting connection, user profile still shows empty data.

## Potential Causes
1. **Connection not created properly** - `is_mutual` not set to `true`
2. **Reverse connection missing** - Only one direction exists
3. **Status not 'accepted'** - Still showing as 'pending'
4. **Privacy check logic issue** - Backend checking wrong direction

## Test Steps

### Step 1: Test the Connection Acceptance Endpoint

1. **Try accepting the connection request again**
2. **Check backend terminal (Django)** for these logs:
   ```
   🔍 Accepting invitation 1 for user 5
   ✅ Found invitation: username1 → username2
   ✅ Invitation accepted successfully, mutual connection created
   ```

3. **If you see errors**, copy the full error and traceback

### Step 2: Use the Test Connection Status Endpoint

**In your browser console (F12)**, run this command:

```javascript
// Replace USER_ID with the ID of the user whose profile you're trying to view
const targetUserId = 8; // Example: the user you can't see

fetch(`http://localhost:8000/api/auth/test-connection/${targetUserId}/`, {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(data => {
  console.log('🔍 CONNECTION STATUS TEST:');
  console.log('==========================');
  console.log('Requesting User:', data.requesting_user?.name);
  console.log('Target User:', data.target_user?.name);
  console.log('');
  console.log('Forward Connection (You → Them):');
  console.log('  Exists:', data.forward_connection?.exists);
  console.log('  Is Mutual:', data.forward_connection?.is_mutual);
  console.log('  Status:', data.forward_connection?.status);
  console.log('');
  console.log('Reverse Connection (Them → You):');
  console.log('  Exists:', data.reverse_connection?.exists);
  console.log('  Is Mutual:', data.reverse_connection?.is_mutual);
  console.log('  Status:', data.reverse_connection?.status);
  console.log('');
  console.log('Summary:');
  console.log('  Are Connected:', data.is_connected);
  console.log('  Recommendation:', data.summary?.recommendation);
  console.log('');
  console.log('Full response:', data);
})
.catch(err => console.error('Error:', err));
```

### Step 3: Check Database Directly (Optional)

If you have access to the database, run this SQL:

```sql
-- Check Following records for specific users
-- Replace 5 and 8 with your user IDs
SELECT 
    id,
    follower_id,
    following_id,
    is_mutual,
    status,
    created_at
FROM auth_app_following
WHERE (follower_id = 5 AND following_id = 8)
   OR (follower_id = 8 AND following_id = 5)
ORDER BY created_at DESC;
```

**Expected Result** (if connection accepted properly):
```
id  follower_id  following_id  is_mutual  status     created_at
1   5            8             true       accepted   2025-11-25 ...
2   8            5             true       accepted   2025-11-25 ...
```

Both records should have:
- ✅ `is_mutual = true`
- ✅ `status = 'accepted'`

### Step 4: View Profile Again with Enhanced Logging

1. **Navigate to the user's profile** whose data you can't see
2. **Check backend terminal** - you should see detailed logs:

```
🔒 Filtering privacy for user 8, viewed by user 5
🔍 _is_item_visible: visibility=connections_only, requesting_user=5, target_user=8
🔍 Checking connection: user5 → user8
🔍 Connection exists (is_mutual=True, status=accepted): True
✅ Education 1 visible
✅ Work experience 1 visible
... etc
```

3. **If connection check returns False**, you'll see:
```
🔍 Connection exists (is_mutual=True, status=accepted): False
🔍 Reverse connection: user8 → user5: False
📊 All connections FROM user5: [...]
📊 All connections TO user8: [...]
🚫 Hiding education 1 (visibility: connections_only)
```

### Step 5: Frontend Console Logs

Check the frontend browser console when viewing the profile:

```
🔐 Privacy filtering - Current user: 5 Viewing user: 8
🔐 Connection status (isFollowing): true
🔐 Raw data from backend: { education: 0, work_histories: 0, ... }
✅ Backend-filtered data applied: { education: 0, workHistories: 0, ... }
⚠️ No items visible - User might have all privacy set to "connections_only" and you are not connected
```

## Common Issues & Solutions

### Issue 1: "Connection exists: False" despite accepting
**Cause**: `accept_invitation()` method didn't create reverse connection

**Solution**: Check backend logs when accepting. Should see:
```
✅ Invitation accepted successfully, mutual connection created
```

If not, the `accept_invitation()` method failed. Check for errors.

### Issue 2: "is_mutual: false" on one or both records
**Cause**: `update_mutual_status()` didn't run properly

**Fix in Django shell**:
```python
from auth_app.models import Following

# Get both connections
forward = Following.objects.get(follower_id=5, following_id=8)
reverse = Following.objects.get(follower_id=8, following_id=5)

# Manually set mutual
forward.is_mutual = True
forward.save(update_fields=['is_mutual'])

reverse.is_mutual = True
reverse.save(update_fields=['is_mutual'])

print("✅ Fixed mutual status")
```

### Issue 3: "status: pending" after accepting
**Cause**: Accept didn't save properly

**Fix in Django shell**:
```python
from auth_app.models import Following

connection = Following.objects.get(id=1)  # Use the invitation ID
connection.status = 'accepted'
connection.save()
print(f"✅ Set status to accepted for connection {connection.id}")
```

### Issue 4: Only one direction exists
**Cause**: Reverse connection wasn't created

**Fix in Django shell**:
```python
from auth_app.models import Following, CustomUser

user1 = CustomUser.objects.get(id=5)
user2 = CustomUser.objects.get(id=8)

# Create forward if missing
forward, created = Following.objects.get_or_create(
    follower=user1,
    following=user2,
    defaults={'status': 'accepted', 'is_mutual': True}
)
if created:
    print(f"✅ Created forward connection: {user1.username} → {user2.username}")

# Create reverse if missing
reverse, created = Following.objects.get_or_create(
    follower=user2,
    following=user1,
    defaults={'status': 'accepted', 'is_mutual': True}
)
if created:
    print(f"✅ Created reverse connection: {user2.username} → {user1.username}")

# Ensure both are mutual
forward.is_mutual = True
forward.status = 'accepted'
forward.save()

reverse.is_mutual = True
reverse.status = 'accepted'
reverse.save()

print("✅ Both connections now mutual and accepted")
```

## Quick Fix Script (Run in Django Shell)

```python
from auth_app.models import Following, CustomUser

def fix_connection(user1_id, user2_id):
    """Fix connection between two users"""
    user1 = CustomUser.objects.get(id=user1_id)
    user2 = CustomUser.objects.get(id=user2_id)
    
    print(f"🔧 Fixing connection between {user1.username} and {user2.username}")
    
    # Get or create both directions
    forward, f_created = Following.objects.get_or_create(
        follower=user1,
        following=user2,
        defaults={'status': 'accepted', 'is_mutual': True}
    )
    
    reverse, r_created = Following.objects.get_or_create(
        follower=user2,
        following=user1,
        defaults={'status': 'accepted', 'is_mutual': True}
    )
    
    # Update both to be mutual and accepted
    forward.status = 'accepted'
    forward.is_mutual = True
    forward.save()
    
    reverse.status = 'accepted'
    reverse.is_mutual = True
    reverse.save()
    
    print(f"✅ Forward: {forward.id} - mutual={forward.is_mutual}, status={forward.status}")
    print(f"✅ Reverse: {reverse.id} - mutual={reverse.is_mutual}, status={reverse.status}")
    print("✅ Connection fixed!")
    
    return forward, reverse

# Example usage:
# fix_connection(5, 8)  # Replace with your user IDs
```

## Verification After Fix

1. **Run the test connection endpoint** again (Step 2)
2. **Expected output**:
   ```
   Forward Connection (You → Them):
     Exists: true
     Is Mutual: true
     Status: "accepted"
   
   Reverse Connection (Them → You):
     Exists: true
     Is Mutual: true
     Status: "accepted"
   
   Summary:
     Are Connected: true
     Recommendation: "✅ Fully connected (mutual)"
   ```

3. **Refresh the user profile** - you should now see their data!

## Final Checklist

- [ ] Invitation accepted without errors (check backend logs)
- [ ] Test connection endpoint returns `is_connected: true`
- [ ] Both forward and reverse connections exist
- [ ] Both have `is_mutual: true`
- [ ] Both have `status: 'accepted'`
- [ ] User profile now shows data (education, work, etc.)
- [ ] Backend privacy logs show "✅ Visible" instead of "🚫 Hiding"

---

**If still not working after all fixes**, run the browser console test (Step 2) and copy the full output here for further debugging.
