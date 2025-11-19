# Conditional Logic Testing Guide

## Overview
This guide provides step-by-step instructions for manually testing the conditional logic implementation in Survey.vue.

---

## Prerequisites

1. ✅ Backend server running (`daphne` or `python manage.py runserver`)
2. ✅ Frontend server running (`npm run dev`)
3. ✅ Admin account with permissions to create surveys
4. ✅ Alumni account for testing surveys
5. ✅ Browser with DevTools open (for console monitoring)

---

## Test 1: Backend Unit Tests

### Run Django Tests

```powershell
cd Backend
python manage.py test survey_app.tests
```

### Expected Results
- ✅ All tests pass (14 tests total)
- ✅ Tests for serializer conditional fields
- ✅ Tests for API endpoint responses
- ✅ Tests for backward compatibility
- ✅ No errors or warnings

### What's Being Tested
- Serializer includes `depends_on_question_id` and `depends_on_value`
- API returns conditional fields correctly
- Non-conditional surveys work normally
- JSON array dependency values work
- Inactive questions filtered out
- Circular dependencies handled gracefully
- Backward compatibility maintained

---

## Test 2: Create Test Survey with Conditionals

### Step 2.1: Login as Admin

1. Navigate to: `http://localhost:8000/admin/`
2. Login with admin credentials
3. Go to **Survey Categories**

### Step 2.2: Create Personal Information Category

**Click "Add Survey Category"**

- **Name:** Personal Information
- **Description:** Basic personal information
- **Order:** 1
- **Is active:** ✅ Checked
- **Include in registration:** ☐ Unchecked (for now)
- **Page break:** ✅ Checked
- **Depends on category:** (leave empty)
- **Depends on question text:** (leave empty)
- **Depends on value:** (leave empty)
- **Created by:** (select your admin user)

**Click "Save and continue editing"**

### Step 2.3: Add Questions to Personal Information

**Click "Add another Survey question" (inline)**

#### Question 1: Employment Status
- **Question text:** Are you currently employed?
- **Question type:** Yes/No Question
- **Is required:** ✅ Checked
- **Order:** 1
- **Is active:** ✅ Checked
- **Depends on question:** (leave empty)
- **Depends on value:** (leave empty)

#### Question 2: Employment Type
- **Question text:** What is your employment type?
- **Question type:** Single Choice (Radio)
- **Options:** `["Full-time", "Part-time", "Contract", "Unemployed"]`
- **Is required:** ✅ Checked
- **Order:** 2
- **Is active:** ✅ Checked
- **Depends on question:** (leave empty)
- **Depends on value:** (leave empty)

**Click "Save"**

### Step 2.4: Create Employment Details Category (Conditional)

**Click "Add Survey Category"**

- **Name:** Employment Details
- **Description:** Information about your current job
- **Order:** 2
- **Is active:** ✅ Checked
- **Page break:** ✅ Checked
- **Depends on category:** Personal Information
- **Depends on question text:** Are you currently employed?
- **Depends on value:** `["Yes"]`
- **Created by:** (select your admin user)

**Click "Save and continue editing"**

### Step 2.5: Add Questions to Employment Details

#### Question 1: Job Title
- **Question text:** What is your job title?
- **Question type:** Text Input
- **Is required:** ✅ Checked
- **Order:** 1
- **Is active:** ✅ Checked

#### Question 2: Manager Question
- **Question text:** Do you have a direct manager?
- **Question type:** Yes/No Question
- **Is required:** ☐ Unchecked
- **Order:** 2
- **Is active:** ✅ Checked

#### Question 3: Manager Name (Conditional)
- **Question text:** What is your manager's name?
- **Question type:** Text Input
- **Is required:** ☐ Unchecked
- **Order:** 3
- **Is active:** ✅ Checked
- **Depends on question:** Do you have a direct manager?
- **Depends on value:** `Yes`

**Click "Save"**

### Step 2.6: Create Work Schedule Category (Multi-Value Conditional)

**Click "Add Survey Category"**

- **Name:** Work Schedule
- **Description:** Details about your work hours
- **Order:** 3
- **Is active:** ✅ Checked
- **Page break:** ✅ Checked
- **Depends on category:** Personal Information
- **Depends on question text:** What is your employment type?
- **Depends on value:** `["Full-time", "Part-time", "Contract"]`
- **Created by:** (select your admin user)

**Click "Save and continue editing"**

### Step 2.7: Add Questions to Work Schedule

#### Question 1: Hours per Week
- **Question text:** How many hours do you work per week?
- **Question type:** Number Input
- **Is required:** ✅ Checked
- **Order:** 1
- **Is active:** ✅ Checked

**Click "Save"**

---

## Test 3: Frontend Manual Testing

### Step 3.1: Login as Alumni

1. Navigate to: `http://localhost:5173/`
2. Login with alumni credentials
3. Navigate to **Survey** page
4. Open browser DevTools (F12) and go to Console tab

### Step 3.2: Test Category-Level Conditionals

#### Test 3.2a: Employment Details Category

**Initial State:**
- ✅ Should see only "Personal Information" category
- ❌ Should NOT see "Employment Details" category
- ❌ Should NOT see "Work Schedule" category

**Action:** Answer "Are you currently employed?" → **No**
- ❌ "Employment Details" should remain hidden
- ❌ "Work Schedule" should remain hidden
- ✅ Progress should only count Personal Information questions

**Action:** Change answer to "Are you currently employed?" → **Yes**
- ✅ "Employment Details" category should appear
- ❌ "Work Schedule" should still be hidden (employment type not answered yet)
- ✅ Progress should update to include Employment Details questions
- ✅ Check console: No errors

**Action:** Click "Next" button
- ✅ Should navigate to "Employment Details" category
- ✅ Should skip any hidden categories

**Action:** Go back and change to "Are you currently employed?" → **No**
- ❌ "Employment Details" should disappear
- ✅ If you had filled in job title, it should be cleared (check console for cleanup message)
- ✅ Progress should update (exclude hidden questions)

#### Test 3.2b: Work Schedule Category (Multi-Value)

**Action:** Answer "What is your employment type?" → **Full-time**
- ✅ "Work Schedule" category should appear
- ✅ Progress includes Work Schedule questions

**Action:** Change to "What is your employment type?" → **Part-time**
- ✅ "Work Schedule" should still be visible (Part-time is in valid values)

**Action:** Change to "What is your employment type?" → **Contract**
- ✅ "Work Schedule" should still be visible (Contract is in valid values)

**Action:** Change to "What is your employment type?" → **Unemployed**
- ❌ "Work Schedule" should disappear (Unemployed not in valid values)
- ✅ Responses to Work Schedule questions should be cleared

### Step 3.3: Test Question-Level Conditionals

**Setup:** Ensure you're in "Employment Details" category

**Initial State:**
- ✅ See "What is your job title?"
- ✅ See "Do you have a direct manager?"
- ❌ Should NOT see "What is your manager's name?"

**Action:** Answer "Do you have a direct manager?" → **No**
- ❌ "What is your manager's name?" should remain hidden

**Action:** Change to "Do you have a direct manager?" → **Yes**
- ✅ "What is your manager's name?" should appear
- ✅ Check console: No errors

**Action:** Fill in manager's name → "John Doe"

**Action:** Change "Do you have a direct manager?" → **No**
- ❌ "What is your manager's name?" should disappear
- ✅ Check console: Should see "Cleaning up response for hidden question: 22" (or similar)
- ✅ Manager name answer should be cleared

### Step 3.4: Test Progress Calculations

**Setup:** Answer some questions to create a mix of answered/unanswered

**Test:**
1. Note the progress percentage
2. Hide a category by changing a dependency answer
3. ✅ Progress should recalculate (increase because denominator decreased)
4. Show the category again
5. ✅ Progress should recalculate (decrease because denominator increased)

**Expected Behavior:**
- Progress only counts visible questions
- Answered hidden questions don't count toward progress
- Progress bar updates in real-time

### Step 3.5: Test Validation

**Test Required Fields with Conditionals:**

**Scenario 1: Required Question in Hidden Category**
1. Make "Employment Details" visible (answer Yes to employment)
2. Navigate to "Employment Details"
3. Leave "Job title" (required) empty
4. Try to click "Next"
5. ✅ Should show validation error

**Scenario 2: Required Question Becomes Hidden**
1. Fill in "Job title"
2. Go back to "Personal Information"
3. Change employment to "No" (hides Employment Details)
4. Try to submit or navigate forward
5. ✅ Should allow it (hidden required questions don't block progress)

### Step 3.6: Test Navigation

**Test Category Navigation:**

**Setup:** Make Employment Details visible, Work Schedule hidden

**Test:**
1. Click "Next" from Personal Information
2. ✅ Should go to Employment Details (skip hidden categories)
3. Click "Next" from Employment Details
4. ✅ Should not show Work Schedule (it's hidden)
5. Make Work Schedule visible (change employment type to Full-time)
6. Click "Next" from Employment Details
7. ✅ Should now show Work Schedule

**Test Direct Category Access:**
1. Try to manually navigate to a hidden category
2. ✅ Should prevent navigation to hidden categories

### Step 3.7: Test Response Cleanup

**Monitor Console:**

**Test:**
1. Open browser console
2. Answer a question that makes another question visible
3. Fill in the newly visible question
4. Change the dependency answer to hide it again
5. ✅ Check console for: `"Cleaning up response for hidden question: [id]"`
6. ✅ Verify the response is actually removed (check responses object)

### Step 3.8: Test Form Submission

**Complete the Survey:**

**Action:** Fill in all visible required questions
1. Personal Information: Answer all questions
2. Make Employment Details visible
3. Fill required fields in Employment Details
4. Make Work Schedule visible
5. Fill required fields in Work Schedule
6. Submit the survey

**Verify:**
1. ✅ Submission succeeds
2. ✅ Only responses to visible questions are submitted
3. ✅ No responses for hidden questions in submission
4. Check backend/database to confirm data saved correctly

---

## Test 4: Edge Cases

### Test 4.1: All Categories Hidden
**Action:** Answer questions so all conditional categories are hidden
- ✅ Should show only Personal Information
- ✅ Should display appropriate message if stuck
- ✅ Should allow submission with only Personal Information

### Test 4.2: Rapid Answer Changes
**Action:** Quickly toggle answers that show/hide categories
- ✅ UI should update smoothly
- ✅ No race conditions or flickering
- ✅ Progress updates correctly
- ✅ Console shows no errors

### Test 4.3: Invalid Dependency Data
**Test:** Survey with malformed JSON in depends_on_value
- ✅ Should fallback to string comparison
- ✅ Should not crash
- ✅ Check console for warnings (not errors)

### Test 4.4: Missing Dependency Question
**Test:** Category depends on non-existent question
- ✅ Category should be hidden (safe default)
- ✅ No JavaScript errors
- ✅ Warning in console (optional)

### Test 4.5: Circular Dependencies
**Setup:** Create questions that depend on each other (if possible in admin)
- ✅ Should not crash
- ✅ Both questions should hide (break the cycle)
- ✅ Or show appropriate behavior

### Test 4.6: Empty/Null Values
**Test:** Dependency values with empty strings or null
- ✅ Should treat as "no dependency"
- ✅ Questions/categories show normally

---

## Test 5: Backward Compatibility

### Test 5.1: Survey Without Conditionals

**Action:** Create a simple survey with no conditional logic
1. Create category with all dependency fields empty
2. Create questions with no depends_on fields
3. Test in Survey.vue

**Expected:**
- ✅ Works exactly as before
- ✅ All categories visible
- ✅ All questions visible
- ✅ No console errors

### Test 5.2: Existing Survey Data

**Action:** Test with surveys created before this implementation
- ✅ Should load normally
- ✅ All questions visible
- ✅ Progress calculates correctly
- ✅ Submission works

---

## Test 6: Cross-Browser Testing

### Test in Multiple Browsers:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (if available)

**Check:**
- Conditional logic works consistently
- Progress updates correctly
- Navigation works
- No browser-specific errors

---

## Test 7: Performance Testing

### Test with Large Survey

**Create:** Survey with 10+ categories, 50+ questions, many conditionals

**Monitor:**
- ✅ Page load time
- ✅ Response time when toggling answers
- ✅ Memory usage (DevTools → Performance tab)
- ✅ No lag or freezing

**Expected:**
- Computed properties are cached (fast re-renders)
- Watchers don't cause performance issues
- Smooth user experience

---

## Expected Console Output

### Normal Operation:
```
✅ No errors
✅ Optional info messages about cleanup:
   "Cleaning up response for hidden question: 22"
```

### Warning Cases:
```
⚠️ "Dependency category not found for: [category name]"
⚠️ "Dependency question not found: [question text]"
```

### Error Cases (Should NOT see):
```
❌ Any JavaScript errors
❌ Any API errors
❌ Any rendering errors
```

---

## Checklist Summary

### Backend Tests
- [ ] All Django unit tests pass
- [ ] Serializer includes conditional fields
- [ ] API returns correct data structure
- [ ] Backward compatibility maintained

### Category-Level Conditionals
- [ ] Category hides when dependency not met
- [ ] Category shows when dependency met
- [ ] Boolean values normalize to Yes/No
- [ ] JSON arrays work for multiple valid values
- [ ] Progress excludes hidden categories

### Question-Level Conditionals
- [ ] Question hides when dependency not met
- [ ] Question shows when dependency met
- [ ] Response cleanup works
- [ ] Console logs cleanup messages

### Navigation
- [ ] Next/Previous skip hidden categories
- [ ] Can't manually navigate to hidden categories
- [ ] Progress indicator shows correct position

### Validation
- [ ] Required questions in hidden categories don't block
- [ ] Required questions in visible categories do block
- [ ] Can submit with hidden required questions unanswered

### Progress & Completion
- [ ] Progress only counts visible questions
- [ ] Progress updates when visibility changes
- [ ] Submission only sends visible question responses

### Edge Cases
- [ ] Missing dependencies handled gracefully
- [ ] Invalid JSON handled gracefully
- [ ] Circular dependencies don't crash
- [ ] Empty values treated as no dependency
- [ ] All categories hidden scenario works

### Backward Compatibility
- [ ] Surveys without conditionals work normally
- [ ] Existing survey data unaffected
- [ ] Mixed conditional/non-conditional works

### Cross-Browser
- [ ] Chrome/Edge works
- [ ] Firefox works
- [ ] Safari works (if available)

### Performance
- [ ] Large surveys perform well
- [ ] No lag when toggling answers
- [ ] Memory usage acceptable

---

## Troubleshooting

### Issue: Category not hiding/showing
**Check:**
1. Dependency fields set correctly in admin?
2. Question text matches exactly?
3. depends_on_value format correct (JSON array or string)?
4. Check browser console for warnings

### Issue: Question not hiding/showing
**Check:**
1. depends_on_question_id is correct?
2. depends_on_value matches expected value?
3. Boolean vs string normalization (Yes/No)?
4. Check console for errors

### Issue: Progress incorrect
**Check:**
1. Are hidden questions being counted?
2. Check visibleCategories computed property
3. Check console for calculation errors

### Issue: Responses not cleaning up
**Check:**
1. Watcher is set up correctly?
2. Check console for cleanup messages
3. Verify responses object in Vue DevTools

---

## Success Criteria

✅ **All tests pass**
✅ **No JavaScript errors in console**
✅ **Conditional logic works as expected**
✅ **Backward compatibility maintained**
✅ **Performance is acceptable**
✅ **User experience is smooth**

---

## Next Steps After Testing

1. ✅ Document any issues found
2. ✅ Fix any bugs discovered
3. ✅ Update documentation if needed
4. ✅ Deploy to production when validated
5. ✅ Monitor for any edge cases in production use

---

**Testing Date:** _______________
**Tested By:** _______________
**Status:** ⬜ Pass | ⬜ Fail | ⬜ Needs Review
**Notes:**
