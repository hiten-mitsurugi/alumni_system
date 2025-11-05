# Implementation Flow Diagrams

## Task 1: Forgot Password Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER STARTS HERE                             │
│              Login Page → Click "Forgot Password?"               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌──────────────────────────────────────┐
        │   ForgotPassword.vue - Email Step    │
        │  ✓ User enters: test@example.com     │
        │  ✓ Frontend validates regex          │
        └────────────┬─────────────────────────┘
                     │ POST /api/auth/forgot-password/
                     │ { email: "test@example.com" }
                     ▼
        ┌──────────────────────────────────────────────────┐
        │     Backend: ForgotPasswordView                   │
        │  1. Validate email format with regex             │
        │     ✓ /^[a-zA-Z0-9._%+-]+@...$/                  │
        │  2. Check if email exists in CustomUser          │
        │     ✓ CustomUser.objects.filter(email=...)       │
        └────┬─────────────────────────────────────────────┘
             │
             ├─────────────────────────┬────────────────┐
             │                         │                │
    Email Found ✓            Not Found/Invalid ✗
             │                         │
             ▼                         ▼
    ┌──────────────────┐     ┌─────────────────────┐
    │  Generate Pass   │     │ Return generic msg  │
    │ K8$xP2@mL9vQ    │     │ "If account exists" │
    │  (12 chars)     │     │ (security: no leak) │
    └────────┬────────┘     └──────────┬──────────┘
             │                         │
             ▼                         ▼
    ┌──────────────────┐     ┌─────────────────────┐
    │ Update Database  │     │ Log attempt (admin) │
    │ user.set_password│     └──────────┬──────────┘
    │      ()          │                │
    └────────┬────────┘                │
             │                         │
             ▼                         ▼
    ┌──────────────────────────────────────┐
    │   RESPONSE 200 OK                    │
    │   { "detail": "If an account        │
    │            exists..." }              │
    │   HTTP 200 (same for both cases)    │
    └────────┬───────────────────────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ Send Email              │
    │ ✓ Subject: "Alumni     │
    │   Mates - Password     │
    │   Reset"               │
    │ ✓ To: test@example.com │
    │ ✓ Password: K8$xP2...  │
    │ ✓ HTML + Plain Text    │
    └────────┬────────────────┘
             │ (Gmail SMTP)
             ▼
    ┌─────────────────────────┐
    │ Frontend Gets Response  │
    │ ✓ Shows success message │
    │ ✓ Auto-redirect to login│
    │   (after 5 seconds)     │
    └────────┬────────────────┘
             │
             ▼
    ┌─────────────────────────┐
    │ USER CHECKS EMAIL       │
    │ ✓ Inbox or Spam Folder  │
    │ ✓ Copies temp password  │
    │ ✓ Logs in with temp pwd │
    │ ✓ Changes password      │
    └─────────────────────────┘
```

---

## Task 2: Login Auto-Refresh Fix

```
BEFORE FIX (Problem):
═══════════════════════════════════════════

User enters: email + wrong password
            │
            ▼
Frontend validates format ✓
            │
            ▼
POST /api/auth/login/
            │
            ▼
Backend returns 401 Unauthorized
            │
            ▼
API Interceptor sees 401
    │
    ├─ OLD BEHAVIOR (BUG):
    │   Always redirect to /login
    │   │
    │   ▼
    │  window.location.href = '/login'
    │   │
    │   ▼
    │  FULL PAGE RELOAD ❌
    │   │
    │   ▼
    │  User annoyed - loses form state
    │
    └─ User wants to retry immediately


AFTER FIX (Solution):
═══════════════════════════════════════════

User enters: email + wrong password
            │
            ▼
Frontend validates format ✓
            │
            ▼
POST /api/auth/login/
            │
            ▼
Backend returns 401 Unauthorized
            │
            ▼
API Interceptor sees 401
    │
    ├─ NEW BEHAVIOR (FIXED):
    │   Check: Does user have existing token?
    │   │
    │   ├─ NO token (Login attempt) ← USER IS HERE
    │   │  │
    │   │  ▼
    │   │  Don't redirect! Just reject promise ✓
    │   │  │
    │   │  ▼
    │   │  Frontend catches error
    │   │  │
    │   │  ▼
    │   │  Shows: "Invalid credentials" error ✓
    │   │  │
    │   │  ▼
    │   │  NO PAGE RELOAD ✓
    │   │  │
    │   │  ▼
    │   │  User can retry immediately ✓
    │   │
    │   └─ YES token (Authenticated user, expired token)
    │      │
    │      ▼
    │      Try token refresh
    │      │
    │      ├─ Refresh succeeds → Retry request
    │      │
    │      └─ Refresh fails → Redirect to login
```

---

## Email Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│  Backend ForgotPasswordView                              │
│  ✓ Email: test@example.com                              │
│  ✓ Found in database                                    │
│  ✓ Password: K8$xP2@mL9vQ                               │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
            ┌────────────────────────────┐
            │ EmailMultiAlternatives     │
            │ from: settings.DEFAULT...  │
            │ to: test@example.com       │
            │ subject: "Alumni Mates..." │
            └────────────┬───────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
            ▼                         ▼
    ┌─────────────────┐     ┌──────────────────┐
    │ Plain Text Body │     │ HTML Body        │
    │ ─────────────── │     │ ──────────────── │
    │ Hello [Name],   │     │ Professional     │
    │                 │     │ formatted with   │
    │ Password:       │     │ - Branding       │
    │ K8$xP2@mL9vQ   │     │ - Styling        │
    │                 │     │ - Security info  │
    │ Contact support │     │ - Images OK      │
    │ if unauthorized │     │                  │
    └────────┬────────┘     └────────┬─────────┘
             │                       │
             └───────────┬───────────┘
                         │
                    SMTP Server
                    (Gmail)
                         │
                    osorioroman101@
                    gmail.com
                         │
                         ▼
            ┌─────────────────────────┐
            │ USER'S EMAIL INBOX      │
            │ ─────────────────────── │
            │ From: osorioroman101... │
            │ Subject: Alumni Mates   │
            │          Password Reset │
            │                         │
            │ Body:                   │
            │ Your temp password:     │
            │ K8$xP2@mL9vQ           │
            │                         │
            │ [Beautiful HTML view]   │
            │ or                      │
            │ [Plain text fallback]   │
            └─────────────────────────┘
```

---

## API Response Codes

```
Forgot Password Endpoint: POST /api/auth/forgot-password/

┌─────────────────────────────────────────────────────────┐
│  HTTP 200 OK                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │ {                                                  │ │
│  │   "detail": "If an account exists with this       │ │
│  │    email, you will receive a password reset       │ │
│  │    email."                                        │ │
│  │ }                                                 │ │
│  │                                                    │ │
│  │ ✓ Returned for BOTH:                              │ │
│  │   - Valid registered email (password sent)        │ │
│  │   - Non-existent email (no password sent)         │ │
│  │   (Security: doesn't reveal if email exists)      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  HTTP 400 BAD REQUEST                                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │ {                                                  │ │
│  │   "detail": "Please enter a valid email          │ │
│  │    address"                                       │ │
│  │ }                                                 │ │
│  │                                                    │ │
│  │ ✓ Returned for:                                   │ │
│  │   - Invalid email format                          │ │
│  │   - Empty email field                             │ │
│  │   - Malformed email                               │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  HTTP 500 INTERNAL SERVER ERROR                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │ {                                                  │ │
│  │   "detail": "Password was reset but email        │ │
│  │    delivery failed. Please contact support."     │ │
│  │ }                                                 │ │
│  │                                                    │ │
│  │ ✓ Returned for:                                   │ │
│  │   - SMTP connection errors                        │ │
│  │   - Email sending failure                         │ │
│  │   - Database errors                               │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Login API Interceptor Logic

```
API Request made (e.g., POST /api/auth/login/)
    │
    ▼
Response received
    │
    ├─ Success (200, 201, etc.) ✓
    │   │
    │   └─ Return response to caller
    │
    └─ Error (4xx, 5xx)
        │
        └─ Check status code
           │
           ├─ 401 Unauthorized
           │   │
           │   ├─ Check: authStore.token exists?
           │   │   │
           │   │   ├─ YES: User has token (Authenticated, expired)
           │   │   │   │
           │   │   │   ├─ Try refresh token
           │   │   │   │
           │   │   │   ├─ Success: Retry original request ✓
           │   │   │   │
           │   │   │   └─ Fail: Logout + Redirect /login
           │   │   │
           │   │   └─ NO: User has no token (Login attempt)
           │   │       │
           │   │       ├─ Don't redirect ✓
           │   │       │
           │   │       └─ Reject error (show to user)
           │   │
           │   └─ Mark as handled (don't retry)
           │
           ├─ 403 Forbidden
           │   │
           │   ├─ Check: Is it auth-related error?
           │   │   │
           │   │   ├─ YES + token exists:
           │   │   │   └─ Try refresh (same as 401)
           │   │   │
           │   │   └─ NO or no token:
           │   │       └─ Pass error through (don't redirect)
           │   │
           │   └─ Mark as handled (don't retry)
           │
           └─ Other (4xx, 5xx)
               │
               └─ Pass error through
```

---

## Data Flow - Password Reset to Login

```
STEP 1: Password Generation
═════════════════════════════
User clicks: Request Password Reset
    │
    ▼
Backend generates: K8$xP2@mL9vQ
    │ (12 random characters)
    │ Uppercase: K, P, M, L, Q
    │ Lowercase: x, m, v
    │ Digits: 8, 2, 9
    │ Special: $, @, !, %
    ▼
Saved to DB: user.set_password(pwd)
    │
    ▼
Password stored as: pbkdf2_sha256$...encrypted...
    │ (One-way hash using Django)
    ▼


STEP 2: Email Delivery
═════════════════════════════
Generated password: K8$xP2@mL9vQ
    │
    ▼
Email template builds:
    ├─ Subject: "Alumni Mates - Password Reset"
    ├─ From: osorioroman101@gmail.com
    ├─ To: test@example.com
    │
    └─ Body (HTML):
        ├─ Header with logo
        ├─ "Hello [FirstName],"
        ├─ Highlight: K8$xP2@mL9vQ
        └─ Security notice
    │
    ▼
Sent via Gmail SMTP
    │
    ▼
Arrives in user inbox
    │
    ▼


STEP 3: User Login
═════════════════════════════
User receives email
    │ Reads: K8$xP2@mL9vQ
    ▼
User goes to login page
    │
    ├─ Email: test@example.com
    ├─ Password: K8$xP2@mL9vQ
    │
    ▼
Backend validates:
    │
    ├─ Hash(K8$xP2@mL9vQ) == stored_hash?
    │
    ▼
✓ Match! User logged in
    │
    ▼
User changes password
    │
    └─ Old: K8$xP2@mL9vQ (temporary)
    └─ New: SecurePassword123! (permanent)
       │
       ▼
    New password hashed and saved
```

---

## File Structure Before & After

```
Before Implementation:
═══════════════════════════════════════════

auth_app/
  ├── views/
  │   ├── authentication.py  (no forgot-password endpoint)
  │   └── ...
  └── urls.py  (no forgot-password route)

ForgotPassword.vue
  ├── Multi-step flow (email → code → password)
  ├── Expects /auth/forgot-password/ ❌ (doesn't exist)
  └── Expects /auth/reset-password/ ❌ (doesn't exist)

api.js
  └── Auto-redirects on 401 (causes page reload)


After Implementation:
═══════════════════════════════════════════

auth_app/
  ├── views/
  │   ├── authentication.py
  │   │   ├── RegisterView
  │   │   ├── LoginView
  │   │   ├── LogoutView
  │   │   ├── ConfirmTokenView
  │   │   ├── CheckEmailExistsView
  │   │   └── ForgotPasswordView ✅ (NEW)
  │   └── ...
  └── urls.py
      ├── 'login/'
      ├── 'register/'
      ├── 'forgot-password/' ✅ (NEW)
      └── ...

ForgotPassword.vue
  ├── Single-step flow (email only) ✅
  ├── Can call /auth/forgot-password/ ✅
  ├── Stricter email validation ✅
  └── Auto-redirects to login ✅

api.js
  └── Checks token before redirect ✅
      └── Only redirects if authenticated ✅
```

---

## Key Improvements Summary

```
BEFORE → AFTER
═════════════════════════════════════════════════════════

❌ No forgot password endpoint
✅ New /api/auth/forgot-password/ endpoint

❌ No email sending capability
✅ Sends professional HTML emails

❌ Weak email validation
✅ Strict RFC5322 regex validation

❌ Page reloads on login failure
✅ Shows error without reload

❌ Non-existent endpoint called
✅ Proper backend implementation

❌ Multi-step password reset flow
✅ Simple single-step flow

❌ No security best practices
✅ Generic error messages (no email leaking)

❌ Annoying UX on login retry
✅ Smooth retry experience
```

---

**Date**: November 5, 2025  
**Status**: ✅ COMPLETE AND DOCUMENTED
