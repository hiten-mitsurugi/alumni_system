<!-- eslint-disable vue/multi-word-component-names -->
<script setup>
import { onMounted } from 'vue';
import AlumniDirectoryTable from '@/components/alumnidirectory/AlumniDirectoryTable.vue';

// You can add any page-level logic here if needed
onMounted(() => {
  console.log('🎓 Alumni Directory page loaded');
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Page Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-3xl font-bold text-gray-900">Alumni Directory Management</h1>
            <p class="text-gray-600 mt-2">Manage and maintain the alumni directory database</p>
          </div>
          <div class="text-sm text-gray-500">
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
