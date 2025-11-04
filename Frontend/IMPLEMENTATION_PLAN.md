# Authentication & Registration Enhancement Plan

## Requested Features

### 1. **Forgot Password Option (Login Page)**
- Add "Forgot Password?" link below password field
- Create ForgotPassword.vue component or modal
- Flow: Email verification → Reset token → New password form

### 2. **Terms and Conditions (Register Page)**
- Add T&C checkbox in PersonalInfo.vue step
- Link to full T&C modal/page
- User must accept T&C to proceed
- Store acceptance flag: `agreed_to_terms`

### 3. **Agreement/Verification Step (After PersonalInfo)**
- Add new step 2.5 (or insert before step 3)
- Show confirmation dialog after PersonalInfo completion
- User must acknowledge data before proceeding to WorkHistory
- Options:
  - ✅ "I Agree & Proceed" → Go to next step
  - ❌ "Go Back" → Return to PersonalInfo
  - Alternative option to register directly (skip remaining steps)

---

## Current Architecture Analysis

### Login.vue (139 lines)
- **Current state**: Email + Password form only
- **Location**: `/Frontend/src/views/Login.vue`
- **Change needed**: Add "Forgot Password?" link

### Register.vue (447 lines)
- **Current state**: 7-step registration flow
- **Steps**:
  1. Verify Alumni Directory
  2. Personal Info (Step 2 - this is where T&C goes)
  3. Current Job
  4. First Job (conditional)
  5. Skills Relevance
  6. Curriculum Relevance
  7. Perception Further Studies
  8. Feedback Recommendations

- **Change needed**: Add agreement confirmation after step 2 (PersonalInfo)

### PersonalInfo.vue (479 lines)
- **Contains**: Email, Password, Address, Civil Status, Parent Info fields
- **Emits**: `update:form` event
- **Change needed**:
  - Add T&C checkbox
  - Add T&C modal/link
  - Store `agreed_to_terms` flag

---

## Implementation Steps

### Step 1: Create ForgotPassword Component
**File**: `/Frontend/src/views/ForgotPassword.vue`
- Email input + submit
- Success message with instructions
- Link back to login

### Step 2: Create TermsAndConditions Component
**File**: `/Frontend/src/components/TermsAndConditions.vue` (Modal or standalone)
- Full T&C content
- Accept/Decline buttons
- Can be modal or full page

### Step 3: Create VerificationAgreement Component
**File**: `/Frontend/src/components/register/VerificationAgreement.vue`
- Shows summary of entered personal info
- Checkbox: "I confirm all information is correct"
- Buttons: "Proceed", "Go Back", "Skip & Register"

### Step 4: Modify PersonalInfo.vue
- Add T&C checkbox before submit
- Add T&C modal/link
- Emit `agreed_to_terms` flag

### Step 5: Modify Register.vue
- Insert VerificationAgreement after PersonalInfo step
- Update step count logic
- Handle skip registration flow

### Step 6: Add Routes
- `/forgot-password` → ForgotPassword.vue
- Existing routes stay the same

---

## Data Changes Needed

### Register.vue form object
```javascript
form.agreed_to_terms = false // Add this flag
```

### PersonalInfo.vue
```javascript
agreed_to_terms: false // Add to localForm
terms_checkbox_visible: false // Show/hide T&C modal
```

---

## UI/UX Details

### Login Page
```
[Email field]
[Password field with toggle]
[Forgot Password?] ← New link (bottom right)
[Login button]
[Don't have account? Register]
```

### PersonalInfo Step
```
[Existing fields...]
[☐ I agree to Terms and Conditions] [View T&C]
[Next / Skip]
```

### VerificationAgreement Step (New Step 2.5)
```
PLEASE VERIFY YOUR INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name: [Display name]
Email: [Display email]
Address: [Display address]
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
☐ I confirm all information is correct
[← Back] [Proceed] [Skip & Register]
```

---

## Timeline & Complexity

| Feature | Complexity | Estimated Time |
|---------|-----------|-----------------|
| Forgot Password | Medium | 30 min |
| T&C Modal | Low | 20 min |
| VerificationAgreement | Medium | 40 min |
| Integration | Low | 15 min |
| **TOTAL** | | **~105 min** |

---

## File Changes Summary

| File | Action | Type |
|------|--------|------|
| `Login.vue` | Add "Forgot Password?" link | Modify |
| `ForgotPassword.vue` | Create new view | Create |
| `Register.vue` | Add VerificationAgreement step | Modify |
| `PersonalInfo.vue` | Add T&C checkbox + modal | Modify |
| `VerificationAgreement.vue` | Create new component | Create |
| `TermsAndConditions.vue` | Create modal component | Create |
| `router/index.js` | Add /forgot-password route | Modify |

---

**Status**: Ready for implementation ✅
**Last Updated**: 04/11/2025
