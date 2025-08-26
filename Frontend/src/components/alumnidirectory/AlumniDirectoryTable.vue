<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import AlumniModalSimple from './AlumniModalSimple.vue';
import AlumniDirectoryRow from './AlumniDirectoryRow.vue';
import AlumniFileImport from '../AlumniFileImport.vue';
import axios from 'axios';

const authStore = useAuthStore();
const BASE_URL = 'http://127.0.0.1:8000';

// State
const alumni = ref([]);
const loading = ref(false);
const showModal = ref(false);
const showImportModal = ref(false);
const selectedAlumni = ref(null);
const searchQuery = ref('');
const sortBy = ref('last_name');
const sortOrder = ref('asc');
const selectedProgram = ref('');
const selectedYear = ref('');

// Pagination variables
const currentPage = ref(1);
const itemsPerPage = 9;

// Programs list for filter
const programs = [
  'BA in Sociology',
  'Bachelor of Agricultural Technology',
  'Bachelor of Elementary Education',
  'Bachelor of Secondary Education Major in English',
  'Bachelor of Secondary Education Major in Filipino',
  'Bachelor of Secondary Education Major in Mathematics',
  'Bachelor of Secondary Education Major in Science',
  'BS in Agroforestry',
  'BS in Agricultural and Biosystems Engineering',
  'BS in Agriculture',
  'BS in Agriculture, Major in Agribusiness Management',
  'BS in Agriculture, Major in Agricultural Economics',
  'BS in Agriculture, Major in Agronomy',
  'BS in Agriculture, Major in Animal Science',
  'BS in Agriculture, Major in Crop Protection',
  'BS in Agriculture, Major in Horticulture',
  'BS in Agriculture, Major in Soil Science',
  'BS in Applied Mathematics',
  'BS in Biology',
  'BS in Chemistry',
  'BS in Civil Engineering',
  'BS in Computer Science',
  'BS in Electronics Engineering',
  'BS in Environmental Science',
  'BS in Forestry',
  'BS in Geodetic Engineering',
  'BS in Geology',
  'BS in Information Systems',
  'BS in Information Technology',
  'BS in Mathematics',
  'BS in Mining Engineering',
  'BS in Physics',
  'BS in Psychology',
  'BS in Social Work'
];

// Computed
const currentYear = computed(() => new Date().getFullYear());

const uniqueYears = computed(() => {
  const years = [...new Set(alumni.value.map(person => person.year_graduated))];
  return years.filter(year => year != null).sort((a, b) => b - a);
});

const filteredAlumni = computed(() => {
  let filtered = alumni.value;
  
  // Text search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(person => 
      person.first_name?.toLowerCase().includes(query) ||
      person.last_name?.toLowerCase().includes(query) ||
      person.middle_name?.toLowerCase().includes(query) ||
      person.school_id?.toLowerCase().includes(query) ||
      person.program?.toLowerCase().includes(query)
    );
  }
  
  // Program filter
  if (selectedProgram.value) {
    filtered = filtered.filter(person => person.program === selectedProgram.value);
  }
  
  // Year graduated filter
  if (selectedYear.value) {
    const yearToFilter = parseInt(selectedYear.value);
    console.log('🎯 Filtering by year:', yearToFilter, 'Available years:', alumni.value.map(p => p.year_graduated));
    filtered = filtered.filter(person => person.year_graduated === yearToFilter);
    console.log('🎯 Filtered results:', filtered.length, 'matches');
  }
  
  // Sort filtered results
  filtered.sort((a, b) => {
    const aValue = a[sortBy.value] || '';
    const bValue = b[sortBy.value] || '';
    
    if (sortOrder.value === 'asc') {
      return aValue.localeCompare(bValue);
    } else {
      return bValue.localeCompare(aValue);
    }
  });
  
  return filtered;
});

// Pagination computed properties
const totalPages = computed(() => {
  return Math.ceil(filteredAlumni.value.length / itemsPerPage);
});

const paginatedAlumni = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage;
  const end = start + itemsPerPage;
  return filteredAlumni.value.slice(start, end);
});

const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage + 1;
  const end = Math.min(currentPage.value * itemsPerPage, filteredAlumni.value.length);
  return {
    start,
    end,
    total: filteredAlumni.value.length
  };
});

// Methods
const fetchAlumni = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`${BASE_URL}/api/alumni-directory/`, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    });
    alumni.value = response.data;
    console.log('✅ Alumni directory loaded:', alumni.value.length, 'entries');
  } catch (error) {
    console.error('❌ Failed to fetch alumni directory:', error);
    showNotification('Failed to load alumni directory. Please try again.', 'error');
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  selectedAlumni.value = null;
  showModal.value = true;
};

const openImportModal = () => {
  showImportModal.value = true;
};

const closeImportModal = () => {
  showImportModal.value = false;
};

const openEditModal = (alumniData) => {
  selectedAlumni.value = { ...alumniData };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  selectedAlumni.value = null;
};

const handleAlumniSaved = () => {
  fetchAlumni();
  closeModal();
  showNotification('Alumni directory entry saved successfully!', 'success');
};

const handleAlumniDeleted = () => {
  fetchAlumni();
  showNotification('Alumni directory entry deleted successfully!', 'success');
};

const sortTable = (column) => {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortBy.value = column;
    sortOrder.value = 'asc';
  }
};

const clearFilters = () => {
  searchQuery.value = '';
  selectedProgram.value = '';
  selectedYear.value = '';
  currentPage.value = 1; // Reset to first page when filters are cleared
};

// Pagination methods
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const previousPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--;
  }
};

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++;
  }
};

// Watch for filter changes to reset pagination
watch([searchQuery, selectedProgram, selectedYear], () => {
  currentPage.value = 1;
});

const showNotification = (message, type = 'info') => {
  // This would integrate with your existing notification system
  console.log(`${type.toUpperCase()}: ${message}`);
};

// Lifecycle
onMounted(() => {
  fetchAlumni();
});
</script>

<template>
  <div>
    <div class="bg-white rounded-lg shadow-lg overflow-hidden relative">
      <!-- Header -->
      <div class="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-2xl font-bold text-white">Alumni Directory</h2>
            <p class="text-green-100 mt-1">Manage alumni records and information</p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="openImportModal"
              class="bg-white  text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-300 transition-colors duration-200 flex items-center space-x-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span>Import Alumni</span>
            </button>
            <button
              @click="openCreateModal"
              class="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-300 transition-colors duration-200 flex items-center space-x-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Create Alumni</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Search and Stats -->
      <div class="p-6 border-b border-gray-200">
        <!-- Search Bar -->
        <div class="flex justify-between items-center mb-4">
          <div class="relative flex-1 max-w-md">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search alumni by name, school ID, or program..."
              class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div class="ml-6 text-sm text-gray-600">
            <span class="font-semibold">{{ filteredAlumni.length }}</span> 
            of 
            <span class="font-semibold">{{ alumni.length }}</span> 
            alumni displayed
          </div>
        </div>

        <!-- Filters -->
        <div class="flex flex-wrap gap-4 items-center">
          <!-- Program Filter -->
          <div class="flex-1 min-w-0 max-w-xs">
            <label class="block text-sm font-medium text-gray-700 mb-1">Filter by Program</label>
            <select
              v-model="selectedProgram"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            >
              <option value="">All Programs</option>
              <option v-for="program in programs" :key="program" :value="program">{{ program }}</option>
            </select>
          </div>

          <!-- Year Filter -->
          <div class="flex-1 min-w-0 max-w-xs">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Filter by Year Graduated
            </label>
            <input
              v-model="selectedYear"
              type="number"
              :min="currentYear - 50"
              :max="currentYear + 5"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              placeholder="Enter year (YYYY)"
            />
          </div>

          <!-- Clear Filters Button -->
          <div class="flex-shrink-0">
            <label class="block text-sm font-medium text-gray-700 mb-1 opacity-0">Clear</label>
            <button
              @click="clearFilters"
              v-if="searchQuery || selectedProgram || selectedYear"
              class="px-4 py-2 text-gray-600 bg-gray-100 border border-gray-300 rounded-lg hover:bg-gray-200 transition-colors duration-200 text-sm flex items-center space-x-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>Clear Filters</span>
            </button>
          </div>
        </div>

        <!-- Active Filters Display -->
        <div v-if="searchQuery || selectedProgram || selectedYear" class="mt-3 flex flex-wrap gap-2">
          <span class="text-sm text-gray-600">Active filters:</span>
          <span v-if="searchQuery" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            Search: "{{ searchQuery }}"
            <button @click="searchQuery = ''" class="ml-1 hover:text-blue-600">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
          <span v-if="selectedProgram" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
            Program: {{ selectedProgram }}
            <button @click="selectedProgram = ''" class="ml-1 hover:text-green-600">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
          <span v-if="selectedYear" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            Year: {{ selectedYear }}
            <button @click="selectedYear = ''" class="ml-1 hover:text-purple-600">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50">
            <tr>
              <th 
                @click="sortTable('school_id')"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div class="flex items-center space-x-1">
                  <span>School ID</span>
                  <svg v-if="sortBy === 'school_id'" class="w-4 h-4" :class="{ 'transform rotate-180': sortOrder === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                </div>
              </th>
              <th 
                @click="sortTable('last_name')"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div class="flex items-center space-x-1">
                  <span>Full Name</span>
                  <svg v-if="sortBy === 'last_name'" class="w-4 h-4" :class="{ 'transform rotate-180': sortOrder === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                </div>
              </th>
              <th 
                @click="sortTable('program')"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div class="flex items-center space-x-1">
                  <span>Program</span>
                  <svg v-if="sortBy === 'program'" class="w-4 h-4" :class="{ 'transform rotate-180': sortOrder === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                </div>
              </th>
              <th 
                @click="sortTable('year_graduated')"
                class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
              >
                <div class="flex items-center space-x-1">
                  <span>Year Graduated</span>
                  <svg v-if="sortBy === 'year_graduated'" class="w-4 h-4" :class="{ 'transform rotate-180': sortOrder === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Birth Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Gender
              </th>
              <th class="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <AlumniDirectoryRow
              v-for="person in paginatedAlumni"
              :key="person.id"
              :alumni="person"
              @edit="openEditModal"
              @delete="handleAlumniDeleted"
            />
            <tr v-if="paginatedAlumni.length === 0 && filteredAlumni.length === 0">
              <td colspan="7" class="px-6 py-12 text-center">
                <div class="flex flex-col items-center">
                  <svg class="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2 2v-5m16 0h-2M4 13h2m0 0V9a2 2 0 012-2h2m0 0V6a2 2 0 012-2h2.586a1 1 0 01.707.293l2.414 2.414A1 1 0 0016 7.414V9a2 2 0 012 2v2m0 0v2a2 2 0 01-2 2h-2m0 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v10.586a1 1 0 001.707.707l2.414-2.414A1 1 0 0012.586 17H15a2 2 0 002-2v-2z" />
                  </svg>
                  <h3 class="text-lg font-medium text-gray-900 mb-2">No Alumni Found</h3>
                  <p class="text-gray-500">
                    {{ searchQuery ? 'Try adjusting your search terms.' : 'Get started by creating your first alumni directory entry.' }}
                  </p>
                  <button
                    v-if="!searchQuery"
                    @click="openCreateModal"
                    class="mt-4 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors duration-200"
                  >
                    Create Alumni Entry
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="filteredAlumni.length > 0" class="bg-white px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <!-- Results info -->
          <div class="text-sm text-gray-700">
            Showing {{ paginationInfo.start }} to {{ paginationInfo.end }} of {{ paginationInfo.total }} results
          </div>
          
          <!-- Pagination controls -->
          <div class="flex items-center space-x-2">
            <!-- Previous button -->
            <button
              @click="previousPage"
              :disabled="currentPage === 1"
              :class="[
                'px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                currentPage === 1 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                  : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
              ]"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>

            <!-- Page numbers -->
            <div class="flex items-center space-x-1">
              <template v-for="page in Math.min(totalPages, 7)">
                <!-- Show first page, current page area, and last page with ellipsis -->
                <button
                  v-if="page === 1 || page === totalPages || (page >= currentPage - 1 && page <= currentPage + 1)"
                  :key="`page-${page}`"
                  @click="goToPage(page)"
                  :class="[
                    'px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                    currentPage === page
                      ? 'bg-green-600 text-white shadow-sm'
                      : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
                  ]"
                >
                  {{ page }}
                </button>
                <!-- Ellipsis -->
                <span
                  v-else-if="(page === 2 && currentPage > 4) || (page === totalPages - 1 && currentPage < totalPages - 3)"
                  :key="`ellipsis-${page}`"
                  class="px-2 py-2 text-gray-500"
                >
                  ...
                </span>
              </template>
            </div>

            <!-- Next button -->
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              :class="[
                'px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                currentPage === totalPages 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                  : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
              ]"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Loading overlay -->
      <div v-if="loading" class="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="text-gray-600">Loading alumni directory...</span>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <AlumniModalSimple
      :show="showModal"
      :alumni="selectedAlumni"
      @close="closeModal"
      @saved="handleAlumniSaved"
    />

    <!-- Import Modal -->
    <div v-if="showImportModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center p-6 border-b border-gray-200">
          <h3 class="text-xl font-semibold text-gray-800">Import Alumni Data</h3>
          <button
            @click="closeImportModal"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6">
          <AlumniFileImport @import-completed="fetchAlumni(); closeImportModal();" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Custom scrollbar for table */
.overflow-x-auto::-webkit-scrollbar {
  height: 6px;
}

.overflow-x-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.overflow-x-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Smooth transitions */
.transition-colors {
  transition: background-color 0.2s ease, color 0.2s ease;
}

/* Table hover effects */
tbody tr:hover {
  background-color: #f8fafc;
}

/* Sort icons */
.transform {
  transition: transform 0.2s ease;
}
</style>
