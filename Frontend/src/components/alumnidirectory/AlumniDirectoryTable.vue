<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useThemeStore } from '@/stores/theme';
import { SearchIcon, FilterIcon, ChevronDownIcon, MoreVerticalIcon, TrashIcon, EyeIcon, EditIcon } from 'lucide-vue-next';
import AlumniModalSimple from './AlumniModalSimple.vue';
import AlumniFileImport from '../AlumniFileImport.vue';
import axios from 'axios';

const authStore = useAuthStore();
const themeStore = useThemeStore();
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
const selectedSex = ref('');

// Dropdown and selection state
const showFilterDropdown = ref(false);
const showActionsDropdown = ref(false);
const selectedAlumniIds = ref([]);

// Pagination variables
const currentPage = ref(1);
const itemsPerPage = 9;

// Programs list for filter
const programs = [
  'BS in Computer Science',
  'BS in Information Systems',
  'BS in Information Technology',
];

// Computed
const currentYear = computed(() => new Date().getFullYear());

const uniqueYears = computed(() => {
  const years = [...new Set(alumni.value.map(person => person.year_graduated))];
  return years.filter(year => year != null).sort((a, b) => b - a);
});

const isAllSelected = computed(() => 
  filteredAlumni.value.length > 0 && selectedAlumniIds.value.length === filteredAlumni.value.length
);

const filteredAlumni = computed(() => {
  let filtered = alumni.value;
  
  // Text search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(person => 
      person.first_name?.toLowerCase().includes(query) ||
      person.last_name?.toLowerCase().includes(query) ||
      person.middle_name?.toLowerCase().includes(query) ||
      `${person.first_name} ${person.last_name}`.toLowerCase().includes(query) ||
      `${person.first_name} ${person.middle_name} ${person.last_name}`.toLowerCase().includes(query)
    );
  }
  
  // Program filter
  if (selectedProgram.value) {
    filtered = filtered.filter(person => person.program === selectedProgram.value);
  }
  
  // Year graduated filter
  if (selectedYear.value) {
    const yearToFilter = parseInt(selectedYear.value);
    filtered = filtered.filter(person => person.year_graduated === yearToFilter);
  }

  // Sex filter
  if (selectedSex.value) {
    filtered = filtered.filter(person => person.sex === selectedSex.value);
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
    const response = await axios.get(`${BASE_URL}/api/auth/alumni-directory/`, {
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
  selectedSex.value = '';
  currentPage.value = 1; // Reset to first page when filters are cleared
};

// Dropdown management methods
const toggleFilterDropdown = () => {
  showFilterDropdown.value = !showFilterDropdown.value;
  showActionsDropdown.value = false;
};

const toggleActionsDropdown = () => {
  if (selectedAlumniIds.value.length > 0) {
    showActionsDropdown.value = !showActionsDropdown.value;
    showFilterDropdown.value = false;
  }
};

const closeDropdowns = () => {
  showFilterDropdown.value = false;
  showActionsDropdown.value = false;
};

// Selection management
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedAlumniIds.value = [];
  } else {
    selectedAlumniIds.value = filteredAlumni.value.map(person => person.id);
  }
};

const toggleAlumniSelection = (alumniId) => {
  const index = selectedAlumniIds.value.indexOf(alumniId);
  if (index > -1) {
    selectedAlumniIds.value.splice(index, 1);
  } else {
    selectedAlumniIds.value.push(alumniId);
  }
};

// Bulk actions
const bulkDeleteAlumni = async () => {
  if (selectedAlumniIds.value.length === 0) return;
  
  if (confirm(`Are you sure you want to delete ${selectedAlumniIds.value.length} selected alumni? This action cannot be undone.`)) {
    try {
      for (const alumniId of selectedAlumniIds.value) {
        await axios.delete(`${BASE_URL}/api/auth/alumni-directory/${alumniId}/`, {
          headers: { Authorization: `Bearer ${authStore.token}` }
        });
      }
      selectedAlumniIds.value = [];
      showActionsDropdown.value = false;
      fetchAlumni();
      showNotification(`${selectedAlumniIds.value.length} alumni deleted successfully!`, 'success');
    } catch (error) {
      console.error('❌ Failed to delete alumni:', error);
      showNotification('Failed to delete some alumni. Please try again.', 'error');
    }
  }
};

const bulkEditAlumni = () => {
  if (selectedAlumniIds.value.length === 1) {
    const alumniToEdit = alumni.value.find(person => person.id === selectedAlumniIds.value[0]);
    if (alumniToEdit) {
      openEditModal(alumniToEdit);
      selectedAlumniIds.value = [];
      showActionsDropdown.value = false;
    }
  } else {
    showNotification('Please select only one alumni to edit.', 'info');
  }
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
watch([searchQuery, selectedProgram, selectedYear, selectedSex], () => {
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
  <div class="alumni-directory-container">
    <div :class="[
      'rounded-lg shadow-lg overflow-hidden relative',
      themeStore.isAdminDark() ? 'bg-gray-800' : 'bg-white'
    ]">
      <!-- Header -->
      <div class="bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-4">
        <div class="flex justify-between items-center">
          <div>
            <h2 class="text-2xl font-bold text-white">Alumni Directory</h2>
            <p class="text-orange-100 mt-1">Manage alumni records and information</p>
          </div>
          <div class="flex space-x-3">
            <button
              @click="openImportModal"
              class="bg-white  text-orange-600 px-6 py-3 rounded-lg font-semibold hover:bg-orange-200 transition-colors duration-200 flex items-center space-x-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span>Import Alumni</span>
            </button>
            <button
              @click="openCreateModal"
              class="bg-white text-orange-600 px-6 py-3 rounded-lg font-semibold hover:bg-orange-200 transition-colors duration-200 flex items-center space-x-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
              </svg>
              <span>Create Alumni</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Search and Controls -->
      <div :class="[
        'p-6 border-b',
        themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200'
      ]">
        <div class="flex items-center gap-4">
          <!-- Search Bar -->
          <div class="flex-1 max-w-md">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by firstname, lastname or fullname..."
                :class="[
                  'w-full pl-10 pr-4 py-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all duration-200',
                  themeStore.isAdminDark() 
                    ? 'border-gray-600 bg-gray-700 text-white placeholder-gray-400' 
                    : 'border-gray-300 bg-white text-gray-900 placeholder-gray-500'
                ]"
              />
              <SearchIcon :class="[
                'absolute left-3 top-3.5 h-5 w-5',
                themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-400'
              ]" />
            </div>
          </div>

          <!-- Right Side: Filter and Actions -->
          <div class="flex items-center gap-3 ml-auto relative">
            <!-- Filter Button -->
            <div class="relative">
              <button
                @click="toggleFilterDropdown"
                :class="[
                  'flex items-center gap-2 px-4 py-3 rounded-lg shadow-sm transition-all duration-200 border cursor-pointer',
                  themeStore.isAdminDark() 
                    ? 'bg-gray-700 hover:bg-orange-600 hover:text-orange-300 hover:border-orange-600 text-gray-300 border-gray-600' 
                    : 'bg-white hover:bg-orange-200 hover:text-orange-600 hover:border-orange-300 text-gray-700 border-gray-300'
                ]"
              >
                <FilterIcon class="w-5 h-5" />
                <span>Filters</span>
                <ChevronDownIcon
                  :class="['w-4 h-4 transition-transform duration-200', showFilterDropdown ? 'rotate-180' : '']"
                />
              </button>

              <!-- Filter Dropdown -->
              <transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-150 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0"
              >
                <div
                  v-if="showFilterDropdown"
                  :class="[
                    'absolute right-0 top-full mt-2 w-80 rounded-lg shadow-xl border z-50 filter-dropdown-scrollable',
                    themeStore.isAdminDark() 
                      ? 'bg-gray-800 border-gray-700' 
                      : 'bg-white border-gray-200'
                  ]"
                  @click.stop
                >
                  <div class="p-4 space-y-4">
                    <h3 :class="[
                      'text-sm font-semibold border-b pb-2',
                      themeStore.isAdminDark() 
                        ? 'text-gray-300 border-gray-700' 
                        : 'text-gray-700 border-gray-200'
                    ]">Filter Options</h3>

                    <!-- Program Filter -->
                    <div>
                      <label :class="[
                        'text-sm font-medium mb-1 block',
                        themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'
                      ]">Program</label>
                      <select
                        v-model="selectedProgram"
                        :class="[
                          'w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500 transition-colors duration-200',
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white hover:bg-gray-600' 
                            : 'border-gray-300 bg-white text-gray-900 hover:bg-orange-200'
                        ]"
                      >
                        <option value="">All Programs</option>
                        <option v-for="program in programs" :key="program" :value="program">{{ program }}</option>
                      </select>
                    </div>

                    <!-- Year Graduated Filter -->
                    <div>
                      <label :class="[
                        'text-sm font-medium mb-1 block',
                        themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'
                      ]">Year Graduated</label>
                      <input
                        v-model="selectedYear"
                        type="number"
                        :min="currentYear - 50"
                        :max="currentYear + 5"
                        placeholder="Enter year (YYYY)"
                        :class="[
                          'w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500 transition-colors duration-200',
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white placeholder-gray-400 hover:bg-gray-600' 
                            : 'border-gray-300 bg-white text-gray-900 placeholder-gray-500 hover:bg-orange-200'
                        ]"
                      />
                    </div>

                    <!-- Sex Filter -->
                    <div>
                      <label :class="[
                        'text-sm font-medium mb-1 block',
                        themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'
                      ]">Sex</label>
                      <select
                        v-model="selectedSex"
                        :class="[
                          'w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500 transition-colors duration-200',
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white hover:bg-gray-600' 
                            : 'border-gray-300 bg-white text-gray-900 hover:bg-orange-200'
                        ]"
                      >
                        <option value="">All</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                        <option value="prefer_not_to_say">Prefer not to say</option>
                      </select>
                    </div>

                    <!-- Clear Filters Button -->
                    <div :class="[
                      'pt-2 border-t',
                      themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200'
                    ]">
                      <button
                        @click="clearFilters"
                        :class="[
                          'w-full py-2 px-3 text-sm rounded-md transition-colors duration-200 font-medium',
                          themeStore.isAdminDark() 
                            ? 'bg-orange-600 text-gray-100 hover:bg-orange-500' 
                            : 'bg-orange-600 text-gray-100 hover:bg-orange-200 hover:text-orange-600'
                        ]"
                      >
                        Clear All Filters
                      </button>
                    </div>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Actions Button -->
            <div class="relative">
              <button
                @click="toggleActionsDropdown"
                :disabled="selectedAlumniIds.length === 0"
                :class="[
                  'flex items-center gap-2 px-4 py-3 rounded-lg shadow-sm transition-all duration-200 border',
                  selectedAlumniIds.length > 0
                    ? themeStore.isAdminDark() 
                      ? 'bg-gray-700 hover:bg-orange-600 hover:text-orange-300 hover:border-orange-600 text-gray-300 border-gray-600 cursor-pointer'
                      : 'bg-white hover:bg-orange-200 text-orange-600 border-orange-300 cursor-pointer'
                    : themeStore.isAdminDark()
                      ? 'bg-gray-800 text-gray-500 border-gray-600 cursor-not-allowed'
                      : 'bg-gray-100 text-gray-400 border-gray-300 cursor-not-allowed'
                ]"
              >
                <MoreVerticalIcon class="w-5 h-5" />
                <span>Actions</span>
                <span
                  v-if="selectedAlumniIds.length > 0"
                  class="bg-orange-600 text-white text-xs px-2 py-0.5 rounded-full"
                >
                  {{ selectedAlumniIds.length }}
                </span>
              </button>

              <!-- Actions Dropdown -->
              <transition
                enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0"
                enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-150 ease-in"
                leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0"
              >
                <div
                  v-if="showActionsDropdown && selectedAlumniIds.length > 0"
                  :class="[
                    'absolute right-0 top-full mt-2 w-48 rounded-lg shadow-xl border z-50',
                    themeStore.isAdminDark() 
                      ? 'bg-gray-800 border-gray-700' 
                      : 'bg-white border-gray-200'
                  ]"
                  @click.stop
                >
                  <div class="py-2">
                    <button
                      @click="bulkEditAlumni"
                      :class="[
                        'w-full px-4 py-2 text-left text-sm flex items-center gap-2',
                        themeStore.isAdminDark() 
                          ? 'text-orange-400 hover:bg-orange-900/20' 
                          : 'text-orange-600 hover:bg-orange-200'
                      ]"
                    >
                      <EditIcon class="w-4 h-4" />
                      Edit Selected ({{ selectedAlumniIds.length }})
                    </button>
                    <hr :class="themeStore.isAdminDark() ? 'border-gray-700 my-1' : 'border-gray-200 my-1'">
                    <button
                      @click="bulkDeleteAlumni"
                      :class="[
                        'w-full px-4 py-2 text-left text-sm flex items-center gap-2',
                        themeStore.isAdminDark() 
                          ? 'text-red-400 hover:bg-red-900/20' 
                          : 'text-red-600 hover:bg-red-200'
                      ]"
                    >
                      <TrashIcon class="w-4 h-4" />
                      Delete Selected ({{ selectedAlumniIds.length }})
                    </button>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>

        <!-- Results info -->
        <div :class="[
          'mt-4 text-sm',
          themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600'
        ]">
          <span class="font-semibold">{{ filteredAlumni.length }}</span> 
          of 
          <span class="font-semibold">{{ alumni.length }}</span> 
          alumni displayed
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table :class="[
          'w-full',
          themeStore.isAdminDark() ? 'bg-gray-800' : 'bg-white'
        ]">
          <thead class="bg-gradient-to-r from-orange-500 to-orange-600">
            <tr>
              <!-- Select All Checkbox -->
              <th class="px-6 py-3 w-12">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  @change="toggleSelectAll"
                  class="w-4 h-4 accent-orange-600 border-gray-300 rounded focus:ring-orange-500"
                />
              </th>
              <th 
                @click="sortTable('last_name')"
                class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer"
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
                class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer"
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
                class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider cursor-pointer"
              >
                <div class="flex items-center space-x-1">
                  <span>Year Graduated</span>
                  <svg v-if="sortBy === 'year_graduated'" class="w-4 h-4" :class="{ 'transform rotate-180': sortOrder === 'desc' }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                </div>
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                Birth Date
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                Sex
              </th>
            </tr>
          </thead>
          <tbody :class="[
            'divide-y',
            themeStore.isAdminDark() 
              ? 'bg-gray-800 divide-gray-700' 
              : 'bg-white divide-gray-200'
          ]">
            <tr
              v-for="person in paginatedAlumni"
              :key="person.id"
              :class="[
                'transition-colors duration-150',
                themeStore.isAdminDark() 
                  ? 'hover:bg-gray-700' 
                  : 'hover:bg-gray-50'
              ]"
            >
              <!-- Row Checkbox -->
              <td class="px-6 py-4" @click.stop>
                <input
                  type="checkbox"
                  :checked="selectedAlumniIds.includes(person.id)"
                  @change="toggleAlumniSelection(person.id)"
                  class="w-4 h-4 accent-orange-600 border-gray-300 rounded focus:ring-orange-500"
                />
              </td>

              <!-- Full Name -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div :class="[
                  'text-sm font-medium',
                  themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'
                ]">
                  {{ `${person.first_name} ${person.middle_name || ''} ${person.last_name}`.replace(/\s+/g, ' ').trim() }}
                </div>
              </td>

              <!-- Program -->
              <td class="px-6 py-4">
                <div :class="[
                  'text-sm max-w-xs',
                  themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-900'
                ]">
                  <span class="line-clamp-2">{{ person.program }}</span>
                </div>
              </td>

              <!-- Year Graduated -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div :class="[
                  'text-sm font-medium',
                  themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'
                ]">{{ person.year_graduated }}</div>
              </td>

              <!-- Birth Date -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div :class="[
                  'text-sm',
                  themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-900'
                ]">
                  {{ person.birth_date ? new Date(person.birth_date).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' }) : '-' }}
                </div>
              </td>

              <!-- Sex -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  class="inline-flex px-2 py-1 text-xs font-medium rounded-full"
                  :class="{
                    'bg-orange-100 text-orange-600': person.sex === 'male',
                    'bg-pink-100 text-pink-800': person.sex === 'female',
                    'bg-gray-100 text-gray-800': person.sex === 'prefer_not_to_say'
                  }"
                >
                  {{ person.sex === 'male' ? 'Male' : person.sex === 'female' ? 'Female' : person.sex === 'prefer_not_to_say' ? 'Prefer not to say' : person.sex }}
                </span>
              </td>
            </tr>

            <tr v-if="paginatedAlumni.length === 0 && filteredAlumni.length === 0">
              <td colspan="6" class="px-6 py-12 text-center">
                <div class="flex flex-col items-center">
                  <svg :class="[
                    'w-12 h-12 mb-4',
                    themeStore.isAdminDark() ? 'text-gray-500' : 'text-gray-400'
                  ]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2 2v-5m16 0h-2M4 13h2m0 0V9a2 2 0 012-2h2m0 0V6a2 2 0 012-2h2.586a1 1 0 01.707.293l2.414 2.414A1 1 0 0016 7.414V9a2 2 0 012 2v2m0 0v2a2 2 0 01-2 2h-2m0 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v10.586a1 1 0 001.707.707l2.414-2.414A1 1 0 0012.586 17H15a2 2 0 002-2v-2z" />
                  </svg>
                  <h3 :class="[
                    'text-lg font-medium mb-2',
                    themeStore.isAdminDark() ? 'text-white' : 'text-gray-900'
                  ]">No Alumni Found</h3>
                  <p :class="[
                    'mb-4',
                    themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500'
                  ]">
                    {{ searchQuery ? 'Try adjusting your search terms.' : 'Get started by creating your first alumni directory entry.' }}
                  </p>
                  <button
                    v-if="!searchQuery"
                    @click="openCreateModal"
                    class="mt-4 bg-orange-600 text-white px-6 py-2 rounded-lg hover:bg-orange-500 transition-colors duration-200"
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
      <div v-if="filteredAlumni.length > 0" :class="[
        'px-6 py-4 border-t',
        themeStore.isAdminDark() 
          ? 'bg-gray-800 border-gray-700' 
          : 'bg-white border-gray-200'
      ]">
        <div class="flex items-center justify-between">
          <!-- Results info -->
          <div :class="[
            'text-sm',
            themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700'
          ]">
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
                  ? themeStore.isAdminDark() 
                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : themeStore.isAdminDark() 
                    ? 'bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600'
                    : 'bg-orange-50 text-orange-600 hover:bg-orange-100 border border-orange-200'
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
                      : themeStore.isAdminDark() 
                        ? 'bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600'
                        : 'bg-green-50 text-green-700 hover:bg-green-100 border border-green-200'
                  ]"
                >
                  {{ page }}
                </button>
                <!-- Ellipsis -->
                <span
                  v-else-if="(page === 2 && currentPage > 4) || (page === totalPages - 1 && currentPage < totalPages - 3)"
                  :key="`ellipsis-${page}`"
                  :class="[
                    'px-2 py-2',
                    themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-500'
                  ]"
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
                  ? themeStore.isAdminDark() 
                    ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : themeStore.isAdminDark() 
                    ? 'bg-gray-700 text-gray-300 hover:bg-gray-600 border border-gray-600'
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
      <div v-if="loading" :class="[
        'absolute inset-0 flex items-center justify-center',
        themeStore.isAdminDark() 
          ? 'bg-gray-800 bg-opacity-75' 
          : 'bg-white bg-opacity-75'
      ]">
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
          <span :class="[
            themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-600'
          ]">Loading alumni directory...</span>
        </div>
      </div>
    </div>

    <!-- Click Outside Handler -->
    <div v-if="showFilterDropdown || showActionsDropdown" @click="closeDropdowns" class="fixed inset-0 z-40"></div>

    <!-- Modal -->
    <AlumniModalSimple
      :show="showModal"
      :alumni="selectedAlumni"
      @close="closeModal"
      @saved="handleAlumniSaved"
    />

    <!-- Import Modal -->
    <div v-if="showImportModal" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <AlumniFileImport 
        @import-completed="fetchAlumni(); closeImportModal();" 
        @close="closeImportModal"
      />
    </div>
  </div>
</template>

<style scoped>
/* Ensure filter dropdown is always visible and scrollable if too tall */
.filter-dropdown-scrollable {
  max-height: 60vh;
  overflow-y: auto;
}
/* Line clamp utility for long program names */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

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

.transition-all {
  transition: all 0.2s ease;
}

/* Alumni Directory Professional Styling */
.alumni-directory-container {
  font-family: 'Poppins', sans-serif;
}

/* Sort icons */
.transform {
  transition: transform 0.2s ease;
}

/* Dropdown animations */
.transition {
  transition-property: transform, opacity;
}

/* Button hover effects */
button:hover:not(:disabled) {
  transform: translateY(-1px);
}

button:disabled {
  cursor: not-allowed;
}

/* Checkbox styling */
input[type="checkbox"] {
  accent-color: #16a34a;
}

/* Focus states */
input:focus, select:focus {
  outline: none;
  box-shadow: 0 0 0 2px #16a34a;
  border-color: #16a34a;
}
</style>
