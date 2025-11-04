# SurveyManagement.vue Refactoring - Visual Structure

## Current Structure (Monolithic)
```
SurveyManagement.vue (1,884 lines)
├── Script (658 lines)
│   ├── State Management (129 lines)
│   ├── Computed Properties (88 lines)
│   └── Functions (441 lines)
└── Template (1,226 lines)
    ├── Header
    ├── Tab Navigation
    ├── Categories Tab
    ├── Questions Tab
    ├── Analytics Tab
    └── 5 Modals
```

## New Structure (Modularized)

```
SurveyManagement.vue (NEW - ~150 lines, Main Orchestrator)
│
├── Composables/
│   ├── useSurveyManagementLogic.js (~80 lines)
│   │   ├── loading
│   │   ├── activeTab
│   │   ├── categories
│   │   ├── questions
│   │   ├── analytics
│   │   ├── loadCategories()
│   │   ├── loadQuestions()
│   │   └── loadAnalytics()
│   │
│   ├── useCategoryManagement.js (~90 lines)
│   │   ├── categoryForm
│   │   ├── selectedCategoryForModal
│   │   ├── categoryQuestions
│   │   ├── showCategoryModal
│   │   ├── openCategoryModal()
│   │   ├── saveCategory()
│   │   ├── deleteCategory()
│   │   └── selectCategory()
│   │
│   ├── useQuestionManagement.js (~120 lines)
│   │   ├── questionForm
│   │   ├── showQuestionModal
│   │   ├── selectedCategory
│   │   ├── availableQuestions (computed)
│   │   ├── openQuestionModal()
│   │   ├── saveQuestion()
│   │   ├── closeQuestionModal()
│   │   ├── deleteQuestion()
│   │   ├── addOption()
│   │   └── removeOption()
│   │
│   ├── useExportManagement.js (~150 lines)
│   │   ├── exportFormat
│   │   ├── exportCategory
│   │   ├── exportDateFrom
│   │   ├── exportDateTo
│   │   ├── exportProfileFields
│   │   ├── showExportModal
│   │   ├── isExporting
│   │   └── exportData()
│   │
│   ├── useDraggableModals.js (~85 lines)
│   │   ├── isDragging
│   │   ├── draggedModal
│   │   ├── dragOffset
│   │   ├── modalPositions
│   │   ├── startDrag()
│   │   ├── onDrag()
│   │   ├── stopDrag()
│   │   └── resetModalPosition()
│   │
│   └── usePaginationLogic.js (~95 lines)
│       ├── currentCategoryPage
│       ├── currentQuestionPage
│       ├── itemsPerPage
│       ├── totalCategoryPages (computed)
│       ├── totalQuestionPages (computed)
│       ├── paginatedCategories (computed)
│       ├── paginatedQuestions (computed)
│       ├── questionsPageNumbers (computed)
│       ├── questionsPageButtons (computed)
│       ├── questionsEllipsis (computed)
│       ├── goToCategoryPage()
│       └── goToQuestionPage()
│
└── Components/survey/
    ├── SurveyHeader.vue (~30 lines)
    │   ├── Props: none
    │   ├── Emits: export-click
    │   └── Shows: Title, Export button
    │
    ├── SurveyTabNavigation.vue (~35 lines)
    │   ├── Props: activeTab
    │   ├── Emits: update:activeTab
    │   └── Shows: 3 tab buttons
    │
    ├── CategoriesTab.vue (~100 lines)
    │   ├── Props: categories, currentPage, totalPages, loading
    │   ├── Emits: page-change, add-category, edit-category, delete-category, view-questions
    │   └── Shows: Grid + Pagination
    │
    ├── QuestionsTab.vue (~120 lines)
    │   ├── Props: questions, categories, questionTypes, currentPage, totalPages
    │   ├── Emits: page-change, add-question, edit-question, delete-question
    │   └── Shows: Table + Pagination
    │
    ├── AnalyticsTab.vue (~60 lines)
    │   ├── Props: analytics, loading
    │   ├── Emits: none
    │   └── Shows: 4 metric cards
    │
    ├── CategoryModal.vue (~85 lines)
    │   ├── Props: show, category, isDragging, modalPosition
    │   ├── Emits: close, save, drag-start, reset-position
    │   └── Shows: Category create/edit form
    │
    ├── QuestionModal.vue (~200 lines)
    │   ├── Props: show, question, categories, availableQuestions, questionTypes, isDragging, modalPosition
    │   ├── Emits: close, save, drag-start, reset-position
    │   └── Shows: Question create/edit form with conditional logic
    │
    ├── AnalyticsModal.vue (~70 lines)
    │   ├── Props: show, analytics, isDragging, modalPosition
    │   ├── Emits: close, drag-start, reset-position
    │   └── Shows: Analytics dashboard
    │
    ├── ExportModal.vue (~110 lines)
    │   ├── Props: show, categories, isDragging, modalPosition, isExporting
    │   ├── Emits: close, export, drag-start, reset-position
    │   └── Shows: Export configuration
    │
    └── CategoryQuestionsModal.vue (~80 lines)
        ├── Props: show, category, questions, questionTypes, isDragging, modalPosition
        ├── Emits: close, edit-question, delete-question, create-question, drag-start, reset-position
        └── Shows: Category questions table
```

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│         SurveyManagement.vue (Main Orchestrator)                 │
│         ~150 lines - Coordinates everything                      │
└─────────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    ┌───────────────────┐  ┌────────────────────┐  ┌──────────────┐
    │  Composables      │  │  Components        │  │   surveyService
    │  (Business Logic) │  │  (UI Display)      │  │   (API Calls)
    └───────────────────┘  └────────────────────┘  └──────────────┘
        │                       │
        ├─ useSurveyManagement  ├─ SurveyHeader
        │  Logic                ├─ SurveyTabNav
        ├─ useCategoryManagement├─ CategoriesTab
        ├─ useQuestionManagement├─ QuestionsTab
        ├─ useExportManagement  ├─ AnalyticsTab
        ├─ useDraggableModals   ├─ CategoryModal
        └─ usePaginationLogic   ├─ QuestionModal
                                ├─ AnalyticsModal
                                ├─ ExportModal
                                └─ CategoryQuestionsModal
```

## Communication Pattern

```
User Action
    │
    ▼
Component Emits Event
    │
    ▼
Main Component Receives Event
    │
    ▼
Calls Composable Function
    │
    ├─ Updates State
    └─ Calls API (surveyService)
    │
    ▼
API Response
    │
    ▼
Updates Composable State
    │
    ▼
Components Re-render (Reactive)
    │
    ▼
UI Updates Automatically
```

## Complexity Reduction

### Before (Monolithic)
- One file to maintain: 1,884 lines
- 6 modal logics mixed together
- 41 variables in one scope
- Hard to find related code
- Difficult to test individual features

### After (Modularized)
```
Main Component:        ~150 lines  (Orchestration)
Composables:          ~625 lines  (Business logic)
Components:           ~890 lines  (UI display)
────────────────────────────────
Total:              ~1,665 lines  (More organized!)

Benefits:
✅ Each file has single responsibility
✅ Easy to locate related code
✅ Simple to unit test
✅ Reusable logic across app
✅ Cleaner prop drilling
✅ Better performance tracking
✅ Team can work in parallel
```

## File Structure on Disk

```
Frontend/
├── src/
│   ├── views/
│   │   └── SuperAdmin/
│   │       ├── SurveyManagement.vue (REFACTORED - 150 lines)
│   │       ├── SurveyManagement.vue.backup (ORIGINAL - 1,884 lines)
│   │       ├── REFACTORING_PLAN.md (Documentation)
│   │       └── [Other files...]
│   │
│   ├── composables/
│   │   ├── useSurveyManagementLogic.js (NEW)
│   │   ├── useCategoryManagement.js (NEW)
│   │   ├── useQuestionManagement.js (NEW)
│   │   ├── useExportManagement.js (NEW)
│   │   ├── useDraggableModals.js (NEW)
│   │   └── usePaginationLogic.js (NEW)
│   │
│   └── components/
│       └── survey/
│           ├── SurveyHeader.vue (NEW)
│           ├── SurveyTabNavigation.vue (NEW)
│           ├── CategoriesTab.vue (NEW)
│           ├── QuestionsTab.vue (NEW)
│           ├── AnalyticsTab.vue (NEW)
│           ├── CategoryModal.vue (NEW)
│           ├── QuestionModal.vue (NEW)
│           ├── AnalyticsModal.vue (NEW)
│           ├── ExportModal.vue (NEW)
│           └── CategoryQuestionsModal.vue (NEW)
```

## State Management Overview

### Composable States
```
useSurveyManagementLogic:
  loading ────┐
  activeTab ──┼─→ UI Rendering
  categories ─┤
  questions ──┤
  analytics ──┘

useCategoryManagement:
  categoryForm ──┐
  showCategoryModal ─┼─→ Category Modal Display
  selectedCategory ─┤
  categoryQuestions ┘

useQuestionManagement:
  questionForm ──┐
  showQuestionModal ─┼─→ Question Modal Display
  selectedCategory ──┤
  availableQuestions ┘

useExportManagement:
  exportFormat ─────┐
  exportCategory ───┼─→ Export Modal Display
  exportDateFrom ───┤
  exportDateTo ──┐  │
  exportProfileFields ┤
  showExportModal ────┘

useDraggableModals:
  isDragging ────┐
  draggedModal ──┼─→ Modal Positioning
  dragOffset ────┤
  modalPositions ┘

usePaginationLogic:
  currentCategoryPage ──┐
  currentQuestionPage ──┼─→ Pagination Display
  itemsPerPage ─────────┤
  totalCategoryPages ───┤
  totalQuestionPages ───┘
```

