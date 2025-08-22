<template>
  <div class="bg-white p-6 rounded-xl shadow-lg mb-8 flex flex-wrap gap-4 items-end">
    <!-- Search -->
    <div class="flex-1 min-w-[250px]">
      <label class="text-sm font-semibold text-gray-700 mb-1 block">Search</label>
      <div class="flex">
        <input
          v-model="filters.search"
          type="text"
          placeholder="Name or School ID"
          class="w-full text-sm border-gray-300 rounded-l-md py-2 px-3 focus:ring-green-500 focus:border-green-500"
          @keyup.enter="applyFilters"
        />
        <button
          @click="applyFilters"
          class="bg-green-600 hover:bg-green-700 text-white px-4 rounded-r-md"
        >
          <SearchIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Employment -->
    <div class="min-w-[180px]">
      <label class="text-sm font-semibold text-gray-700 mb-1 block">Employment</label>
      <select
        v-model="filters.employment_status"
        @change="applyFilters"
        class="w-full text-sm border-gray-300 rounded-md py-2 px-3 focus:ring-green-500 focus:border-green-500"
      >
        <option value="">All</option>
        <option value="Employed Locally">Employed Locally</option>
        <option value="Employed Internationally">Employed Internationally</option>
        <option value="Self-Employed">Self-Employed</option>
        <option value="Unemployed">Unemployed</option>
      </select>
    </div>

    <!-- Gender -->
    <div class="min-w-[150px]">
      <label class="text-sm font-semibold text-gray-700 mb-1 block">Gender</label>
      <select
        v-model="filters.gender"
        @change="applyFilters"
        class="w-full text-sm border-gray-300 rounded-md py-2 px-3 focus:ring-green-500 focus:border-green-500"
      >
        <option value="">All</option>
        <option value="Male">Male</option>
        <option value="Female">Female</option>
        <option value="Prefer not to say">Prefer not to say</option>
      </select>
    </div>

    <!-- Year Graduated -->
    <div class="min-w-[150px]">
      <label class="text-sm font-semibold text-gray-700 mb-1 block">Year Graduated</label>
      <select
        v-model="filters.year_graduated"
        @change="applyFilters"
        class="w-full text-sm border-gray-300 rounded-md py-2 px-3 focus:ring-green-500 focus:border-green-500"
      >
        <option value="">All</option>
        <option v-for="year in years" :key="year" :value="year">{{ year }}</option>
      </select>
    </div>

    <!-- Program -->
    <div class="min-w-[150px]">
      <label class="text-sm font-semibold text-gray-700 mb-1 block">Program</label>
      <select
        v-model="filters.program"
        @change="applyFilters"
        class="w-full text-sm border-gray-300 rounded-md py-2 px-3 focus:ring-green-500 focus:border-green-500"
      >
        <option value="">All</option>
        <option v-for="program in programs" :key="program" :value="program">{{ program }}</option>
      </select>
    </div>

    <!-- Status -->
    <div class="min-w-[150px]">
      <label class="text-sm font-semibold text-gray-700 mb-1 block">Status</label>
      <select
        v-model="filters.status"
        @change="applyFilters"
        class="w-full text-sm border-gray-300 rounded-md py-2 px-3 focus:ring-green-500 focus:border-green-500"
      >
        <option value="">All</option>
        <option value="active">Active</option>
        <option value="blocked">Blocked</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { SearchIcon } from 'lucide-vue-next';
import api from '@/services/api';

const filters = ref({
  search: '',
  employment_status: '',
  year_graduated: '',
  program: '',
  status: '',
  gender: ''
});

const emit = defineEmits(['apply-filters']);
const programs = ref([]);
const years = ref([]);

const applyFilters = () => {
  emit('apply-filters', {
    ...filters.value,
    employment_status: filters.value.employment_status?.toLowerCase() || '',
    gender: filters.value.gender?.toLowerCase() || ''
  });
};

const fetchProgramsAndYears = async () => {
  try {
    const res = await api.get('/approved-users/');
    const users = res.data;
    programs.value = [...new Set(users.map(u => u.program))].filter(Boolean);
    years.value = [...new Set(users.map(u => u.year_graduated))].sort((a, b) => b - a);
  } catch (error) {
    console.error(error);
  }
};

onMounted(fetchProgramsAndYears);
</script>
