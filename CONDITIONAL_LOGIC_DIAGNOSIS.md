# Conditional Logic Diagnosis & Solution

## Test Results

### ✅ Backend Test: **ALL PASSED**
Ran `Backend/test_conditional_logic.py` - Verified:
- ✅ Questions can be created with conditional logic
- ✅ `is_required` field saves correctly
- ✅ `depends_on_question` field saves correctly  
- ✅ `depends_on_value` field saves correctly
- ✅ Serializer returns all fields correctly
- ✅ API will return proper data

**Conclusion: Backend is working 100% correctly!**

## Issue Identified

The problem is in the **FRONTEND** - specifically with how the dropdown is populated or how the data flows.

## Fixes Applied

### 1. QuestionModal.vue
```javascript
// Added debug logging for available questions
const availableQuestions = computed(() => {
  const available = props.questions.filter(...)
  
  console.log('🔍 Available questions for conditional logic:', available)
  return available
})

// Added debug logging when initializing form
const initializeForm = () => {
  if (props.question) {
    console.log('🔄 Initializing form with question:', {
      depends_on_question: questionData.depends_on_question,
      depends_on_value: questionData.depends_on_value
    })
  }
}

// Fixed save payload
const saveQuestion = async () => {
  const payload = {
    ...form.value,
    depends_on_value: form.value.depends_on_question ? form.value.depends_on_value : ''
  }
  console.log('📤 Sending question data:', payload)
  ...
}
```

### 2. SectionView.vue  
```javascript
// Added debug logging for question data
const sortedQuestions = computed(() => {
  const sorted = [...]
  console.log('📊 Section questions:', sorted.map(q => ({
    is_required: q.is_required,
    depends_on_question: q.depends_on_question,
    depends_on_value: q.depends_on_value
  })))
  return sorted
})
```

### 3. Fixed Field Names
- Changed `question.required` → `question.is_required`
- Added check for `question.depends_on_value` before displaying

## How to Test & Debug

### Step 1: Open Browser Console
Press `F12` to open Developer Tools → Console tab

### Step 2: Create Yes/No Question
1. Go to Survey Management
2. Open a form/template
3. Click on a section
4. Click "Add Question"
5. Create:
   - Question: "Are you currently employed?"
   - Type: **Yes/No**
   - Required: ✅
   - Click Save

**Check Console:** Should see `📤 Sending question data:` with `is_required: true`

### Step 3: Create Conditional Question
1. Click "Add Question" again
2. Fill:
   - Question: "What is your job title?"
   - Type: Short Text
   - Required: ✅
3. **Scroll down to Conditional Logic section**
4. **Check Console:** Look for `🔍 Available questions for conditional logic:`
   - Should show array with the Yes/No question
   - If empty → **Problem: Questions not being passed to modal**

5. In dropdown "Show this question only if":
   - **Should see:** "Are you currently employed?"
   - **If empty:** Questions not filtering correctly

6. Select the question
7. Select "Yes" for answer
8. Click Save

**Check Console:** Should see:
```
📤 Sending question data: {
  depends_on_question: 12,
  depends_on_value: "Yes",
  is_required: true,
  ...
}
```

### Step 4: Verify in Table
After saving, check the Section View table:

**Check Console:** Should see:
```
📊 Section questions: [
  { is_required: true, depends_on_question: 12, depends_on_value: "Yes" }
]
```

**In UI:**
- Required column: Should show "Required" (red badge)
- Conditional column: Should show icon + "Yes" badge

### Step 5: Edit Question
1. Click Edit on the conditional question
2. **Check Console:** Should see:
```
🔄 Initializing form with question: {
  depends_on_question: 12,
  depends_on_value: "Yes"
}
```
3. Modal should show:
   - Conditional dropdown: "Are you currently employed?" selected
   - Answer dropdown: "Yes" selected

## Possible Issues & Solutions

### Issue 1: "Show this question only if" dropdown is empty

**Symptoms:**
- Console shows `🔍 Available questions: []`
- No questions in dropdown

**Causes:**
1. No Yes/No questions exist yet → **Create one first**
2. `props.questions` is empty → **Check FormEditor is passing `allQuestionsInForm`**
3. Questions not loaded yet → **Refresh the form data**

**Solutions:**
- Create a Yes/No question first
- Check network tab for API response with questions array
- Verify FormEditor passes `:questions="allQuestionsInForm"`

### Issue 2: Conditional value not saving

**Symptoms:**
- Console shows `depends_on_value: ""`  or `null`
- Table shows only icon, no "Yes/No" badge

**Causes:**
1. `depends_on_value` not selected in dropdown
2. Payload not including the field

**Solutions:**
- Select both dropdowns (question AND value)
- Check `📤 Sending question data:` includes `depends_on_value`

### Issue 3: Edit doesn't show existing conditional logic

**Symptoms:**
- Dropdowns empty when editing
- Console shows `depends_on_question: null`

**Causes:**
- Watcher not firing
- Form not reinitializing

**Solutions:**
- Check console for `🔄 Initializing form with question:`
- Verify props.question has the fields
- Close and reopen modal

## Network Debugging

1. Open DevTools → **Network** tab
2. Create/update a question
3. Find the POST/PATCH request
4. Check **Payload** tab:
```json
{
  "question_text": "What is your job title?",
  "question_type": "text",
  "is_required": true,
  "depends_on_question": 12,
  "depends_on_value": "Yes",
  "category": 11,
  ...
}
```

5. Check **Response** tab - should return same fields

## Success Criteria

All working when:
- ✅ Console shows available questions for conditional logic
- ✅ Dropdown populates with Yes/No questions
- ✅ Can select question and value
- ✅ Console shows correct payload being sent
- ✅ Table displays "Required" correctly
- ✅ Table shows conditional icon + value
- ✅ Edit modal pre-fills conditional settings
- ✅ Network request includes all fields
- ✅ Can update/remove conditional logic

## Next Steps

1. **Test in browser** following steps above
2. **Share console output** if issues persist
3. Check if questions array is being passed correctly
4. Verify the v-model bindings in the conditional logic section
