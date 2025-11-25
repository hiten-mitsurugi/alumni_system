# Verification Steps for Profile Parity Fix

## Quick Test Guide

### Step 1: Start the Application
```powershell
# Terminal 1: Backend
cd Backend
.\env\Scripts\activate
python manage.py runserver

# Terminal 2: Frontend  
cd Frontend
npm run dev
```

### Step 2: Test Own Profile (MyProfile)

1. **Navigate to your profile**
   - Click on your profile or go to `/alumni/profile`

2. **Test Publications**
   - Click "Add Publication"
   - Fill in the form:
     - Title: "Test Publication 2025"
     - Publication Type: "Journal Article"
     - Co-Authors: Add at least one author
     - Year Published: 2025
     - Place of Publication: "Test Publisher"
     - URL: Any valid URL
   - Click Save
   - **Expected**: Publication appears immediately
   - Refresh the page (F5)
   - **Expected**: Publication still appears

3. **Test Career Enhancement (Certificates)**
   - Click "Add Certificate" in Career Enhancement section
   - Fill in:
     - Certificate Type: "Professional License"
     - Certificate Number: "TEST-2025-001"
     - Issuing Body: "Test Certification Board"
     - Date Issued: Today's date
     - Expiry Date: One year from today
   - Upload a test file (optional)
   - Click Save
   - **Expected**: Certificate appears with all details
   - Refresh the page (F5)
   - **Expected**: Certificate persists with:
     - ✅ Green "Active" badge (if not expired)
     - All fields visible (type, number, issuing body, dates, file link)

4. **Test Trainings**
   - Add a training with title, organization, and dates
   - **Expected**: Saves and persists after refresh

5. **Test Skills**
   - Add a new skill
   - **Expected**: Appears immediately and persists

### Step 3: Test Other User's Profile (UserProfile)

1. **Open browser developer tools** (F12)
2. **Go to Console tab**
3. **Navigate to another user's profile**
   - Click on any connection or suggested user
   - URL should be `/alumni/profile/{username}`

4. **Check Console Logs**
   Look for these log messages:
   ```
   ✅ "UserProfile API response:" - Should show full data structure
   ✅ "Available fields in response:" - Should list all fields
   ✅ "Skills data in response:" - Should show user_skills array
   ✅ "🔐 Other user profile - using user_skills from response:" - Skills count
   ✅ "🔐 Memberships: X (backend-filtered)"
   ✅ "🔐 Recognitions: X (backend-filtered)"
   ✅ "🔐 Trainings: X (backend-filtered)"
   ✅ "🔐 Publications: X (backend-filtered)"
   ✅ "🔐 Career Enhancement: X certificates"
   ```

5. **Verify Data Parity**
   - Compare the sections between MyProfile and UserProfile
   - **Expected**: If you're viewing your own profile via username URL, ALL data should match
   - **Expected**: If viewing another user, data respects privacy settings:
     - Items with "everyone" privacy: Always visible
     - Items with "connections_only" privacy: Only visible if you're connected

### Step 4: Test Privacy Filtering

1. **In MyProfile, set a publication to "connections_only"**
   - Edit privacy settings for one publication

2. **View from another account (not connected)**
   - **Expected**: Publication is hidden

3. **View from connected account**
   - **Expected**: Publication is visible

### Step 5: Backend Console Check

Check the Django runserver terminal for these logs:
```
✅ "🔓 Own profile - returning all data for user X"
   OR
✅ "🔒 Filtering privacy for user X, viewed by user Y"
✅ "🔍 DEBUG get_education: Found N records for user X"
✅ No error tracebacks or 400/500 responses
```

## Common Issues and Solutions

### Issue: Publications return 400 Bad Request
**Check**:
1. Browser console for error details
2. Backend terminal for DRF validation errors

**Solution**:
- Ensure all required fields are filled (title, authors, date_published)
- Check `PROFILE_PARITY_FIX.md` for field mapping

### Issue: Certificates disappear after refresh
**Check**:
1. Browser console for `careerEnhancement.value` after page load
2. Network tab → `enhanced-profile` response → Look for `certificates` array

**Solution**:
- Should already be fixed
- If still occurring, check if backend is returning `certificates` at top level

### Issue: Skills not showing for other users
**Check**:
1. Console log: "Skills data in response:"
2. Network tab → `enhanced-profile` response → Look for `user_skills` array

**Solution**:
- Backend should include `user_skills` in response
- Privacy filtering is now backend-side only

### Issue: Different data between MyProfile and UserProfile (for same user)
**Check**:
1. Console logs in both views
2. Compare the API responses in Network tab

**Solution**:
- Both should fetch from `/auth/enhanced-profile/` (or variant)
- Both should map data identically
- Check `PROFILE_PARITY_FIX.md` for mapping details

## Success Criteria

✅ **Publications**: Save, persist, and display identically in both views
✅ **Certificates**: Save with all fields, persist after refresh, show correct active/expired badge
✅ **Trainings**: Display all fields correctly in both views
✅ **Skills**: Show the same skills in both views (respecting privacy)
✅ **Memberships/Recognitions**: Display identically
✅ **Privacy Filtering**: Works correctly (backend-side)
✅ **Error Handling**: Clear error messages for validation failures
✅ **Console Logs**: No errors, only informational logs

## Performance Check

1. **Open Network tab** (F12 → Network)
2. **Navigate to a user profile**
3. **Count API calls**:
   - ✅ Should see 2-3 calls max:
     1. `/auth/enhanced-profile/...` (main data)
     2. `/auth/user/` (current user check)
     3. `/auth/connections/` (following status)
   - ❌ Should NOT see multiple calls to `/auth/profile/field-update/` per item

4. **Check response times**:
   - Enhanced-profile call should complete in < 1 second
   - Total page load should be < 2 seconds

## Final Verification

Open **MyProfile** and **UserProfile (own)** side-by-side:
```
Tab 1: http://localhost:5173/alumni/profile
Tab 2: http://localhost:5173/alumni/profile/YOUR_USERNAME
```

**Compare**:
- [ ] Profile header (name, headline, education info)
- [ ] About section
- [ ] Contact info
- [ ] Education entries
- [ ] Work experience entries
- [ ] Skills list
- [ ] Achievements
- [ ] Memberships
- [ ] Recognitions
- [ ] Trainings
- [ ] Publications
- [ ] Career Enhancement (certificates + CSE status)

**Result**: Should be **100% identical** (except for edit buttons)

---

If all checks pass ✅, the fix is complete and working correctly!

If any checks fail ❌, refer to `PROFILE_PARITY_FIX.md` for detailed troubleshooting.
