# SurveyManagement.vue Refactoring Plan

## Executive Summary
- **Original File Size**: 1,884 lines
- **Current Status**: Monolithic component
- **Refactoring Goal**: Break into modular components and composables
- **Expected Result**: 50% code reduction with improved maintainability
- **All Functionalities**: ✅ Will be preserved
- **UI/Styling**: ✅ Will remain identical
- **Backup Created**: ✅ SurveyManagement.vue.backup

---

## DETAILED LINE-BY-LINE ANALYSIS

### SCRIPT SECTION (Lines 1-658)

#### Section 1: IMPORTS (Lines 1-22)
**Lines**: 1-22 | **Function**: Import dependencies
```javascript
- Vue 3 Composition API: ref, onMounted, onUnmounted, computed, nextTick
- 22 Lucide Vue icons
- surveyService for API calls
```
**Refactoring**: Import statements to remain in each component/composable as needed

---

#### Section 2: REACTIVE DATA INITIALIZATION (Lines 27-47)
**Lines**: 27-47 | **Variables**: 14 ref() calls
```
✓ loading (Boolean) - App-wide loading state
✓ activeTab (String: 'categories'|'questions'|'analytics')
✓ categories (Array) - List of survey categories
✓ questions (Array) - List of survey questions
✓ selectedCategory (Object) - Currently selected category
✓ showCategoryModal (Boolean) - Category modal visibility
✓ showQuestionModal (Boolean) - Question modal visibility
✓ showAnalyticsModal (Boolean) - Analytics modal visibility
✓ showExportModal (Boolean) - Export modal visibility
✓ showCategoryQuestionsModal (Boolean) - Category questions modal visibility
✓ selectedCategoryForModal (Object) - Category selected in modal
✓ categoryQuestions (Array) - Questions in selected category
✓ analytics (Object) - Analytics data
```
**Refactoring Location**: 
- Split into multiple composables:
  - `usesurveyManagementLogic.js`: loading, activeTab, categories, questions, analytics
  - `useCategoryManagement.js`: selectedCategory, showCategoryModal, selectedCategoryForModal, categoryQuestions
  - `useQuestionManagement.js`: showQuestionModal
  - `useExportManagement.js`: showExportModal
  - `useDraggableModals.js`: Modal position tracking

---

#### Section 3: EXPORT DATA STATE (Lines 49-71)
**Lines**: 49-71 | **Variables**: 8 ref() calls
```
✓ exportFormat (String: 'xlsx'|'json')
✓ exportCategory (String) - Category ID filter
✓ includeInactive (Boolean) - Include inactive questions
✓ exportDateFrom (String) - Start date
✓ exportDateTo (String) - End date
✓ exportProfileFields (Array) - Selected profile fields
✓ isExporting (Boolean) - Export loading state
```
**Purpose**: Manage export modal state and configuration
**Refactoring Location**: `useExportManagement.js` composable

---

#### Section 4: PAGINATION STATE (Lines 73-76)
**Lines**: 73-76 | **Variables**: 3 ref() calls
```
✓ currentCategoryPage (Number: 1)
✓ currentQuestionPage (Number: 1)
✓ itemsPerPage (Constant: 6)
```
**Purpose**: Track pagination for categories and questions tabs
**Refactoring Location**: `usePaginationLogic.js` composable

---

#### Section 5: PAGINATION COMPUTED PROPERTIES (Lines 78-165)
**Lines**: 78-165 | **Functions**: 7 computed properties
```
1. totalCategoryPages - Calculates max category pages
   └─ Math.ceil(categories.length / itemsPerPage)

2. totalQuestionPages - Calculates max question pages
   └─ Math.ceil(questions.length / itemsPerPage)

3. paginatedCategories - Returns sliced categories for current page
   └─ Complex slice logic with page offset

4. paginatedQuestions - Returns sliced questions for current page
   └─ Complex slice logic with page offset

5. questionsPageNumbers - Generates page numbers with smart ellipsis
   └─ Handles edge cases: 7 pages, start, middle, end of range
   └─ Adds "..." for skipped pages

6. questionsPageButtons - Filters out ellipsis from page numbers
   └─ Used for buttons in pagination

7. questionsEllipsis - Extracts ellipsis elements
   └─ Used for "..." display in pagination

8. availableQuestions - Filters questions for conditional logic
   └─ Only yes_no type or radio with Yes/No options
   └─ Excludes current question being edited
```
**Refactoring Location**: `usePaginationLogic.js` composable

---

#### Section 6: PAGINATION FUNCTIONS (Lines 167-176)
**Lines**: 167-176 | **Functions**: 2
```
1. goToCategoryPage(page) 
   └─ Validates page range
   └─ Sets currentCategoryPage

2. goToQuestionPage(page)
   └─ Validates page range
   └─ Sets currentQuestionPage
```
**Refactoring Location**: `usePaginationLogic.js` composable

---

#### Section 7: MODAL DATA & FORMS (Lines 178-239)
**Lines**: 178-239 | **Data Structures**: 3
```
1. categoryForm (Object) - Category edit/create form
   ├─ id (Number|null)
   ├─ name (String)
   ├─ description (String)
   ├─ order (Number)
   └─ is_active (Boolean)

2. questionForm (Object) - Question edit/create form
   ├─ id (Number|null)
   ├─ category (Number|null)
   ├─ question_text (String)
   ├─ question_type (String)
   ├─ options (Array)
   ├─ is_required (Boolean)
   ├─ order (Number)
   ├─ is_active (Boolean)
   ├─ placeholder_text (String)
   ├─ help_text (String)
   ├─ min_value (Number|null)
   ├─ max_value (Number|null)
   ├─ max_length (Number|null)
   ├─ depends_on_question (Number|null)
   └─ depends_on_value (String)

3. questionTypes (Array) - 10 question type options
   └─ Each has: value, label, hasOptions (boolean)
```
**Refactoring Location**: 
- `useCategoryManagement.js`: categoryForm
- `useQuestionManagement.js`: questionForm, questionTypes constant

---

#### Section 8: DRAGGABLE MODAL LOGIC (Lines 241-310)
**Lines**: 241-310 | **Functions**: 4 + State management
```
State Variables:
✓ isDragging (Boolean) - Track if dragging
✓ draggedModal (String) - Which modal type: 'category'|'question'|'analytics'|'export'|'categoryQuestions'
✓ dragOffset (Object) - {x, y} offset for cursor position
✓ modalPositions (Object) - Track position of each modal type

Functions:
1. startDrag(event, modalType)
   └─ Initialize drag on mousedown
   └─ Calculate offset
   └─ Attach mousemove/mouseup listeners

2. onDrag(event)
   └─ Calculate new position
   └─ Apply viewport bounds
   └─ Update transform styles

3. stopDrag()
   └─ Clean up event listeners
   └─ Reset drag state

4. resetModalPosition(modalType)
   └─ Reset specific modal to origin
   └─ Use nextTick for DOM updates
```
**Refactoring Location**: `useDraggableModals.js` composable

---

#### Section 9: DATA LOADING FUNCTIONS (Lines 312-335)
**Lines**: 312-335 | **Functions**: 3 API calls
```
1. loadCategories()
   └─ Calls: surveyService.getCategories()
   └─ Updates: categories.value
   └─ Error handling: console.error

2. loadQuestions(categoryId = null)
   └─ Calls: surveyService.getQuestions(categoryId)
   └─ Updates: questions.value
   └─ Parameters: Optional category filter
   └─ Error handling: console.error

3. loadAnalytics()
   └─ Calls: surveyService.getAnalytics()
   └─ Updates: analytics.value
   └─ Error handling: console.error
```
**Refactoring Location**: `usesurveyManagementLogic.js` composable

---

#### Section 10: CATEGORY MANAGEMENT (Lines 337-401)
**Lines**: 337-401 | **Functions**: 3 CRUD operations
```
1. openCategoryModal(category = null)
   └─ If editing: Copy category data into categoryForm
   └─ If creating: Initialize empty form with order=length
   └─ Sets: showCategoryModal = true

2. saveCategory()
   └─ If categoryForm.id exists: Update (surveyService.updateCategory)
   └─ If new: Create (surveyService.createCategory)
   └─ After save: Close modal, reload categories
   └─ Error handling: console.error

3. deleteCategory(id)
   └─ Confirms with alert
   └─ Optimistic UI update: Remove from array
   └─ API call: surveyService.deleteCategory
   └─ Reload categories from server
   └─ On error: Restore category to array
```
**Refactoring Location**: `useCategoryManagement.js` composable

---

#### Section 11: QUESTION MANAGEMENT (Lines 403-479)
**Lines**: 403-479 | **Functions**: 3 CRUD operations
```
1. openQuestionModal(question = null)
   └─ If editing: Deep copy question with options array
   └─ If creating: Initialize empty form with category filter
   └─ Sets: showQuestionModal = true

2. saveQuestion()
   └─ If questionForm.id exists: Update
   └─ If new: Create
   └─ After save: Close modal, reload questions, reload categories (for counters)
   └─ Error handling: Detailed error parsing for 400 responses
   └─ Shows specific validation errors to user

3. closeQuestionModal()
   └─ Closes modal
   └─ Resets questionForm to initial state (prevents null refs)

4. deleteQuestion(id)
   └─ Confirms with alert
   └─ Optimistic UI update: Remove from array
   └─ API call: surveyService.deleteQuestion
   └─ Reload questions and categories
   └─ On error: Restore question to array
```
**Refactoring Location**: `useQuestionManagement.js` composable

---

#### Section 12: OPTIONS MANAGEMENT (Lines 481-496)
**Lines**: 481-496 | **Functions**: 2
```
1. addOption()
   └─ Pushes empty string to questionForm.options
   └─ Used by: Choice/Checkbox/Select question types

2. removeOption(index)
   └─ Removes option at index from questionForm.options
   └─ Used for: Dynamic option removal
```
**Refactoring Location**: `useQuestionManagement.js` composable

---

#### Section 13: LIFECYCLE HOOKS (Lines 498-518)
**Lines**: 498-518 | **Functions**: 2
```
1. onMounted()
   └─ Loads: Categories, Questions (all), Analytics
   └─ Sets: loading = false
   └─ Adds global event listeners for drag (mousemove, mouseup)

2. onUnmounted()
   └─ Cleans up: Removes event listeners
   └─ Prevents: Memory leaks
```
**Refactoring Location**: Main component or usesurveyManagementLogic

---

#### Section 14: ADDITIONAL HANDLERS (Lines 520-546)
**Lines**: 520-546 | **Functions**: 3
```
1. selectCategory(category)
   └─ Sets selectedCategoryForModal = category
   └─ Loads questions for that category
   └─ Shows showCategoryQuestionsModal = true

2. goToQuestionsTab()
   └─ Switches to questions tab
   └─ Clears selectedCategory filter
   └─ Resets pagination
   └─ Loads ALL questions

3. (Export handler - see section 15)
```
**Refactoring Location**: 
- `useCategoryManagement.js`: selectCategory
- Main component: goToQuestionsTab (tab logic)

---

#### Section 15: EXPORT FUNCTIONALITY (Lines 520-658)
**Lines**: 520-658 | **Functions**: 1 complex function
```
exportData() - 138 lines of complex logic
├─ Checks: isExporting flag to prevent duplicate calls
├─ Builds: exportParams object
│  ├─ format (xlsx|json)
│  ├─ category_id (optional)
│  ├─ date_from (optional)
│  ├─ date_to (optional)
│  └─ include_profile_fields (array)
├─ API Call: surveyService.exportResponses(exportParams)
├─ File Handling:
│  ├─ Creates Blob from response
│  ├─ Generates download URL
│  ├─ Creates <a> element
│  ├─ Sets filename with timestamp
│  ├─ Triggers download
│  └─ Cleans up resources
├─ Modal: Closes showExportModal
├─ Success: Logs completion
├─ Error: Shows alert, logs error
└─ Finally: Resets isExporting flag
```
**Refactoring Location**: `useExportManagement.js` composable

---

### TEMPLATE SECTION (Lines 659-1884)

#### Template 1: HEADER SECTION (Lines 659-679)
**Lines**: 659-679 | **Components**: Title + Export Button
```html
<div class="min-h-screen bg-gradient-to-br from-slate-50 to-orange-50">
  <!-- Header with title, description, export button -->
  <button @click="showExportModal = true">
    <Download icon />
    Export Data
  </button>
</div>
```
**Refactoring Component**: `SurveyHeader.vue`
**Props**: None
**Emits**: `export-click`

---

#### Template 2: TAB NAVIGATION (Lines 681-721)
**Lines**: 681-721 | **Components**: 3 Tab buttons
```html
<nav class="flex space-x-1 p-2">
  <button @click="activeTab = 'categories'">Categories</button>
  <button @click="goToQuestionsTab">Questions</button>
  <button @click="activeTab = 'analytics'">Analytics</button>
</nav>
```
**Styling**: Conditional classes for active state
**Refactoring Component**: `SurveyTabNavigation.vue`
**Props**: 
- `activeTab` (String)
**Emits**: 
- `update:activeTab`

---

#### Template 3: LOADING STATE (Lines 723-731)
**Lines**: 723-731 | **Display**: Spinner + message
```html
<div v-if="loading" class="flex justify-center py-16">
  <spinner animation />
  <p>Loading survey data...</p>
</div>
```
**Refactoring Location**: Main component or SurveyHeader

---

#### Template 4: CATEGORIES TAB (Lines 733-883)
**Lines**: 733-883 | **Components**: Grid + Pagination
```html
<!-- Section Header -->
- Title, Description, Add Category button

<!-- Category Grid -->
- 3-column grid (lg), 2-column (md), 1-column (sm)
- Card per category showing:
  ├─ Name & Description
  ├─ Edit/Delete buttons
  ├─ Question count + status bar
  ├─ Active/Inactive badge
  └─ View Questions button

<!-- Pagination -->
- Previous button (disabled if page=1)
- Page number buttons (max 5)
- Next button (disabled if page=last)
```
**Refactoring Component**: `CategoriesTab.vue`
**Props**:
- `categories` (Array)
- `currentPage` (Number)
- `totalPages` (Number)
- `loading` (Boolean)
**Emits**:
- `page-change`
- `add-category`
- `edit-category`
- `delete-category`
- `view-questions`

---

#### Template 5: QUESTIONS TAB (Lines 885-1130)
**Lines**: 885-1130 | **Components**: Table + Pagination
```html
<!-- Section Header -->
- Title, Description, Add Question button

<!-- Questions Table -->
Columns:
1. Question (text + help_text)
2. Category (badge)
3. Type (badge)
4. Required (Yes/No badge)
5. Status (Active/Inactive badge)
6. Responses (count)
7. Conditional (Icon if conditional logic)
8. Actions (Edit/Delete buttons)

<!-- Empty State -->
- Icon, message, Create First Question button

<!-- Pagination -->
- Previous/Next buttons
- Page number buttons with ellipsis
- Record count display
```
**Refactoring Component**: `QuestionsTab.vue`
**Props**:
- `questions` (Array)
- `categories` (Array)
- `questionTypes` (Array)
- `currentPage` (Number)
- `totalPages` (Number)
**Emits**:
- `page-change`
- `add-question`
- `edit-question`
- `delete-question`

---

#### Template 6: ANALYTICS TAB (Lines 1132-1245)
**Lines**: 1132-1245 | **Components**: 4 Cards + Info boxes
```html
<!-- Analytics Cards -->
1. Total Questions
   ├─ Icon: FileCheck
   └─ Value: analytics.total_questions

2. Total Responses
   ├─ Icon: TrendingUp
   └─ Value: analytics.total_responses

3. Active Users
   ├─ Icon: Users
   └─ Value: analytics.total_users_responded

4. Completion Rate
   ├─ Icon: BarChart3
   └─ Value: analytics.completion_rate + "%"

<!-- Info Boxes -->
- Response Trends placeholder
- Category Distribution placeholder
```
**Refactoring Component**: `AnalyticsTab.vue`
**Props**:
- `analytics` (Object)
- `loading` (Boolean)

---

#### Template 7: CATEGORY MODAL (Lines 1249-1346)
**Lines**: 1249-1346 | **Type**: Draggable Modal
```html
<!-- Draggable Header -->
- Title: "Edit Category" or "Create New Category"
- Move icon + Reset position button
- @mousedown="startDrag($event, 'category')"

<!-- Form -->
1. Category Name (text input, required)
2. Description (textarea)
3. Display Order (number input)
4. Active checkbox

<!-- Actions -->
- Cancel button
- Save button
```
**Refactoring Component**: `CategoryModal.vue`
**Props**:
- `show` (Boolean)
- `category` (Object|null)
- `isDragging` (Boolean)
- `modalPosition` (Object)
**Emits**:
- `close`
- `save`
- `drag-start`
- `reset-position`

---

#### Template 8: QUESTION MODAL (Lines 1348-1590)
**Lines**: 1348-1590 | **Type**: Draggable Modal (Largest)
```html
<!-- Draggable Header -->
- Title: "Edit Question" or "Create New Question"
- Move icon + Reset button

<!-- Form Sections -->
1. Category Selection (dropdown, required)
2. Question Text (textarea, required)
3. Question Type (select, required)
4. Display Order (number)

5. Options Section (if hasOptions)
   ├─ Dynamic inputs for each option
   ├─ Add Option button
   └─ Remove Option button

6. Placeholder & Help Text (text inputs)

7. Rating Min/Max (if type='rating')
   ├─ Minimum Value (number, required)
   └─ Maximum Value (number, required)

8. Conditional Logic Section
   ├─ Depends on Question (dropdown)
   └─ Show when answer is (select: Yes/No)

9. Checkboxes
   ├─ Required Question
   └─ Active Question

<!-- Actions -->
- Cancel button
- Save button
```
**Refactoring Component**: `QuestionModal.vue`
**Props**:
- `show` (Boolean)
- `question` (Object|null)
- `categories` (Array)
- `availableQuestions` (Array)
- `questionTypes` (Array)
- `isDragging` (Boolean)
- `modalPosition` (Object)
**Emits**:
- `close`
- `save`
- `drag-start`
- `reset-position`

---

#### Template 9: ANALYTICS MODAL (Lines 1592-1686)
**Lines**: 1592-1686 | **Type**: Draggable Modal
```html
<!-- Draggable Header -->
- Title: "Survey Analytics Dashboard"
- Purple gradient background
- Reset button

<!-- Content -->
- Same 4 metric cards as Analytics Tab
- Grid layout with 4 columns (lg), 2 (md), 1 (sm)

<!-- Close Button -->
- "Close Dashboard" button
```
**Refactoring Component**: `AnalyticsModal.vue`
**Props**:
- `show` (Boolean)
- `analytics` (Object)
- `isDragging` (Boolean)
- `modalPosition` (Object)
**Emits**:
- `close`
- `drag-start`
- `reset-position`

---

#### Template 10: EXPORT MODAL (Lines 1688-1836)
**Lines**: 1688-1836 | **Type**: Draggable Modal (Large)
```html
<!-- Draggable Header -->
- Title: "Export Survey Data"
- Subtitle: "Choose export format and filters"

<!-- Content Sections -->
1. Export Format (2 buttons)
   ├─ JSON Data
   └─ Excel File

2. Category Filter (dropdown)
   └─ All Categories | Individual categories

3. Date Range Filter (2 date inputs)
   ├─ From Date
   └─ To Date

4. Profile Fields Selection (if xlsx)
   ├─ Checkboxes for:
   │  ├─ first_name, last_name, email, program
   │  ├─ year_graduated, student_id, birth_date
   │  ├─ user_type, date_joined
   └─ Max height with scroll

5. Export Summary (Info box)
   ├─ Format description
   ├─ Category filter info
   └─ Date range info

<!-- Actions -->
- Cancel button (disabled during export)
- Export button with loading spinner
```
**Refactoring Component**: `ExportModal.vue`
**Props**:
- `show` (Boolean)
- `categories` (Array)
- `isDragging` (Boolean)
- `modalPosition` (Object)
- `isExporting` (Boolean)
**Emits**:
- `close`
- `export` (with params)
- `drag-start`
- `reset-position`

---

#### Template 11: CATEGORY QUESTIONS MODAL (Lines 1838-1884)
**Lines**: 1838-1884 | **Type**: Draggable Modal
```html
<!-- Draggable Header -->
- Title: "Questions in '{category.name}' Category"
- Subtitle: "{count} question(s) found"

<!-- Content -->
Table with columns:
1. Question (with help_text)
2. Type (badge)
3. Required (Yes/No badge)
4. Status (Active/Inactive badge)
5. Responses (count)
6. Actions (Edit/Delete buttons)

<!-- Empty State -->
- Icon, message, Create First Question button

<!-- Close Button -->
- "Close" button (bottom)
```
**Refactoring Component**: `CategoryQuestionsModal.vue`
**Props**:
- `show` (Boolean)
- `category` (Object)
- `questions` (Array)
- `questionTypes` (Array)
- `isDragging` (Boolean)
- `modalPosition` (Object)
**Emits**:
- `close`
- `edit-question`
- `delete-question`
- `create-question`
- `drag-start`
- `reset-position`

---

## COMPOSABLES TO CREATE

### 1. useSurveyManagementLogic.js
**Purpose**: Core data loading and app state
**Exports**:
```javascript
export function useSurveyManagementLogic() {
  return {
    loading,
    activeTab,
    categories,
    questions,
    analytics,
    questionTypes,
    loadCategories(),
    loadQuestions(),
    loadAnalytics()
  }
}
```

### 2. useCategoryManagement.js
**Purpose**: Category CRUD operations
**Exports**:
```javascript
export function useCategoryManagement(categories, categoryForm) {
  return {
    categoryForm,
    openCategoryModal(),
    saveCategory(),
    deleteCategory(),
    selectCategory()
  }
}
```

### 3. useQuestionManagement.js
**Purpose**: Question CRUD operations
**Exports**:
```javascript
export function useQuestionManagement(questions, questionForm) {
  return {
    questionForm,
    openQuestionModal(),
    saveQuestion(),
    closeQuestionModal(),
    deleteQuestion(),
    addOption(),
    removeOption()
  }
}
```

### 4. useExportManagement.js
**Purpose**: Export functionality
**Exports**:
```javascript
export function useExportManagement() {
  return {
    exportFormat,
    exportCategory,
    exportDateFrom,
    exportDateTo,
    exportProfileFields,
    isExporting,
    exportData()
  }
}
```

### 5. useDraggableModals.js
**Purpose**: Drag and drop for modals
**Exports**:
```javascript
export function useDraggableModals() {
  return {
    isDragging,
    draggedModal,
    dragOffset,
    modalPositions,
    startDrag(),
    onDrag(),
    stopDrag(),
    resetModalPosition()
  }
}
```

### 6. usePaginationLogic.js
**Purpose**: Pagination for categories and questions
**Exports**:
```javascript
export function usePaginationLogic(categories, questions) {
  return {
    currentCategoryPage,
    currentQuestionPage,
    itemsPerPage,
    totalCategoryPages,
    totalQuestionPages,
    paginatedCategories,
    paginatedQuestions,
    questionsPageNumbers,
    questionsPageButtons,
    questionsEllipsis,
    goToCategoryPage(),
    goToQuestionPage(),
    availableQuestions()
  }
}
```

---

## COMPONENTS TO CREATE

1. ✅ `SurveyHeader.vue` - Header with title and export button
2. ✅ `SurveyTabNavigation.vue` - Tab navigation
3. ✅ `CategoriesTab.vue` - Categories grid and pagination
4. ✅ `QuestionsTab.vue` - Questions table and pagination
5. ✅ `AnalyticsTab.vue` - Analytics cards
6. ✅ `CategoryModal.vue` - Category create/edit modal
7. ✅ `QuestionModal.vue` - Question create/edit modal
8. ✅ `AnalyticsModal.vue` - Analytics dashboard modal
9. ✅ `ExportModal.vue` - Export configuration modal
10. ✅ `CategoryQuestionsModal.vue` - View category questions modal

---

## EXPECTED RESULTS

### File Reduction
- **Original**: 1,884 lines
- **Main Component**: ~150-200 lines
- **Composables**: ~600 lines total
- **Components**: ~1,000 lines total
- **Total**: ~1,750 lines (but highly organized)

### Benefits
✅ Easier to maintain each component
✅ Better code reusability
✅ Simpler testing
✅ Clearer separation of concerns
✅ Easier to debug issues
✅ Team members can work on different components in parallel

### Preservation
✅ All UI/styling identical
✅ All functionality preserved
✅ All API calls unchanged
✅ All validation/error handling intact
✅ All animations/transitions preserved
✅ Draggable modal functionality maintained
✅ Export functionality unchanged
✅ Pagination logic identical

---

## Implementation Order

1. Create composables directory structure
2. Create composables one by one
3. Create components directory structure
4. Create components one by one
5. Create refactored main SurveyManagement.vue
6. Test all functionality
7. Backup original (already done ✅)

