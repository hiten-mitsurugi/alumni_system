# Authentication Features - Workflow Diagrams

## 1. Complete Registration Flow with New Features

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ALUMNI REGISTRATION SYSTEM                      │
└─────────────────────────────────────────────────────────────────────┘

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
    │            STEP 1: Verify Alumni
    │                    │
    │            ┌───────┴──────────┐
    │            │                  │
    │      [NOT FOUND]         [FOUND] ✓
    │            │                  │
    │         (Error)         STEP 2: Personal Info
    │                              │
    │                    ┌─────────┴──────────┐
    │                    │                    │
    │            [T&C CHECKBOX] ← [T&C LINK]
    │            [TERMS MODAL]      ↓
    │                (Modal Opens)   │
    │                    │           │
    │            ┌───────┴───────────┘
    │            │
    │         STEP 3: Verification Agreement ✨ NEW
    │            │
    │    ┌───────┴────────────────┐
    │    │                        │
    │ [PROCEED] ─→ SURVEYS    [GO BACK] → Edit PersonalInfo
    │    │                        │
    │    │                   [SKIP] → STEP 4
    │    │
    │ STEP 4+: Dynamic Surveys
    │    │
    │ STEP N: Final Submission
    │    │
    │ [SUBMIT REGISTRATION]
    │    │
    │ Success/Pending Approval
    │    │
    └────→ Return to Login

```

## 2. Forgot Password Flow (Detail)

```
┌────────────────────────────────────────────┐
│     FORGOT PASSWORD - 3 STEP RECOVERY      │
└────────────────────────────────────────────┘

STEP 1: EMAIL VERIFICATION
┌──────────────────────────────┐
│ "Enter your registered email"│
│ ┌──────────────────────────┐ │
│ │ your@email.com          │ │
│ └──────────────────────────┘ │
│                              │
│ [Send Recovery Code]         │
│                              │
│ ⚠️ Email not found (Error)   │
│ ✅ Email found (Continue)     │
└──────────────────────────────┘
           │ Success
           ▼
STEP 2: CODE VERIFICATION
┌──────────────────────────────┐
│ "Enter verification code"    │
│ ┌──────────────────────────┐ │
│ │ 0 0 0 0 0 0 (6 digits) │ │
│ └──────────────────────────┘ │
│                              │
│ Check mark when filled       │
│                              │
│ ⚠️ Invalid code (Retry)       │
│ ✅ Code verified (Continue)   │
└──────────────────────────────┘
           │ Success
           ▼
STEP 3: NEW PASSWORD
┌──────────────────────────────┐
│ "Set your new password"      │
│                              │
│ Password Requirements:       │
│ • 8+ characters              │
│ • 1 Uppercase (A-Z)          │
│ • 1 Lowercase (a-z)          │
│ • 1 Number (0-9)             │
│ • 1 Special (!@#$%)          │
│                              │
│ New Password:                │
│ ┌──────────────────────────┐ │
│ │ ••••••••••••••••••••     │ │
│ └──────────────────────────┘ │
│                              │
│ Confirm Password:            │
│ ┌──────────────────────────┐ │
│ │ ••••••••••••••••••••     │ │
│ └──────────────────────────┘ │
│                              │
│ [Reset Password]             │
│                              │
│ ✅ Password updated          │
│ [Back to Login]              │
└──────────────────────────────┘
```

## 3. Terms & Conditions Flow

```
┌────────────────────────────────┐
│  TERMS & CONDITIONS MODAL      │
└────────────────────────────────┘

PersonalInfo Step
    │
[Click T&C Link] ────────┐
    │                    │
    │              Modal Overlay
    │              (Dark Background)
    │                    │
    │      ┌─────────────┴──────────────┐
    │      │                            │
    │      │ TERMS AND CONDITIONS       │
    │      │                            │
    │      │ 1. Acceptance of Terms     │
    │      │ 2. User Responsibilities  │
    │      │ 3. Account Security       │
    │      │ 4. Intellectual Property  │
    │      │ 5. Limitation of Liability│
    │      │ 6. Indemnification        │
    │      │ 7. Termination of Account │
    │      │ 8. Modifications to Terms │
    │      │ 9. Governing Law          │
    │      │ 10. Contact Information   │
    │      │ 11. Entire Agreement      │
    │      │ 12. Severability          │
    │      │                            │
    │      │ [Accept]  [Close]         │
    │      │                            │
    │      └────────────┬───────────────┘
    │                   │
    │      ┌────────────┴────────────┐
    │      │                         │
    │   [ACCEPT]                [CLOSE]
    │      │                         │
    │      └─ Return to PersonalInfo ─┘
    │                 ▲
    │                 │
    │      T&C Checkbox ✓ (Checked)
    │
   Continue to Next Step ✓
```

## 4. Verification Agreement Step (New!)

```
┌─────────────────────────────────────────────┐
│   VERIFICATION AGREEMENT - STEP 3           │
└─────────────────────────────────────────────┘

After PersonalInfo Submission
        │
        ▼
┌─────────────────────────────────────────────┐
│  PLEASE REVIEW YOUR INFORMATION             │
│                                             │
│  Email: your@email.com                      │
│  Phone: +63 9XX XXX XXXX                    │
│  Name: Juan Dela Cruz                       │
│  Gender: Male | Civil Status: Single        │
│  Present Address: Manila, Philippines       │
│  Permanent Address: Same as Present         │
│  Employment: Employed Locally               │
│                                             │
│  [View Full Details ▼]                      │
│                                             │
│  ☐ I confirm all information is correct    │
│                                             │
│  [Go Back] [Proceed to Surveys] [Skip]     │
└─────────────────────────────────────────────┘
        │    │    │
        │    │    └─→ Skip & Register
        │    │        (Jump to Submit)
        │    │
        │    └──→ Proceed to Surveys
        │        (Continue normally)
        │
        └──→ Go Back to PersonalInfo
             (Edit entered data)
```

## 5. T&C Validation Chain

```
PersonalInfo Component
        │
        ▼
┌──────────────────────────────┐
│  Local Form State:           │
│  - email: "xxx@xxx.com"      │
│  - password: "***"           │
│  - address: "..."            │
│  - agreedToTerms: false ✗    │
└──────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  User Interaction:                   │
│  1. Click T&C Link                   │
│     → Modal Opens                    │
│  2. Read Terms                       │
│  3. Click "Accept"                   │
│     → agreedToTerms = true ✓         │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Watcher Syncs:                      │
│  agreedToTerms → localForm           │
│  (true)           (agreed_to_terms)  │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  emitValidation() Check:             │
│  IF agreedToTerms === true ✓         │
│     → Validation passes              │
│     → Can proceed to next step       │
│  ELSE                                │
│     → Show error message             │
│     → Proceed button disabled        │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Emit to Parent:                     │
│  emit('update:form', {               │
│    ...localForm,                     │
│    agreed_to_terms: true ✓           │
│  })                                  │
└──────────────────────────────────────┘
        │
        ▼
RegisterDynamic Component Receives
Updated Form with T&C Flag
```

## 6. Step Navigation Logic (RegisterDynamic)

```
Initial State: currentStep = 1

┌─────────────────────────┬──────────────────────┐
│ Step Number             │ Step Title           │
├─────────────────────────┼──────────────────────┤
│ 1                       │ Verify Alumni ✓      │
│ 2                       │ Personal Info ✓      │
│ 3                       │ Confirm Info ✨ NEW  │
│ 4 to N                  │ Dynamic Surveys      │
│ N+1 (Submit)            │ Review & Submit      │
└─────────────────────────┴──────────────────────┘

Navigation Buttons:

┌──────────────────────────────────────────────────┐
│ [Back Button]                [Action Button]     │
├──────────────────────────────────────────────────┤
│ Visible: currentStep > 1     Visible: Varies     │
├──────────────────────────────────────────────────┤
│ Step 1: Hidden               "Auto-Proceeds"     │
│ Step 2: [Back]               [Proceed]           │
│ Step 3: [Back]               [Proceed/Skip]      │
│ Step 4+: [Back]              [Proceed]           │
│ Step N: [Back]               [Submit]            │
└──────────────────────────────────────────────────┘

Dynamic Survey Counting:
- Static steps: 3 (Verify, PersonalInfo, Agreement)
- Survey steps: Based on visible categories
- Total: 3 + surveyCategories.length
- Offset in code: currentStep - 4 (for step 4+)
```

## 7. Data Flow Summary

```
User Input (Step 2)
    │
    ├─→ email, password, address, employment_status
    ├─→ gender, civil_status, family_info
    └─→ agreed_to_terms ✨ NEW
        │
        ▼
LocalForm Object
    │
    ├─ Validation ✓
    │  └─ Checks agreed_to_terms
    │
    ├─ Watcher syncs data
    │  └─ emit('update:form', {...})
    │
    ▼
RegisterDynamic Form Object
    │
    ├─ Store entire form data
    ├─ Sync across all steps
    ├─ Validate on each step
    │
    ▼
Final Submission (FormData)
    │
    ├─ first_name, email, password
    ├─ present_address_data (JSON)
    ├─ permanent_address_data (JSON)
    ├─ agreed_to_terms: true ✓
    ├─ survey_responses: [...]
    │
    ▼
POST /auth/register/
    │
    ▼
Backend Processing
    │
    ├─ Create User Account
    ├─ Store All Data
    ├─ Log T&C Acceptance ✨
    ├─ Process Survey Responses
    │
    ▼
Success Response
    │
    ▼
Pending Approval Page
```

---

## Color Code Reference

| Symbol | Meaning |
|--------|---------|
| ✓ | Completed/Working |
| ✨ | New Feature |
| ⚠️ | Error/Warning |
| → | Flow/Navigation |
| ▼ | Next Step |
| ☐ | Checkbox |
| [ ] | Button |

---

## Key Points

1. **Three-Step Forgot Password**: Email → Code → New Password
2. **T&C Modal**: Accessible from PersonalInfo, required to proceed
3. **Verification Agreement**: NEW step to confirm entered data
4. **Skip Option**: Users can skip surveys and register immediately
5. **Data Persistence**: All data flows through the same form object
6. **Dynamic Steps**: Survey steps count dynamically based on categories
7. **Validation**: T&C must be accepted before proceeding from Step 2
