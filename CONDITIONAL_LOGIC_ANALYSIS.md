# Comprehensive Conditional Logic Analysis
**Date:** November 19, 2025  
**Purpose:** Analyze and plan implementation of conditional questions in Survey.vue

---

## 1. BACKEND ANALYSIS

### 1.1 Registration Survey Endpoint (RegistrationSurveyQuestionsView)
**File:** `Backend/survey_app/views/alumni_views.py`  
**Route:** `/api/survey/registration-questions/`  
**Permission:** `AllowAny` (public registration)

#### Data Structure Sent:
```python
{
    'category': {
        'id': int,
        'name': str,
        'description': str,
        'order': int,
        # CONDITIONAL CATEGORY FIELDS (included when present):
        'depends_on_category': int,  # ID of dependency category
        'depends_on_category_name': str,
        'depends_on_question_text': str,  # Question text to check
        'depends_on_value': str  # JSON array or string of required values
    },
    'questions': [
        {
            'id': int,
            'question_text': str,
            'question_type': str,
            'placeholder_text': str,
            'help_text': str,
            'options': list,
            'is_required': bool,
            'min_value': int,
            'max_value': int,
            'max_length': int,
            'order': int,
            # CONDITIONAL QUESTION FIELDS (included when present):
            'depends_on_question_id': int,  # ID of dependency question
            'depends_on_value': str  # Required value to show this question
        }
    ]
}
```

**Key Implementation:**
```python
# Question-level conditional logic
if question.depends_on_question:
    question_data['depends_on_question_id'] = question.depends_on_question.id
    question_data['depends_on_value'] = question.depends_on_value

# Category-level conditional logic
if category.depends_on_category:
    category_data['category']['depends_on_category'] = category.depends_on_category.id
    category_data['category']['depends_on_category_name'] = category.depends_on_category.name
    category_data['category']['depends_on_question_text'] = category.depends_on_question_text
    category_data['category']['depends_on_value'] = category.depends_on_value
```

✅ **INCLUDES BOTH CATEGORY AND QUESTION CONDITIONAL FIELDS**

---

### 1.2 Alumni Survey Endpoint (ActiveSurveyQuestionsView)
**File:** `Backend/survey_app/views/alumni_views.py`  
**Route:** `/api/survey/questions/`  
**Permission:** `CanRespondToSurveys` (authenticated alumni)

#### Data Structure Sent:
```python
{
    'template': {
        'id': int,
        'name': str,
        'description': str
    },
    'categories': [
        {
            'category': SurveyCategorySerializer(category).data,  # Uses serializer
            'questions': ActiveSurveyQuestionsSerializer(questions).data  # Uses serializer
        }
    ]
}
```

#### SurveyCategorySerializer Fields:
```python
fields = [
    'id', 'name', 'description', 'order', 'is_active', 'include_in_registration',
    'depends_on_category', 'depends_on_category_name',  # ✅ INCLUDED
    'depends_on_question_text', 'depends_on_value',  # ✅ INCLUDED
    'active_questions_count', 'total_questions_count', 'created_by', 'created_by_name',
    'created_at', 'updated_at'
]
```

#### ActiveSurveyQuestionsSerializer Fields:
```python
fields = [
    'id', 'category', 'question_text', 'question_type',
    'placeholder_text', 'help_text', 'options', 'is_required',
    'min_value', 'max_value', 'max_length', 'order', 'user_response'
    # ❌ MISSING: 'depends_on_question_id', 'depends_on_value'
]
```

❌ **MISSING QUESTION-LEVEL CONDITIONAL FIELDS IN SERIALIZER**

---

## 2. FRONTEND ANALYSIS

### 2.1 RegisterDynamic.vue - Category-Level Conditional Logic

#### Function: shouldShowCategory
```javascript
const shouldShowCategory = (categoryData) => {
  const category = categoryData.category;
  
  // If no conditional logic, show the category
  if (!category.depends_on_category) {
    return true;
  }
  
  // Check if the dependency condition is met
  const dependsOnCategoryId = category.depends_on_category;
  const dependsOnQuestionText = category.depends_on_question_text;
  const dependsOnValue = JSON.parse(category.depends_on_value || '[]');
  
  // Find the response for the dependency question
  const dependencyCategoryData = surveyCategories.value.find(
    cat => cat.category.id === dependsOnCategoryId
  );
  
  if (!dependencyCategoryData) return false;
  
  // Find the specific question in the dependency category
  const dependencyQuestion = dependencyCategoryData.questions.find(
    q => q.question_text === dependsOnQuestionText
  );
  
  if (!dependencyQuestion) return false;
  
  // Check if user has answered the dependency question with the required value
  const userResponse = surveyResponses.value[dependencyQuestion.id];
  return dependsOnValue.includes(userResponse);
};
```

**Key Features:**
- Parses JSON array for `depends_on_value` (handles multiple valid answers)
- Searches by question text within dependency category
- Uses direct response lookup via question ID
- Returns boolean for visibility

#### Computed: getVisibleCategories
```javascript
const getVisibleCategories = computed(() => {
  return surveyCategories.value.filter(categoryData => shouldShowCategory(categoryData));
});
```

---

### 2.2 DynamicSurveyStep.vue - Question-Level Conditional Logic

#### Computed: getQuestionVisibility
```javascript
const getQuestionVisibility = computed(() => {
  const visibility = {}
  props.questions.forEach(question => {
    // Always show questions without dependencies
    if (!question.depends_on_question_id || !question.depends_on_value) {
      visibility[question.id] = true
      return
    }
    
    // Get the parent question response
    const parentResponse = localResponses[question.depends_on_question_id]
    
    // Hide if no response yet
    if (parentResponse === undefined || parentResponse === null || parentResponse === '') {
      visibility[question.id] = false
      return
    }
    
    // Handle boolean to string conversion for yes/no questions
    let normalizedResponse = parentResponse
    let normalizedRequiredValue = question.depends_on_value
    
    // Convert boolean responses to Yes/No strings for comparison
    if (typeof parentResponse === 'boolean') {
      normalizedResponse = parentResponse ? 'Yes' : 'No'
    }
    
    // Compare values
    const isVisible = String(normalizedResponse) === String(normalizedRequiredValue)
    visibility[question.id] = isVisible
  })
  return visibility
})
```

**Key Features:**
- Returns map of `{questionId: boolean}`
- Normalizes boolean values (true → 'Yes', false → 'No')
- Direct ID-based dependency lookup (simpler than category approach)
- String comparison for flexibility

#### Template Usage:
```vue
<div v-for="question in props.questions" :key="question.id"
     v-show="getQuestionVisibility[question.id]">
  <!-- Question rendering -->
</div>
```

#### Response Cleanup:
```javascript
// Watch for visibility changes and clear hidden question responses
watch(
  getQuestionVisibility,
  (newVisibility, oldVisibility) => {
    props.questions.forEach(question => {
      // If question became hidden, clear its response
      if (oldVisibility && oldVisibility[question.id] && !newVisibility[question.id]) {
        if (question.question_type === 'checkbox') {
          localResponses[question.id] = []
        } else {
          delete localResponses[question.id]
        }
      }
    })
  },
  { deep: true }
)
```

---

### 2.3 Survey.vue - Current State

#### Data Structure (from API):
```javascript
surveyData.value = [
  {
    template: { id, name, description },
    categories: [
      {
        category: { 
          id, name, description, order,
          depends_on_category,  // ✅ Available
          depends_on_category_name,  // ✅ Available
          depends_on_question_text,  // ✅ Available
          depends_on_value  // ✅ Available
        },
        questions: [
          {
            id, question_text, question_type, options, is_required, ...
            // ❌ Missing: depends_on_question_id, depends_on_value
          }
        ]
      }
    ]
  }
]
```

#### Current Behavior:
```javascript
const currentQuestions = computed(() => {
  return currentCategory.value?.questions || []  // ❌ No filtering
})

const totalCategories = computed(() => {
  return currentForm.value?.categories.length || 0  // ❌ No filtering
})
```

**Issues:**
1. ❌ No category visibility filtering
2. ❌ No question visibility filtering
3. ❌ No response cleanup for hidden items
4. ❌ Progress calculations include all questions (not just visible)
5. ❌ Navigation assumes linear category sequence
6. ❌ Required validation on all questions (including potentially hidden ones)

---

## 3. GAP ANALYSIS

### Backend Gaps:
| Feature | Registration API | Alumni API | Action Needed |
|---------|-----------------|------------|---------------|
| Category conditional fields | ✅ Included | ✅ Included | None |
| Question conditional fields | ✅ Included | ❌ **Missing** | **Add to ActiveSurveyQuestionsSerializer** |

### Frontend Gaps (Survey.vue):
| Feature | RegisterDynamic | Survey.vue | Action Needed |
|---------|----------------|------------|---------------|
| Category visibility logic | ✅ Implemented | ❌ Missing | **Implement shouldShowCategory** |
| Question visibility logic | ✅ Implemented | ❌ Missing | **Implement question filtering** |
| Visible category filtering | ✅ Computed | ❌ Missing | **Create visibleCategories computed** |
| Visible question filtering | ✅ v-show | ❌ Missing | **Filter currentQuestions** |
| Response cleanup | ✅ Watcher | ❌ Missing | **Add cleanup watcher** |
| Navigation on visible only | ✅ Yes | ❌ No | **Update nav logic** |
| Progress on visible only | ✅ Yes | ❌ No | **Update progress calcs** |
| Value normalization | ✅ Boolean→String | ❌ Missing | **Add normalization** |

---

## 4. DETAILED DATA FLOW COMPARISON

### 4.1 Registration Flow (WORKING)
```
Backend API
  ↓ Manual field inclusion in RegistrationSurveyQuestionsView
  ↓ Includes depends_on_question_id, depends_on_value
Frontend (RegisterDynamic)
  ↓ Loads via useRegistrationSurvey composable
  ↓ Stores in surveyCategories ref
  ↓ shouldShowCategory filters by category dependencies
  ↓ getVisibleCategories computed provides filtered list
  ↓ DynamicSurveyStep receives questions
  ↓ getQuestionVisibility computed filters by question dependencies
  ↓ v-show hides/shows based on visibility map
  ↓ Watcher clears responses when questions become hidden
  ↓ Validation only on visible required questions
```

### 4.2 Alumni Flow (NOT WORKING)
```
Backend API
  ↓ Uses ActiveSurveyQuestionsSerializer
  ↓ ❌ Does NOT include depends_on_question_id, depends_on_value
Frontend (Survey.vue)
  ↓ Loads via surveyService.getActiveSurveyQuestions()
  ↓ Stores in surveyData ref
  ↓ ❌ No category filtering
  ↓ ❌ No question filtering
  ↓ v-for renders ALL questions
  ❌ All questions always visible
  ❌ No response cleanup
  ❌ Validation on all questions
```

---

## 5. IMPLEMENTATION REQUIREMENTS

### 5.1 Backend Changes (MINIMAL)

#### File: `Backend/survey_app/serializers.py`
**Class: ActiveSurveyQuestionsSerializer**

**Current:**
```python
class ActiveSurveyQuestionsSerializer(serializers.ModelSerializer):
    category = SurveyCategorySerializer(read_only=True)
    user_response = serializers.SerializerMethodField()

    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'category', 'question_text', 'question_type',
            'placeholder_text', 'help_text', 'options', 'is_required',
            'min_value', 'max_value', 'max_length', 'order', 'user_response'
        ]
```

**Required:**
```python
class ActiveSurveyQuestionsSerializer(serializers.ModelSerializer):
    category = SurveyCategorySerializer(read_only=True)
    user_response = serializers.SerializerMethodField()
    depends_on_question_id = serializers.IntegerField(
        source='depends_on_question.id', 
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = SurveyQuestion
        fields = [
            'id', 'category', 'question_text', 'question_type',
            'placeholder_text', 'help_text', 'options', 'is_required',
            'min_value', 'max_value', 'max_length', 'order', 'user_response',
            'depends_on_question_id', 'depends_on_value'  # ADD THESE
        ]
```

---

### 5.2 Frontend Changes (Survey.vue)

#### Phase 1: Add Helper Functions
```javascript
// Normalize values for comparison (handle boolean → string)
const normalizeValue = (value) => {
  if (value === null || value === undefined || value === '') return null
  if (typeof value === 'boolean') return value ? 'Yes' : 'No'
  return String(value)
}

// Parse dependency values (handle JSON arrays or single strings)
const parseDependencyValue = (depValue) => {
  if (!depValue) return []
  try {
    const parsed = JSON.parse(depValue)
    return Array.isArray(parsed) ? parsed : [parsed]
  } catch (e) {
    return [depValue]
  }
}
```

#### Phase 2: Category Visibility Logic
```javascript
const shouldShowCategory = (categoryWrapper) => {
  if (!categoryWrapper || !categoryWrapper.category) return false
  const cat = categoryWrapper.category
  
  // No dependency = always visible
  if (!cat.depends_on_category) return true
  
  // Find dependency category
  const depCat = currentForm.value.categories.find(
    c => c.category.id === cat.depends_on_category
  )
  if (!depCat) return false
  
  // Find dependency question by text
  const depQuestion = depCat.questions.find(
    q => q.question_text === cat.depends_on_question_text
  )
  if (!depQuestion) return false
  
  // Check user's answer
  const userAnswer = normalizeValue(responses.value[depQuestion.id])
  if (!userAnswer) return false
  
  // Check if answer matches required values
  const requiredValues = parseDependencyValue(cat.depends_on_value)
  return requiredValues.some(val => normalizeValue(val) === userAnswer)
}

const visibleCategories = computed(() => {
  if (!currentForm.value) return []
  return currentForm.value.categories.filter(cat => shouldShowCategory(cat))
})
```

#### Phase 3: Question Visibility Logic
```javascript
const shouldShowQuestion = (question) => {
  if (!question) return false
  
  // No dependency = always visible
  if (!question.depends_on_question_id) return true
  
  // Check dependency answer
  const depAnswer = normalizeValue(responses.value[question.depends_on_question_id])
  if (!depAnswer) return false
  
  // Compare with required value
  const requiredValues = parseDependencyValue(question.depends_on_value)
  return requiredValues.some(val => normalizeValue(val) === depAnswer)
}

const currentQuestions = computed(() => {
  if (!currentCategory.value) return []
  return currentCategory.value.questions.filter(q => shouldShowQuestion(q))
})
```

#### Phase 4: Navigation Updates
```javascript
const visibleCategoryIndices = computed(() => {
  if (!currentForm.value) return []
  return currentForm.value.categories
    .map((c, idx) => ({ c, idx }))
    .filter(({ c }) => shouldShowCategory(c))
    .map(({ idx }) => idx)
})

const totalCategories = computed(() => {
  return visibleCategoryIndices.value.length
})

const isLastCategory = computed(() => {
  const visible = visibleCategoryIndices.value
  if (!visible.length) return true
  return currentCategoryIndex.value === visible[visible.length - 1]
})

const nextCategory = () => {
  if (isLastCategory.value) return
  const visible = visibleCategoryIndices.value
  const currentPos = visible.indexOf(currentCategoryIndex.value)
  if (currentPos !== -1 && currentPos < visible.length - 1) {
    currentCategoryIndex.value = visible[currentPos + 1]
  }
}

const previousCategory = () => {
  const visible = visibleCategoryIndices.value
  const currentPos = visible.indexOf(currentCategoryIndex.value)
  if (currentPos > 0) {
    currentCategoryIndex.value = visible[currentPos - 1]
  }
}
```

#### Phase 5: Response Cleanup
```javascript
// Watch for question visibility changes and cleanup
watch(
  [responses, () => currentQuestions.value.map(q => q.id)],
  () => {
    // Clean up responses for questions that are no longer visible
    if (!currentCategory.value) return
    
    const visibleIds = new Set(currentQuestions.value.map(q => q.id))
    const allQuestionIds = currentCategory.value.questions.map(q => q.id)
    
    allQuestionIds.forEach(qId => {
      if (!visibleIds.has(qId) && responses.value[qId] !== undefined) {
        // Question is hidden but has a response - clean it up
        const question = currentCategory.value.questions.find(q => q.id === qId)
        if (question?.question_type === 'checkbox') {
          responses.value[qId] = []
        } else {
          delete responses.value[qId]
        }
      }
    })
  },
  { deep: true }
)
```

#### Phase 6: Progress Calculations (Visible Only)
```javascript
const getFormProgress = (formIndex) => {
  const form = surveyData.value[formIndex]
  if (!form || !form.categories) return { answered: 0, total: 0, percentage: 0 }
  
  let totalQuestions = 0
  let answeredQuestions = 0
  
  form.categories.forEach(cat => {
    if (!shouldShowCategory(cat)) return  // Skip hidden categories
    
    cat.questions.forEach(q => {
      if (!shouldShowQuestion(q)) return  // Skip hidden questions
      
      totalQuestions++
      const response = responses.value[q.id]
      if (response !== undefined && response !== '' && response !== null) {
        answeredQuestions++
      }
    })
  })
  
  return {
    answered: answeredQuestions,
    total: totalQuestions,
    percentage: totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0
  }
}
```

#### Phase 7: Validation (Visible Required Only)
```javascript
const canGoNext = computed(() => {
  if (!currentCategory.value) return false
  
  // Only validate visible required questions
  const visibleRequired = currentQuestions.value.filter(q => q.is_required)
  return visibleRequired.every(q => {
    const response = responses.value[q.id]
    return response !== undefined && response !== '' && response !== null
  })
})
```

---

## 6. EDGE CASES & SAFEGUARDS

### 6.1 Circular Dependencies
**Risk:** Category A depends on Category B, Category B depends on Category A  
**Solution:** Track visited categories during evaluation; if cycle detected, return false

### 6.2 Missing Dependency Question
**Risk:** Question depends on ID 999 but that question doesn't exist  
**Solution:** Return false (hide dependent question), log warning in console

### 6.3 Malformed JSON in depends_on_value
**Risk:** `depends_on_value` contains invalid JSON  
**Solution:** Try-catch in parseDependencyValue; fallback to raw string comparison

### 6.4 Type Mismatches
**Risk:** Boolean response vs string "Yes" comparison  
**Solution:** normalizeValue function handles all type conversions

### 6.5 All Categories Hidden
**Risk:** User answers make all categories invisible  
**Solution:** Check visibleCategories.length; if 0, show message and auto-close form

### 6.6 Hidden Required Questions
**Risk:** Required question hidden but counted in validation  
**Solution:** Filter by currentQuestions (already filtered for visibility)

---

## 7. TESTING STRATEGY

### 7.1 Unit Tests (Manual Console Testing)
- [ ] Category with no dependency shows always
- [ ] Category with met dependency shows
- [ ] Category with unmet dependency hides
- [ ] Question with no dependency shows always
- [ ] Question with met dependency shows
- [ ] Question with unmet dependency hides
- [ ] Boolean value normalization (true → 'Yes')
- [ ] JSON array parsing for multiple valid answers
- [ ] Response cleanup when question becomes hidden

### 7.2 Integration Tests
- [ ] Navigate through form with conditional categories
- [ ] Answer dependency question, verify dependent category appears
- [ ] Change dependency answer, verify dependent category disappears
- [ ] Verify progress only counts visible questions
- [ ] Verify submit only sends visible question responses
- [ ] Verify required validation only on visible questions

### 7.3 Regression Tests
- [ ] Forms without conditional logic still work
- [ ] Existing cache behavior unchanged
- [ ] Submission flow filters empty responses as before
- [ ] Card view progress calculations accurate

---

## 8. IMPLEMENTATION ORDER

1. ✅ **Backend:** Add conditional fields to ActiveSurveyQuestionsSerializer
2. ✅ **Frontend:** Add normalizeValue and parseDependencyValue helpers
3. ✅ **Frontend:** Implement shouldShowCategory and visibleCategories
4. ✅ **Frontend:** Implement shouldShowQuestion and filter currentQuestions
5. ✅ **Frontend:** Update navigation to use visibleCategoryIndices
6. ✅ **Frontend:** Update progress calculations for visible only
7. ✅ **Frontend:** Update validation for visible required only
8. ✅ **Frontend:** Add response cleanup watcher
9. ✅ **Testing:** Verify conditional logic works end-to-end
10. ✅ **Testing:** Verify non-conditional forms still work

---

## 9. RISK MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Backend field missing | Low | High | Use allow_null=True, check data in console |
| Circular dependencies | Low | Medium | Add cycle detection in shouldShowCategory |
| Performance degradation | Medium | Low | Use Set for visible IDs, avoid nested loops |
| Hidden required blocking | High | High | Filter by currentQuestions before validation |
| Stale hidden responses | High | Medium | Cleanup watcher removes hidden responses |
| All categories hidden | Low | Medium | Check visibleCategories.length, show message |

---

## 10. SUMMARY

**Root Cause:** ActiveSurveyQuestionsSerializer does not include `depends_on_question_id` and `depends_on_value` fields.

**Solution:** 
1. Add 2 fields to backend serializer (1 file, ~4 lines)
2. Add conditional logic to Survey.vue (~150 lines total)
3. Reuse proven patterns from RegisterDynamic + DynamicSurveyStep

**Complexity:** Medium (proven patterns exist, just need adaptation)

**Testing:** Medium (requires end-to-end verification)

**Risk:** Low (isolated changes, backward compatible)

---

**Ready for implementation upon approval.**
