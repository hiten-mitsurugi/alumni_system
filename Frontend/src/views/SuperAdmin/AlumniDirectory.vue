<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { onMounted, computed } from 'vue';
import AlumniDirectoryTable from '@/components/alumnidirectory/AlumniDirectoryTable.vue';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();
const adminDark = computed(() => themeStore.isAdminDark());

// You can add any page-level logic here if needed
onMounted(() => {
  console.log('🎓 Alumni Directory page loaded');
});
</script>

<template>
  <div :class="[
    'min-h-screen p-6',
    adminDark 
      ? 'bg-gradient-to-br from-gray-900 to-green-900' 
      : 'bg-gray-50'
  ]">
    <div class="max-w-7xl mx-auto">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
         
          <div :class="[
            'text-sm',
            adminDark ? 'text-gray-300' : 'text-gray-500'
          ]">
            <time :datetime="new Date().toISOString()">
              {{ new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              }) }}
            </time>
          </div>
        </div>
      </div>

      <!-- Alumni Directory Table Component -->
      <AlumniDirectoryTable />
    </div>
  </div>
</template>

<style scoped>
/* Page-specific styles */
.min-h-screen {
  min-height: calc(100vh - 64px); /* Account for any header/nav height */
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .max-w-7xl {
    max-width: 100%;
    padding: 0 1rem;
  }
  
  .text-3xl {
    font-size: 1.875rem;
  }
  
  .flex.items-center.justify-between {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
