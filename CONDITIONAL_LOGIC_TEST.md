# Conditional Logic Test Guide

## What Was Fixed

### 1. **QuestionModal - Saving**
- ✅ Added proper initialization of `depends_on_question` and `depends_on_value` fields
- ✅ Added watcher to reload form when editing different questions
- ✅ Clean up `depends_on_value` when `depends_on_question` is null/empty

### 2. **SectionView - Display**
- ✅ Fixed "Required" field: Changed from `question.required` to `question.is_required`
- ✅ Added conditional value display (Yes/No) below the icon
- ✅ Added tooltip showing full conditional logic info

## Test Steps

### Test 1: Create Question with Conditional Logic
1. Open Survey Management
2. Click on a form/template
3. Create a Section (if none exists)
4. Click on the section card to open Section View
5. Click "Add Question" button
6. Create a **Yes/No question** first:
   - Question Text: "Are you currently employed?"
   - Type: Yes/No
   - Required: ✅ Check it
   - Click Save

7. Click "Add Question" again to create a second question
8. Fill in:
   - Question Text: "What is your job title?"
   - Type: Short Text
   - Required: ✅ Check it
   - Scroll down to **Conditional Logic** section
   - "Show this question only if": Select "Are you currently employed?"
   - "Answer is": Select "Yes"
   - Click Save

### Test 2: Verify Table Display
After saving, check the Section View table:

**Expected Results:**
- ✅ **Required column**: Both questions should show "Required" (red badge)
- ✅ **Conditional column**: 
  - First question (Are you employed?): Shows "—" (no condition)
  - Second question (Job title): Shows conditional icon + "Yes" badge
- ✅ **Hover** over the conditional icon: Tooltip shows "Shows only if [Question Text] = Yes"

### Test 3: Update/Edit Question with Conditional Logic
1. Click the **Edit button** (pencil icon) on the second question (Job title)
2. Modal should open with:
   - ✅ All fields pre-filled
   - ✅ Conditional Logic section shows: "Are you currently employed?"
   - ✅ Answer is: "Yes"
3. Try changing the condition to "No"
4. Click Save
5. Verify table updates to show "No" badge

### Test 4: Remove Conditional Logic
1. Edit the second question again
2. In Conditional Logic section:
   - Change "Show this question only if" to "No condition (always show)"
3. Click Save
4. Verify table shows "—" in Conditional column

## Common Issues & Solutions

### Issue: "Required" always shows "Optional"
**Solution:** ✅ FIXED - Changed `question.required` to `question.is_required`

### Issue: Conditional value (Yes/No) not showing in table
**Solution:** ✅ FIXED - Added `question.depends_on_value` display

### Issue: Edit modal doesn't show existing conditional logic
**Solution:** ✅ FIXED - Added watcher for `props.question` changes

### Issue: Conditional logic not saving
**Solution:** ✅ FIXED - Ensure `depends_on_question` and `depends_on_value` are in payload

## Backend Verification

If issues persist, check the browser console for:
1. The payload being sent (look for `📤 Sending question data:`)
2. Any error responses
3. Check that these fields are present:
   - `is_required: true/false`
   - `depends_on_question: <question_id>` (or null)
   - `depends_on_value: "Yes"/"No"` (or empty string)

## API Response Check

Open browser DevTools → Network tab:
1. Create/update a question
2. Find the POST/PATCH request to `/api/survey/questions/`
3. Check **Request Payload** has:
   ```json
   {
     "question_text": "...",
     "is_required": true,
     "depends_on_question": 123,  // or null
     "depends_on_value": "Yes"     // or ""
   }
   ```
4. Check **Response** returns the same fields

## Success Criteria

All tests pass when:
- ✅ Required badge shows correctly (Required/Optional)
- ✅ Conditional icon appears when question has condition
- ✅ Conditional value (Yes/No) displays below icon
- ✅ Tooltip shows readable condition
- ✅ Edit modal pre-fills all conditional logic fields
- ✅ Saving preserves conditional logic
- ✅ Can update/remove conditional logic
