# Testing Guide - Password Reset & Login Fixes

## Quick Test Scenarios

### Scenario 1: Forgot Password - Valid Registered Email
**Steps**:
1. Go to Login page → Click "Forgot Password?"
2. Enter a valid registered email (e.g., an account you created)
3. Click "Send Password Reset Email"

**Expected Results**:
- ✅ Success message appears: "If an account exists with this email, a password reset email has been sent..."
- ✅ Email received in inbox with subject "Alumni Mates - Password Reset"
- ✅ Email contains temporary password
- ✅ Page auto-redirects to login after 5 seconds
- ✅ User can login with temporary password
- ✅ User can change password after login

**Verify Email Contents**:
- Subject: "Alumni Mates - Password Reset"
- From: osorioroman101@gmail.com (or configured EMAIL_HOST_USER)
- Contains: "Your temporary password is: [random-12-char-password]"
- Has HTML and plain text versions
- Includes security notice about contacting support

---

### Scenario 2: Forgot Password - Invalid Email Format
**Steps**:
1. Go to Forgot Password page
2. Enter invalid email format (e.g., "notanemail", "user@.com", "user space@test.com")
3. Click "Send Password Reset Email"

**Expected Results**:
- ✅ Error message appears: "Please enter a valid email address"
- ✅ Request is NOT sent to backend
- ✅ No email is sent
- ✅ User stays on same page and can retry

**Test Cases**:
- `notanemail` → Error
- `user@` → Error
- `user@@example.com` → Error
- `user example@test.com` → Error
- `user@test` → Error (no TLD)
- `user@test.c` → Error (TLD too short)
- `user@example.com` → OK (valid format)

---

### Scenario 3: Forgot Password - Non-Existent Email
**Steps**:
1. Go to Forgot Password page
2. Enter valid email format but non-existent account (e.g., "nonexistent@example.com")
3. Click "Send Password Reset Email"

**Expected Results**:
- ✅ Same success message appears as valid email: "If an account exists..."
- ✅ NO email is sent (doesn't reveal if account exists)
- ✅ Page auto-redirects to login
- ✅ No error is shown (security best practice)

---

### Scenario 4: Login - Invalid Credentials (NO Auto-Refresh)
**Steps**:
1. Go to Login page
2. Enter valid email format but wrong password (e.g., "test@example.com" + "WrongPassword123!!")
3. Click Login or press Enter
4. Observe the page behavior

**Expected Results**:
- ✅ Error message shows: "Invalid credentials" or similar
- ✅ Page DOES NOT reload/refresh (critical fix!)
- ✅ User can immediately retry login
- ✅ No network requests after the failed login attempt
- ✅ URL stays on `/login` page

**Verify Behavior**:
- Try entering wrong password 3-5 times
- Each attempt should show error without page reload
- No browser loading indicator
- Form remains interactive

---

### Scenario 5: Login - Valid Credentials (Still Works)
**Steps**:
1. Go to Login page
2. Enter correct email and password
3. Click Login

**Expected Results**:
- ✅ User is logged in successfully
- ✅ Redirected to appropriate dashboard (alumni/admin/super-admin)
- ✅ No errors occur

---

### Scenario 6: Login - Email Format Validation
**Steps**:
1. Go to Login page
2. Try entering invalid email formats:
   - `notanemail`
   - `user@`
   - `user@@example.com`
3. Click Login

**Expected Results**:
- ✅ Error: "Invalid email format" or similar
- ✅ Request NOT sent to backend
- ✅ No page reload
- ✅ User can correct and retry

---

## Browser Dev Tools Verification

### Task 1 Verification (Forgot Password):
1. Open **Network Tab** in DevTools
2. Go to Forgot Password page
3. Enter valid email and submit
4. Look for request to `/api/auth/forgot-password/`
5. Check response:
   ```json
   {
     "detail": "If an account exists with this email, you will receive a password reset email."
   }
   ```

### Task 2 Verification (Login Fix):
1. Open **Network Tab** in DevTools
2. Go to Login page
3. Enter wrong credentials and submit
4. Look for request to `/api/auth/login/`
5. Should see `401` status code
6. Check that interceptor does NOT trigger redirect:
   - Look in **Console** for any navigation/redirect
   - Should see NO `window.location` changes
   - Should only see error response

**Console Log Check**:
- Should see: "Login error: Invalid credentials" (if logging is enabled)
- Should NOT see redirect messages

---

## Email Testing

### If Emails Not Received:
1. **Check Spam Folder**: Gmail sometimes marks automated emails as spam
2. **Check Email Settings**:
   ```
   Backend/.env should have:
   - EMAIL_HOST=smtp.gmail.com
   - EMAIL_PORT=587
   - EMAIL_USE_TLS=True
   - EMAIL_HOST_USER=osorioroman101@gmail.com
   - EMAIL_HOST_PASSWORD=gzyjxdiuyaxoxefc
   - DEFAULT_FROM_EMAIL=osorioroman101@gmail.com
   ```

3. **Test Email Service**:
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> from django.conf import settings
   >>> send_mail('Test', 'Test message', settings.DEFAULT_FROM_EMAIL, ['your-email@example.com'])
   ```

4. **Check Django Logs**:
   - Look for "Password reset email sent successfully to..."
   - Or "Failed to send password reset email..."

---

## Edge Cases to Test

### Edge Case 1: Rapid Email Submissions
**Test**: Click "Send Password Reset Email" multiple times rapidly
**Expected**: Only last request should succeed, earlier requests might be throttled by browser

### Edge Case 2: Special Characters in Email
**Test**: Email like `user+tag@example.co.uk`
**Expected**: Should be valid and work correctly

### Edge Case 3: Long Wait Time
**Test**: Submit forgot password, wait 5+ seconds before redirecting
**Expected**: Auto-redirect should still work correctly

### Edge Case 4: Browser Back Button
**Test**: 
1. Submit forgot password
2. Press browser back button during redirect countdown
**Expected**: Should return to forgot password page, not error

### Edge Case 5: Session Expiry During Login
**Test**:
1. On login page
2. Wait for session to expire (if applicable)
3. Try logging in
**Expected**: Should work normally, no session issues

---

## Database Verification

### Check User Password was Updated:
```sql
SELECT email, password FROM auth_app_customuser 
WHERE email = 'test@example.com';
-- Password hash should be different from before
-- And start with 'pbkdf2_sha256$...' (Django's format)
```

### Check No Logs of Errors:
```bash
tail -f Backend/debug.log
# Should see entries like:
# "Password reset for user: test@example.com (ID: 123)"
# "Password reset email sent successfully to test@example.com"
```

---

## Performance Considerations

### Expected Response Times:
- Forgot password form submission: **2-5 seconds** (includes email sending)
- Login form submission (invalid): **<1 second** (no page reload)
- Login form submission (valid): **1-3 seconds** (with dashboard load)

### If Slow:
- Check network latency to SMTP server
- Check database query performance
- Verify Redis is running (for caching)

---

## Success Criteria - All Tasks Complete

- [ ] Task 1: Forgot password email endpoint working
- [ ] Task 1: Random password generated and sent via email
- [ ] Task 1: Email validation regex preventing invalid formats
- [ ] Task 1: Non-existent emails handled securely
- [ ] Task 1: User can login with temporary password
- [ ] Task 2: Login with invalid credentials shows error without page reload
- [ ] Task 2: Login can be retried multiple times smoothly
- [ ] Task 2: Valid login still works correctly
- [ ] Task 2: Email validation in login matches forgot password validation
- [ ] Task 2: No browser navigation/redirects on login failure
- [ ] All 6 test scenarios above pass completely

---

## Rollback Instructions (If Issues Found)

1. **Backend Rollback**:
   ```bash
   git revert <commit-hash>
   # or manually:
   # 1. Remove ForgotPasswordView from auth_app/views/authentication.py
   # 2. Remove forgot-password import and URL from auth_app/urls.py
   ```

2. **Frontend Rollback**:
   ```bash
   git revert <commit-hash>
   # or manually:
   # 1. Revert ForgotPassword.vue to previous version
   # 2. Revert Login.vue email validation
   # 3. Revert api.js interceptor logic
   ```

3. **Restart Services**:
   ```bash
   # Kill running Django and frontend dev servers
   # Restart them fresh
   ```

---

## Support & Troubleshooting

### Issue: Email not sending
- Check `.env` SMTP settings
- Verify Gmail app password (not regular password)
- Check Gmail "Less secure apps" setting
- Look for error in `debug.log`

### Issue: Login page auto-refreshing
- Hard refresh browser (Ctrl+Shift+R)
- Clear browser cache
- Check browser console for JavaScript errors

### Issue: Forgot password page stuck
- Check Network tab for pending requests
- Verify backend is running
- Check API base URL in `Frontend/src/services/api.js`

---

**Last Updated**: November 5, 2025  
**Implementation Status**: ✅ COMPLETE
