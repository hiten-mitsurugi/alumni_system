<template>
  <div class="sections-grid">
    <!-- Header -->
    <div class="sections-grid__header">
      <h2 class="sections-grid__title">Sections</h2>
      <button class="sections-grid__add-btn" @click="handleAddSection">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
          <path d="M8 2v12M2 8h12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        Add Section
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="!sections || sections.length === 0" class="sections-grid__empty">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="8" y="12" width="48" height="40" rx="4"/>
        <line x1="16" y1="24" x2="48" y2="24"/>
        <line x1="16" y1="32" x2="40" y2="32"/>
        <line x1="16" y1="40" x2="44" y2="40"/>
      </svg>
      <p class="sections-grid__empty-text">No sections yet</p>
      <button class="sections-grid__empty-btn" @click="handleAddSection">
        Create your first section
      </button>
    </div>

    <!-- Grid -->
    <div
      v-else
      class="sections-grid__container"
      @dragover.prevent="handleDragOver"
      @drop="handleDrop"
    >
      <SectionCard
        v-for="section in sortedSections"
        :key="section.category.id"
        :section="section"
        @section-click="handleSectionClick"
        @add-question="handleAddQuestion"
        @edit="handleEditSection"
        @delete="handleDeleteSection"
        @drag-start="handleDragStart"
        @drag-end="handleDragEnd"
      />
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue';
import SectionCard from './SectionCard.vue';

const props = defineProps({
  sections: {
    type: Array,
    required: true,
    // Array of { category: {...}, questions: [...] }
  },
});

const emit = defineEmits([
  'add-section',
  'section-click',
  'add-question',
  'edit-section',
  'delete-section',
  'reorder-sections',
]);

const draggedSection = ref(null);
const dragOverIndex = ref(null);

const sortedSections = computed(() => {
  if (!props.sections) return [];
  return [...props.sections].sort((a, b) => a.category.order - b.category.order);
});

function handleAddSection() {
  emit('add-section');
}

function handleSectionClick(section) {
  emit('section-click', section);
}

function handleAddQuestion(categoryId) {
  emit('add-question', categoryId);
}

function handleEditSection(section) {
  emit('edit-section', section);
}

function handleDeleteSection(categoryId) {
  emit('delete-section', categoryId);
}

function handleDragStart(section) {
  draggedSection.value = section;
}

function handleDragEnd() {
  draggedSection.value = null;
  dragOverIndex.value = null;
}

function handleDragOver(event) {
  if (!draggedSection.value) return;
  
  const grid = event.currentTarget;
  const cards = Array.from(grid.querySelectorAll('.section-card'));
  
  let closestCard = null;
  let closestOffset = Number.NEGATIVE_INFINITY;
  
  cards.forEach(card => {
    const box = card.getBoundingClientRect();
    const offset = event.clientY - box.top - box.height / 2;
    
    if (offset < 0 && offset > closestOffset) {
      closestOffset = offset;
      closestCard = card;
    }
  });
  
  if (closestCard) {
    const index = cards.indexOf(closestCard);
    dragOverIndex.value = index;
  }
}

function handleDrop(event) {
  event.preventDefault();
  
  if (!draggedSection.value) return;
  
  const draggedId = draggedSection.value.category.id;
  const sections = sortedSections.value;
  const draggedIndex = sections.findIndex(s => s.category.id === draggedId);
  
  if (draggedIndex === -1) return;
  
  // Calculate new order based on drop position
  const grid = event.currentTarget;
  const cards = Array.from(grid.querySelectorAll('.section-card'));
  
  let targetIndex = cards.length - 1;
  
  cards.forEach((card, index) => {
    const box = card.getBoundingClientRect();
    if (event.clientY < box.top + box.height / 2) {
      targetIndex = Math.min(targetIndex, index);
    }
  });
  
  if (draggedIndex === targetIndex) {
    handleDragEnd();
    return;
  }
  
  // Build new ordered category IDs
  const reordered = [...sections];
  const [removed] = reordered.splice(draggedIndex, 1);
  reordered.splice(targetIndex, 0, removed);
  
  const newCategoryIds = reordered.map(s => s.category.id);
  
  emit('reorder-sections', newCategoryIds);
  handleDragEnd();
}
</script>

<style scoped>
.sections-grid {
  width: 100%;
}

.sections-grid__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.sections-grid__title {
  font-size: 20px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.sections-grid__add-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #dd6b20;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;
}

.sections-grid__add-btn:hover {
  background: #F57C00;
}

.sections-grid__add-btn:active {
  transform: scale(0.98);
}

.sections-grid__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
  color: #6b7280;
}

.sections-grid__empty svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.sections-grid__empty-text {
  font-size: 16px;
  margin: 0 0 16px 0;
}

.sections-grid__empty-btn {
  padding: 10px 20px;
  background: #dd6b20;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s ease;
}

.sections-grid__empty-btn:hover {
  background: #c05621;
}

.sections-grid__container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  min-height: 200px;
}

@media (max-width: 768px) {
  .sections-grid__container {
    grid-template-columns: 1fr;
  }
}

@media (min-width: 769px) and (max-width: 1200px) {
  .sections-grid__container {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}
</style>
