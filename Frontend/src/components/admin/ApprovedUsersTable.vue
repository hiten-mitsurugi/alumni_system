<template>
  <div>
    <div :class="['rounded-xl shadow-lg', themeStore.isAdminDark() ? 'bg-gray-800' : 'bg-white']">
      <!-- Enhanced Header with Search, Filters, and Actions -->
      <div :class="['p-6 border-b', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
        <div class="flex items-center gap-4">
          <!-- Search Bar -->
          <div class="flex-1 max-w-md">
            <div class="relative">
              <input v-model="internalFilters.search" type="text"
                placeholder="Search by firstname, last name or fullname..."
                :class="['w-full pl-10 pr-4 py-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-orange-500 focus:border-orange-500 transition-all duration-200', 
                  themeStore.isAdminDark() 
                    ? 'border-gray-600 bg-gray-700 text-white placeholder-gray-400' 
                    : 'border-white bg-white text-gray-900 placeholder-gray-500']"
                @keyup.enter="applyFilters" @input="applyFilters" />
              <SearchIcon :class="['absolute left-3 top-3.5 h-5 w-5', themeStore.isAdminDark() ? 'text-gray-400' : 'text-gray-400']" />
            </div>
          </div>

          <!-- Right Side: Filter and Actions -->
          <div class="flex items-center gap-3 ml-auto">
            <!-- Filter Button -->
            <div class="relative">
              <button @click="toggleFilterDropdown"
                :class="['flex items-center gap-2 px-4 py-3 rounded-lg shadow-sm transition-all duration-200 border cursor-pointer', 
                  themeStore.isAdminDark() 
                    ? 'bg-gray-700 hover:bg-orange-500 hover:text-orange-300 hover:border-orange-600 text-gray-300 border-gray-600' 
                    : 'bg-white hover:bg-orange-200 hover:text-orange-600 hover:border-orange-300 text-gray-700 border-gray-300']">
                <FilterIcon class="w-5 h-5" />
                <span>Filters</span>
                <ChevronDownIcon
                  :class="['w-4 h-4 transition-transform duration-200', showFilterDropdown ? 'rotate-180' : '']" />
              </button>

              <!-- Filter Dropdown -->
              <transition enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-150 ease-in" leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0">
                <div v-if="showFilterDropdown"
                  :class="['absolute right-0 top-full mt-2 w-80 rounded-lg shadow-xl border z-50', 
                    themeStore.isAdminDark() 
                      ? 'bg-gray-800 border-gray-700' 
                      : 'bg-white border-gray-200']"
                  @click.stop>
                  <div class="p-4 space-y-4">
                    <h3 :class="['text-sm font-semibold border-b pb-2', 
                      themeStore.isAdminDark() 
                        ? 'text-gray-300 border-gray-700' 
                        : 'text-gray-700 border-gray-200']">Filter Options</h3>

                    <!-- Employment Filter -->
                    <div>
                      <label :class="['text-sm font-medium mb-1 block', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700']">Employment Status</label>
                      <select v-model="internalFilters.employment_status" @change="applyFilters"
                        :class="['w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500', 
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white' 
                            : 'border-gray-300 bg-white text-gray-900']">
                        <option value="">All</option>
                        <option value="employed_locally">Employed Locally</option>
                        <option value="employed_internationally">Employed Internationally</option>
                        <option value="self_employed">Self-Employed</option>
                        <option value="unemployed">Unemployed</option>
                      </select>
                    </div>

                    <!-- Sex Filter -->
                    <div>
                      <label :class="['text-sm font-medium mb-1 block', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700']">Sex</label>
                      <select v-model="internalFilters.sex" @change="applyFilters"
                        :class="['w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500', 
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white' 
                            : 'border-gray-300 bg-white text-gray-900']">
                        <option value="">All</option>
                        <option value="male">Male</option>
                        <option value="female">Female</option>
                      </select>
                    </div>

                    <!-- Year Graduated Filter (number input) -->
                    <div>
                      <label :class="['text-sm font-medium mb-1 block', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700']">Year Graduated</label>
                      <input
                        v-model="internalFilters.year_graduated"
                        @input="applyFilters"
                        type="number"
                        min="1900"
                        max="2099"
                        step="1"
                        placeholder="e.g. 2022"
                        :class="['w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500', 
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white placeholder-gray-400' 
                            : 'border-gray-300 bg-white text-gray-900 placeholder-gray-500']"
                      />
                    </div>

                    <!-- Program Filter -->
                    <div>
                      <label :class="['text-sm font-medium mb-1 block', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700']">Program</label>
                      <select v-model="internalFilters.program" @change="applyFilters"
                        :class="['w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500', 
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white' 
                            : 'border-gray-300 bg-white text-gray-900']">
                        <option value="">All</option>
                        <option v-for="program in programs" :key="program" :value="program">{{ program }}</option>
                      </select>
                    </div>

                    <!-- Status Filter -->
                    <div>
                      <label :class="['text-sm font-medium mb-1 block', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-700']">Account Status</label>
                      <select v-model="internalFilters.status" @change="applyFilters"
                        :class="['w-full text-sm rounded-md py-2 px-3 focus:ring-orange-500 focus:border-orange-500', 
                          themeStore.isAdminDark() 
                            ? 'border-gray-600 bg-gray-700 text-white' 
                            : 'border-gray-300 bg-white text-gray-900']">
                        <option value="">All</option>
                        <option value="active">Active</option>
                        <option value="blocked">Blocked</option>
                      </select>
                    </div>

                    <!-- Clear Filters Button -->
                    <div :class="['pt-2 border-t', themeStore.isAdminDark() ? 'border-gray-700' : 'border-gray-200']">
                      <button @click="clearFilters"
                        :class="['w-full py-2 px-3 text-sm rounded-md transition-colors duration-200', 
                          themeStore.isAdminDark() 
                            ? 'text-gray-300 hover:text-gray-100 hover:bg-gray-700' 
                            : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50']">
                        Clear All Filters
                      </button>
                    </div>
                  </div>
                </div>
              </transition>
            </div>

            <!-- Actions Button -->
            <div class="relative">
              <button @click="toggleActionsDropdown" :disabled="selectedUsers.length === 0" :class="[
                'flex items-center gap-2 px-4 py-3 rounded-lg shadow-sm transition-all duration-200 border',
                selectedUsers.length > 0
                  ? 'bg-white hover:bg-orange-200 text-orange-600 border-orange-300 cursor-pointer'
                  : 'bg-gray-100 text-gray-400 border-gray-300 cursor-not-allowed'
              ]">
                <MoreVerticalIcon class="w-5 h-5" />
                <span>Actions</span>
                <span v-if="selectedUsers.length > 0" class="bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {{ selectedUsers.length }}
                </span>
              </button>

              <!-- Actions Dropdown -->
              <transition enter-active-class="transition duration-200 ease-out"
                enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100"
                leave-active-class="transition duration-150 ease-in" leave-from-class="transform scale-100 opacity-100"
                leave-to-class="transform scale-95 opacity-0">
                <div v-if="showActionsDropdown && selectedUsers.length > 0"
                  class="absolute right-0 top-full mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 z-50"
                  @click.stop>
                  <div class="py-2">
                    <button @click="bulkBlockUsers"
                      class="w-full px-4 py-2 text-left text-sm text-yellow-600 hover:bg-yellow-50 flex items-center gap-2">
                      <BanIcon class="w-4 h-4" />
                      Block Selected ({{ selectedUsers.length }})
                    </button>
                    <button @click="bulkUnblockUsers"
                      class="w-full px-4 py-2 text-left text-sm text-orange-500 hover:bg-orange-50 flex items-center gap-2">
                      <UnlockIcon class="w-4 h-4" />
                      Unblock Selected ({{ selectedUsers.length }})
                    </button>
                    <hr class="my-1">
                    <button @click="bulkDeleteUsers"
                      class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2">
                      <TrashIcon class="w-4 h-4" />
                      Delete Selected ({{ selectedUsers.length }})
                    </button>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table v-if="users.length" class="min-w-full">
          <thead :class="['text-white text-sm uppercase', themeStore.isAdminDark() ? 'bg-gray-700' : 'bg-orange-600']">
            <tr>
              <!-- Select All Checkbox -->
              <th class="p-4 w-12 text-left">
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll"
                  class="w-4 h-4 accent-orange-600 border-gray-300 rounded focus:ring-orange-500" />

              </th>
              <th class="p-4 w-20 text-center">Profile</th>
              <th class="p-4 w-32 text-left">First Name</th>
              <th class="p-4 w-32 text-left">Last Name</th>
              <th class="p-4 w-20 text-center">Sex</th>
              <th class="p-4 w-40 text-left">Program</th>
              <th class="p-4 w-24 text-center">Year</th>
              <th class="p-4 w-32 text-left">Employment</th>
              <th class="p-4 w-32 text-center">Online Status</th>
              <th class="p-4 w-24 text-center">Status</th>
              <th class="p-4 w-32 text-left">Last Login</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" @click="viewUserDetails(user)"
              :class="['border-t cursor-pointer transition-colors duration-200', themeStore.isAdminDark() ? 'hover:bg-gray-700' : 'hover:bg-orange-50']">
              <!-- Row Checkbox -->
              <td class="p-4 w-12 text-left" @click.stop>
                <input type="checkbox" :checked="selectedUsers.includes(user.id)" @change="toggleUserSelection(user.id)"
                  class="w-4 h-4 accent-orange-600 border-gray-300 rounded focus:ring-orange-500" />
              </td>
              <td class="p-4 w-20">
                <div class="flex items-center justify-center">
                  <img 
                    :src="user.profile_picture || '/default-avatar.png'" 
                    :alt="`${user.first_name} ${user.last_name}`"
                    class="w-10 h-10 rounded-full object-cover border"
                    @error="$event.target.src = '/default-avatar.png'"
                  />
                </div>
              </td>
              <td :class="['p-4 w-32 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.first_name }}</td>
              <td :class="['p-4 w-32 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.last_name }}</td>
              <td :class="['p-4 w-20 text-center', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.sex || 'N/A' }}</td>
              <td :class="['p-4 w-40 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.program }}</td>
              <td :class="['p-4 w-24 text-center', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ user.year_graduated }}</td>
              <td :class="['p-4 w-32 text-left', themeStore.isAdminDark() ? 'text-white' : 'text-gray-900']">{{ formatEmployment(user.employment_status) }}</td>
              <td class="p-4 w-32">
                <div class="flex items-center justify-center space-x-2">
                  <div
                    :class="['w-2 h-2 rounded-full', getOnlineStatusClass(userStatuses.get(user.id) || user.real_time_status)]">
                  </div>
                  <span :class="getOnlineStatusTextClass(userStatuses.get(user.id) || user.real_time_status)">
                    {{ getOnlineStatusText(userStatuses.get(user.id) || user.real_time_status) }}
                  </span>
                </div>
              </td>
              <td class="p-4 w-24">
                <div class="flex justify-center">
                  <span :class="user.is_active ? 'text-green-600 font-semibold' : 'text-red-500 font-semibold'">
                    {{ user.is_active ? 'Active' : 'Blocked' }}
                  </span>
                </div>
              </td>
              <td :class="['p-4 w-32 text-left text-sm', themeStore.isAdminDark() ? 'text-gray-300' : 'text-gray-900']">
                {{ formatLastLogin(user.last_login, userStatuses.get(user.id) || user.real_time_status) }}
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="text-center py-10 text-gray-400">
          No approved users found or user does not exist.
        </div>
      </div>
    </div>

    <!-- Click Outside Handler -->
    <div v-if="showFilterDropdown || showActionsDropdown" @click="closeDropdowns" class="fixed inset-0 z-40"></div>
  </div>
</template>

<script setup>
import {
  SearchIcon,
  FilterIcon,
  ChevronDownIcon,
  MoreVerticalIcon,
  BanIcon,
  UnlockIcon,
  TrashIcon
} from 'lucide-vue-next';
import { onMounted, onUnmounted, ref, computed, watch } from 'vue';
import { websocketService } from '@/services/websocket';
import {
  formatLastLogin,
  getOnlineStatusClass,
  getOnlineStatusTextClass,
  getOnlineStatusText
} from '@/utils/timeFormat';
import api from '@/services/api';
import { useThemeStore } from '@/stores/theme';

const themeStore = useThemeStore();

const props = defineProps({
  users: Array,
  search: String,
  // optional: the full list of approved users so filters can be populated from entire dataset
  allUsers: {
    type: Array,
    default: null
  }
});

const emit = defineEmits([
  'view-user',
  'block-user',
  'unblock-user',
  'delete-user',
  'apply-filters',
  'bulk-block-users',
  'bulk-unblock-users',
  'bulk-delete-users'
]);

// User details view function
const viewUserDetails = (user) => {
  emit('view-user', user);
};

// User status management
const userStatuses = ref(new Map());

// Filter and dropdown management
const showFilterDropdown = ref(false);
const showActionsDropdown = ref(false);
const selectedUsers = ref([]);

// Internal filters to manage the state locally
const internalFilters = ref({
  search: '',
  employment_status: '',
  year_graduated: '',
  program: '',
  status: '',
});
const programs = computed(() => {
  // Use `allUsers` when provided (full dataset), otherwise fall back to current users prop
  const source = Array.isArray(props.allUsers) ? props.allUsers : (props.users || []);
  const allPrograms = source.map(u => u.program).filter(Boolean);
  return Array.from(new Set(allPrograms)).sort();
});

// Data for filter dropdowns
// (programs is now a computed property, see above)
const years = ref([]);

// Computed properties
const isAllSelected = computed(() =>
  props.users.length > 0 && selectedUsers.value.length === props.users.length
);

// Watch for external search prop changes
watch(() => props.search, (newSearch) => {
  internalFilters.value.search = newSearch || '';
});

// Filter functions
const applyFilters = () => {
  emit('apply-filters', {
    ...internalFilters.value,
    gender: internalFilters.value.gender?.toLowerCase() || ''
  });
};

const clearFilters = () => {
  internalFilters.value = {
    search: '',
    employment_status: '',
    year_graduated: '',
    program: '',
    status: '',
    gender: ''
  };
  applyFilters();
  showFilterDropdown.value = false;
};

// Dropdown toggle functions
const toggleFilterDropdown = () => {
  showFilterDropdown.value = !showFilterDropdown.value;
  showActionsDropdown.value = false;
};

const toggleActionsDropdown = () => {
  if (selectedUsers.value.length > 0) {
    showActionsDropdown.value = !showActionsDropdown.value;
    showFilterDropdown.value = false;
  }
};

const closeDropdowns = () => {
  showFilterDropdown.value = false;
  showActionsDropdown.value = false;
};

// User selection functions
const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedUsers.value = [];
  } else {
    selectedUsers.value = props.users.map(user => user.id);
  }
};

const toggleUserSelection = (userId) => {
  const index = selectedUsers.value.indexOf(userId);
  if (index > -1) {
    selectedUsers.value.splice(index, 1);
  } else {
    selectedUsers.value.push(userId);
  }
};

// Bulk action functions
const bulkBlockUsers = async () => {
  if (selectedUsers.value.length === 0) return;

  if (confirm(`Are you sure you want to block ${selectedUsers.value.length} selected users?`)) {
    try {
      const selectedUserObjects = props.users.filter(user => selectedUsers.value.includes(user.id));

      for (const user of selectedUserObjects) {
        if (user.is_active) {
          emit('block-user', user);
        }
      }

      selectedUsers.value = [];
      showActionsDropdown.value = false;
    } catch (error) {
      console.error('Failed to block users:', error);
      alert('Failed to block some users. Please try again.');
    }
  }
};

const bulkUnblockUsers = async () => {
  if (selectedUsers.value.length === 0) return;

  if (confirm(`Are you sure you want to unblock ${selectedUsers.value.length} selected users?`)) {
    try {
      const selectedUserObjects = props.users.filter(user => selectedUsers.value.includes(user.id));

      for (const user of selectedUserObjects) {
        if (!user.is_active) {
          emit('unblock-user', user);
        }
      }

      selectedUsers.value = [];
      showActionsDropdown.value = false;
    } catch (error) {
      console.error('Failed to unblock users:', error);
      alert('Failed to unblock some users. Please try again.');
    }
  }
};

const bulkDeleteUsers = async () => {
  if (selectedUsers.value.length === 0) return;

  if (confirm(`Are you sure you want to delete ${selectedUsers.value.length} selected users? This action cannot be undone.`)) {
    try {
      const selectedUserObjects = props.users.filter(user => selectedUsers.value.includes(user.id));

      for (const user of selectedUserObjects) {
        emit('delete-user', user);
      }

      selectedUsers.value = [];
      showActionsDropdown.value = false;
    } catch (error) {
      console.error('Failed to delete users:', error);
      alert('Failed to delete some users. Please try again.');
    }
  }
};


// WebSocket listener for real-time status updates
const handleStatusUpdate = (data) => {
  if (data.type === 'status_update' && data.data) {
    const { user_id, status, timestamp } = data.data;
    userStatuses.value.set(user_id, {
      status,
      last_seen: timestamp,
      is_online: status === 'online'
    });
  }
};

// Utility function
function formatEmployment(status) {
  if (!status) return 'N/A';
  return status
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase());
}

// Lifecycle hooks
onMounted(() => {
  // Listen for status updates via WebSocket
  websocketService.addListener(handleStatusUpdate);

  // Filter programs are computed from the passed users/allUsers props

  // Initialize search from props
  if (props.search) {
    internalFilters.value.search = props.search;
  }
});

onUnmounted(() => {
  websocketService.removeListener(handleStatusUpdate);
});

// Watch for users prop changes to reset selection
watch(() => props.users, () => {
  selectedUsers.value = [];
});
</script>
