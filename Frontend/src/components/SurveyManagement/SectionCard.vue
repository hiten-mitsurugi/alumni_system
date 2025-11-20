<template>
  <div
    class="section-card"
    :class="{ 'section-card--dragging': isDragging, 'section-card--conditional': hasConditions }"
    draggable="true"
    @dragstart="handleDragStart"
    @dragend="handleDragEnd"
  >
    <!-- Card Content -->
    <div class="section-card__content" @click="handleCardClick">
      <!-- Header -->
      <div class="section-card__header">
        <h3 class="section-card__title" :title="section.category.name">
          {{ section.category.name }}
        </h3>
        <span class="section-card__order">{{ section.category.order }}</span>
      </div>

      <!-- Description -->
      <p v-if="section.category.page_description" class="section-card__description">
        {{ truncateText(section.category.page_description, 80) }}
      </p>

      <!-- Metadata -->
      <div class="section-card__metadata">
        <span class="section-card__question-count" :title="`${questionCount} questions`">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
            <path d="M8 2a6 6 0 100 12A6 6 0 008 2zm0 10a1 1 0 110-2 1 1 0 010 2zm1-3.5V10H7V6h1a1 1 0 100-2H7v1h2z"/>
          </svg>
          {{ questionCount }}
        </span>

        <span v-if="section.category.page_break" class="section-card__badge section-card__badge--page-break" title="Page break enabled">
          Page Break
        </span>

        <span v-if="hasConditions" class="section-card__badge section-card__badge--conditional" title="Has visibility conditions">
          Conditional
        </span>

        <span v-if="hasBranching" class="section-card__badge section-card__badge--branching" title="Contains branching logic">
          Branching
        </span>

        <span v-if="section.category.include_in_registration" class="section-card__badge section-card__badge--registration" title="Shown in registration">
          Registration
        </span>
      </div>
    </div>

    <!-- Actions -->
    <div class="section-card__actions" @click.stop>
      <button
        class="section-card__action-btn"
        title="Add question"
        @click="handleAddQuestion"
      >
        <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">
          <path d="M8 2a.75.75 0 01.75.75v4.5h4.5a.75.75 0 010 1.5h-4.5v4.5a.75.75 0 01-1.5 0v-4.5h-4.5a.75.75 0 010-1.5h4.5v-4.5A.75.75 0 018 2z"/>
        </svg>
      </button>
      <button
        class="section-card__action-btn"
        title="Edit section"
        @click="handleEdit"
      >
        <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">
          <path d="M11.013 1.427a1.75 1.75 0 012.474 0l1.086 1.086a1.75 1.75 0 010 2.474l-8.61 8.61c-.21.21-.47.364-.756.445l-3.251.93a.75.75 0 01-.927-.928l.929-3.25a1.75 1.75 0 01.445-.758l8.61-8.61zm1.414 1.06a.25.25 0 00-.354 0L10.811 3.75l1.439 1.44 1.263-1.263a.25.25 0 000-.354l-1.086-1.086zM11.189 6.25L9.75 4.81l-6.286 6.287a.25.25 0 00-.064.108l-.558 1.953 1.953-.558a.249.249 0 00.108-.064l6.286-6.286z"/>
        </svg>
      </button>
      <button
        class="section-card__action-btn section-card__action-btn--danger"
        title="Delete section"
        @click="handleDelete"
      >
        <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">
          <path d="M11 1.75V3h2.25a.75.75 0 010 1.5H2.75a.75.75 0 010-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75zM4.496 6.675a.75.75 0 10-1.492.15l.66 6.6A1.75 1.75 0 005.405 15h5.19c.9 0 1.652-.681 1.741-1.576l.66-6.6a.75.75 0 00-1.492-.149l-.66 6.6a.25.25 0 01-.249.225h-5.19a.25.25 0 01-.249-.225l-.66-6.6zM6.5 1.75V3h3V1.75a.25.25 0 00-.25-.25h-2.5a.25.25 0 00-.25.25z"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';

const props = defineProps({
  section: {
    type: Object,
    required: true,
    // Shape: { category: { id, name, order, page_break, page_title, page_description, depends_on_* }, questions: [...] }
  },
});

const emit = defineEmits([
  'section-click',
  'add-question',
  'edit',
  'delete',
  'drag-start',
  'drag-end',
]);

const isDragging = ref(false);

const questionCount = computed(() => props.section.questions?.length || 0);

const hasConditions = computed(() => {
  const cat = props.section.category;
  return !!(cat.depends_on_category || cat.depends_on_question_text || cat.depends_on_value);
});

const hasBranching = computed(() => {
  return props.section.questions?.some(q => q.branching && Object.keys(q.branching).length > 0) || false;
});

function truncateText(text, maxLength) {
  if (!text || text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

function handleCardClick() {
  emit('section-click', props.section);
}

function handleAddQuestion() {
  emit('add-question', props.section.category.id);
}

function handleEdit() {
  emit('edit', props.section);
}

function handleDelete() {
  emit('delete', props.section.category.id);
}

function handleDragStart(event) {
  isDragging.value = true;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.setData('section-id', props.section.category.id);
  emit('drag-start', props.section);
}

function handleDragEnd() {
  isDragging.value = false;
  emit('drag-end', props.section);
}
</script>

<style scoped>
.section-card {
  position: relative;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
  cursor: pointer;
  display: flex;
  gap: 16px;
}

.section-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.section-card--dragging {
  opacity: 0.5;
  cursor: grabbing;
}

.section-card--conditional {
  border-left: 3px solid #f59e0b;
}

.section-card__content {
  flex: 1;
  min-width: 0;
}

.section-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 8px;
}

.section-card__title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.section-card__order {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 4px;
}

.section-card__description {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.section-card__metadata {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.section-card__question-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #6b7280;
}

.section-card__badge {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-card__badge--page-break {
  background: #dbeafe;
  color: #1e40af;
}

.section-card__badge--conditional {
  background: #fef3c7;
  color: #92400e;
}

.section-card__badge--branching {
  background: #ddd6fe;
  color: #5b21b6;
}

.section-card__badge--registration {
  background: #dcfce7;
  color: #166534;
}

.section-card__actions {
  flex-shrink: 0;
  display: flex;
  gap: 4px;
  align-items: flex-start;
}

.section-card__action-btn {
  padding: 8px;
  background: transparent;
  border: 1px solid #fed7aa;
  border-radius: 6px;
  cursor: pointer;
  color: #c2410c;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-card__action-btn:hover {
  background: #ffedd5;
  border-color: #fdba74;
  color: #c2410c;
}

.section-card__action-btn--danger {
  border-color: #fed7aa;
}

.section-card__action-btn--danger:hover {
  background: #ffedd5;
  border-color: #fdba74;
  color: #c2410c;
}

.section-card__action-btn:active {
  transform: scale(0.95);
}
</style>
