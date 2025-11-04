# Updated Registration Flow with Survey Consent

## Complete Registration Flow (Latest Version)

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   ALUMNI REGISTRATION SYSTEM v2.0                        │
│                     (With Survey Consent Added)                          │
└──────────────────────────────────────────────────────────────────────────┘

                              HOME PAGE
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                [LOGIN]                     [REGISTER]
                    │                           │
    ┌───────────────┴────────────┐              │
    │                            │              │
[FORGOT PASSWORD]     [NORMAL LOGIN]            │
    │                            │              │
    │                    ┌───────┴──────────────┘
    │                    │
    │            STEP 1: Verify Alumni Directory
    │                    │
    │            ┌───────┴──────────┐
    │            │                  │
    │      [NOT FOUND]         [FOUND] ✓
    │            │                  │
    │         (Error)         STEP 2: Personal Info + T&C
    │                              │
    │                    ┌─────────┴──────────┐
    │                    │                    │
    │            [T&C CHECKBOX] ← [T&C LINK]
    │            [TERMS MODAL]      ↓
    │                (Modal Opens)   │
    │                    │           │
    │            ┌───────┴───────────┘
    │            │
    │         STEP 3: Verification Agreement
    │            │
    │    ┌───────┴────────────────┐
    │    │                        │
    │ [PROCEED] ─→            [GO BACK] → Edit PersonalInfo
    │    │                        │
    │    │                   [SKIP] → STEP 4
    │    │
    │ STEP 4: Survey Consent ✨ NEW
    │    │
    │    ├──────────────────────────────────────┐
    │    │                                      │
    │ [Accept & Proceed] ───→ SURVEYS    [Decline & Submit]
    │    │                       │              │
    │    │    STEP 5+: Survey   │              │
    │    │    Questions 1-N     │              │
    │    │        ...           │              │
    │    │    Question N        │              │
    │    │        │             │              │
    │    └────────┴─────────────┘              │
    │            │                            │
    │    STEP N+1: Final Submission           │
    │            │◄────────────────────────────┘
    │            │
    │ [SUBMIT REGISTRATION]
    │            │
    │ Success/Pending Approval
    │            │
    └────→ Return to Login

```

---

## Step-by-Step Breakdown

### Step 1: Alumni Directory Verification (Auto-proceeds)
```
┌─────────────────────────────────────────┐
│ Enter Alumni Details:                   │
│ • First Name                            │
│ • Last Name                             │
│ • Program                               │
│ • Year Graduated                        │
│                                         │
│ [Verify Alumni]                         │
│      ↓                                  │
│  Alumni Database Lookup                 │
│      ↓                                  │
│  ✓ Found → Proceed Automatically       │
│  ✗ Not Found → Error                    │
└─────────────────────────────────────────┘
```

### Step 2: Personal & Demographic Information
```
┌──────────────────────────────────────────┐
│ Personal Details:                        │
│ • Email                                  │
│ • Password (with T&C checkbox below)    │
│ • Address (Present & Permanent)         │
│ • Gender, Civil Status                  │
│ • Employment Status                     │
│ • Family Information                    │
│ • Government ID, Profile Pic            │
│                                         │
│ ☐ I agree to Terms & Conditions        │
│   [Read T&C Link] → Opens Modal        │
│                                         │
│ [Proceed] (if T&C checked)              │
└──────────────────────────────────────────┘
```

### Step 3: Verification Agreement
```
┌──────────────────────────────────────────┐
│ Please Review Your Information           │
│                                         │
│ Email: your@email.com                   │
│ Name: Juan Dela Cruz                    │
│ Address: Manila, Philippines            │
│ Employment: Employed Locally            │
│ [View Full Details ▼]                   │
│                                         │
│ ☐ I confirm all information is correct │
│                                         │
│ [Go Back]  [Proceed]  [Skip & Register]│
└──────────────────────────────────────────┘
```

### Step 4: Survey Consent ✨ NEW
```
┌──────────────────────────────────────────┐
│  We Value Your Insights 📊              │
│  Help us understand your career journey │
│                                         │
│  SURVEY INVITATION & CONSENT            │
│  ┌────────────────────────────────────┐ │
│  │ We would like to invite you to     │ │
│  │ participate in our Alumni Tracer   │ │
│  │ Survey. Your participation is      │ │
│  │ entirely voluntary...              │ │
│  └────────────────────────────────────┘ │
│                                         │
│  PURPOSE OF THIS SURVEY                 │
│  ✓ Career Development                  │
│  ✓ Educational Impact                  │
│  ✓ Institutional Improvement           │
│  ✓ Alumni Network                      │
│                                         │
│  HOW YOUR RESPONSES HELP US             │
│  [Curriculum] [Student Prep]           │
│  [Strategy]   [Networking]             │
│                                         │
│  SURVEY INFORMATION                     │
│  Time: 10-15 min | Questions: 15-25   │
│  Confidentiality: Protected | Opt-in  │
│                                         │
│  DATA PROTECTION & CONFIDENTIALITY     │
│  ✓ All information kept confidential   │
│  ✓ Statistical analysis only           │
│  ✓ Data stored securely                │
│  ✓ Can withdraw anytime                │
│                                         │
│  [Decline & Submit] [Accept & Proceed] │
│         (Skip Surveys)   (Go to Q1)    │
└──────────────────────────────────────────┘
```

### Step 5+: Dynamic Survey Questions (IF ACCEPTED)
```
┌──────────────────────────────────────────┐
│ Survey Question 1 of N                   │
│                                         │
│ Category: Current Employment             │
│                                         │
│ Question 1: Are you currently employed? │
│ ○ Yes  ○ No  ○ Self-employed  ○ Other  │
│                                         │
│ Question 2: Industry sector?             │
│ [Dropdown with options]                 │
│                                         │
│ Question 3: Your role?                  │
│ [Text input]                            │
│                                         │
│ [Back]                    [Next Step]    │
└──────────────────────────────────────────┘
```

### Final Step: Submit Registration
```
┌──────────────────────────────────────────┐
│ FINAL SUBMISSION                        │
│                                         │
│ Review All Information:                 │
│ ✓ Alumni Verified                       │
│ ✓ Personal Info Complete                │
│ ✓ Agreement Accepted                    │
│ ✓ Survey Data: [Accepted/Declined]     │
│                                         │
│ [Submit Registration]                   │
│         ↓                               │
│ Processing...                           │
│         ↓                               │
│ ✓ Registration Successful               │
│ Your account is pending admin approval  │
└──────────────────────────────────────────┘
```

---

## Decision Tree

```
START REGISTRATION
        │
        ▼
Step 1: Alumni Verification
        │
    ┌───┴───┐
    │       │
  ✓Found  ✗Not Found
    │       │
    ▼       └──→ Error Screen
Step 2: Personal Info + T&C

    ┌─────────────────────┐
    │                     │
 T&C Not Checked     T&C Checked ✓
    │                     │
    └─────────────────────┘
    (Can't proceed)        ▼
                      Step 3: Verify Data
                           │
                    ┌──────┼──────┐
                    │      │      │
                 Go Back Confirm  Skip
                    │      │      │
                    │      ▼      │
              Edit P2   Step 4:   │
                        Consent   │
                           │      │
                      ┌─────┴─┬───┘
                      │       │
                   Accept  Decline
                      │       │
                      │       └──→ Submit
                      │            │
                      ▼            ▼
                  Survey Q1      Success
                      │           (No surveys)
                   ... Qs
                      │
                      ▼
                   Submit
                      │
                      ▼
                   Success
                (With surveys)
```

---

## Data Flow

```
USER REGISTRATION DATA
        │
        ├─ Step 1 Data
        │  └─ first_name, last_name, program, year_graduated
        │
        ├─ Step 2 Data
        │  ├─ email, password, contact_number
        │  ├─ address data (present & permanent)
        │  ├─ gender, civil_status, employment_status
        │  ├─ family_info
        │  ├─ government_id, profile_picture
        │  └─ agreed_to_terms: true ✓
        │
        ├─ Step 3 Data
        │  └─ (All Step 2 data confirmed)
        │
        ├─ Step 4 Data
        │  └─ survey_consent_given: true/false ✨ NEW
        │
        └─ Step 5+ Data (IF consent_given = true)
           ├─ survey_responses: [...]
           └─ (Only included if accepted)
                
                ↓
        
        FINAL SUBMISSION
        │
        ├─ All user data
        ├─ All survey responses (if consented)
        ├─ Timestamps
        └─ Status: pending_approval
```

---

## API Submission Scenarios

### Scenario A: User Accepts All & Completes Surveys
```
POST /auth/register/
{
  "first_name": "Juan",
  "email": "juan@example.com",
  "password": "SecurePass123!",
  "address_data": {...},
  "agreed_to_terms": true,           ← Step 2 T&C
  "survey_consent_given": true,      ← Step 4 consent ✨
  "survey_responses": [               ← Step 5+ responses
    { question_id: 1, answer: "Yes" },
    { question_id: 2, answer: "IT" },
    ...
  ]
}
```

### Scenario B: User Accepts T&C but Declines Surveys
```
POST /auth/register/
{
  "first_name": "Juan",
  "email": "juan@example.com",
  "password": "SecurePass123!",
  "address_data": {...},
  "agreed_to_terms": true,           ← Step 2 T&C
  "survey_consent_given": false,     ← Declined surveys ✨
  "survey_responses": []             ← Empty
}
```

### Scenario C: User Skips Verification & Declines Surveys
```
POST /auth/register/
{
  "first_name": "Juan",
  "email": "juan@example.com",
  "password": "SecurePass123!",
  "address_data": {...},
  "agreed_to_terms": true,           ← Still required
  "survey_consent_given": false,     ← Skipped at Step 3
  "survey_responses": []             ← Empty
}
```

---

## Dynamic Step Counting

### Total Steps Calculation
```javascript
// Base static steps: 4
// 1. Alumni Verification
// 2. Personal Info + T&C
// 3. Verification Agreement
// 4. Survey Consent ✨ NEW

const staticSteps = 4;

// Conditional survey steps
if (surveyConsentGiven === true) {
  visibleSurveySteps = surveyCategories.length;
  // Example: 7 survey categories = 7 survey steps
} else {
  visibleSurveySteps = 0;
  // Skip directly to submit
}

// Final calculation
totalSteps = staticSteps + visibleSurveySteps + 1; // +1 for submit
// If accepted: 4 + 7 + 1 = 12 steps
// If declined: 4 + 0 + 1 = 5 steps
```

---

## Navigation Logic Changes

### Before (v1.0)
```
Step 1 → Step 2 → Step 3 → Surveys (4+) → Submit
Survey was mandatory
```

### After (v2.0)
```
Step 1 → Step 2 → Step 3 → Step 4 ✨ → Branch:
                                    ├─ Accept → Surveys (5+) → Submit
                                    └─ Decline → Submit
Survey is now optional with consent step
```

---

## Button Visibility Matrix

| Step | Back Button | Proceed Button | Custom Buttons |
|------|-------------|----------------|----------------|
| 1    | ✗ Hidden    | ✗ Hidden       | ✓ Auto-proceed |
| 2    | ✓ Visible   | ✓ Visible      | ✗ None         |
| 3    | ✓ Visible   | ✓ Visible      | ✗ None         |
| 4    | ✗ Hidden    | ✗ Hidden       | ✓ [Decline][Accept] |
| 5+   | ✓ Visible   | ✓ Visible      | ✗ None         |
| Final| ✓ Visible   | ✗ Hidden       | ✓ [Submit]     |

---

## Responsive Behavior

### Mobile View (< 640px)
```
┌─────────────────┐
│ We Value Your   │
│ Insights 📊     │
├─────────────────┤
│ Invitation Text │
├─────────────────┤
│ Purpose Section │
│ • Item 1        │
│ • Item 2        │
│ • Item 3        │
│ • Item 4        │
├─────────────────┤
│ How It Helps    │
│ [Box 1]         │
│ [Box 2]         │
│ [Box 3]         │
│ [Box 4]         │
├─────────────────┤
│ Survey Info     │
│ [Stat 1]        │
│ [Stat 2]        │
│ [Stat 3]        │
│ [Stat 4]        │
├─────────────────┤
│ Data Protection │
│ ✓ Item 1        │
│ ✓ Item 2        │
│ ✓ Item 3        │
│ ✓ Item 4        │
├─────────────────┤
│ [Decline]       │
│ [Accept]        │
└─────────────────┘
```

### Desktop View (> 1024px)
```
┌─────────────────────────────────────────┐
│ We Value Your Insights 📊               │
├─────────────────────────────────────────┤
│ Invitation Text (Full Width)            │
├─────────────────────────────────────────┤
│ PURPOSE          │ HOW IT HELPS          │
│ • Career Dev     │ [Curr Dev] [Stud Prep]
│ • Education      │ [Strategy] [Network] │
│ • Improvement    │                     │
│ • Network        │ SURVEY INFO          │
│                  │ [Time] [Q's] [Conf]  │
│                  │ [Participation]      │
├─────────────────────────────────────────┤
│ DATA PROTECTION  │ CONSENT STATEMENT    │
│ ✓ Confidential   │ By proceeding...     │
│ ✓ Statistical   │                      │
│ ✓ Secure Storage │                      │
│ ✓ Can Withdraw   │                      │
├─────────────────────────────────────────┤
│ [Decline & Submit] [Accept & Proceed]   │
└─────────────────────────────────────────┘
```

---

## Key Metrics Tracked

### Before Submission
1. Survey consent choice (accept/decline)
2. Whether surveys completed (if accepted)
3. Survey response quality

### After Submission
1. Consent rate: % users accepting surveys
2. Completion rate: % of surveys actually filled
3. Drop-off point: Where users abandon registration
4. Time spent on each step

---

## Summary of Changes from v1.0 to v2.0

| Aspect | v1.0 | v2.0 | Change |
|--------|------|------|--------|
| Total Static Steps | 3 | 4 | +1 Step |
| Survey Mandatory | Yes | Optional | ✨ NEW |
| Consent Required | No | Yes | ✨ NEW |
| Max Steps (if accept) | 10 | 12 | +2 |
| Min Steps (if decline) | 10 | 5 | -5 |
| T&C Checkbox | Yes | Yes | Same |
| Data Protection Info | No | Yes | ✨ NEW |
| Purpose Explanation | No | Yes | ✨ NEW |
| Invitation Statement | No | Yes | ✨ NEW |

---

**Updated**: November 4, 2025
**Version**: 2.0 with Survey Consent
**Status**: ✅ Production Ready
