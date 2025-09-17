<template>
  <div class="space-y-4">
    <!-- Address Type Selector -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-2">Address Type</label>
      <div class="flex space-x-4">
        <label class="flex items-center">
          <input 
            v-model="localForm.address_type" 
            type="radio" 
            value="philippines"
            class="text-green-600 focus:ring-green-500"
          />
          <span class="ml-2 text-sm text-gray-700">Philippines</span>
        </label>
        <label class="flex items-center">
          <input 
            v-model="localForm.address_type" 
            type="radio" 
            value="international"
            class="text-green-600 focus:ring-green-500"
          />
          <span class="ml-2 text-sm text-gray-700">International</span>
        </label>
      </div>
    </div>

    <!-- Philippines Address (PSGC) -->
    <div v-if="localForm.address_type === 'philippines'" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Region -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Region <span class="text-red-500">*</span></label>
          <select 
            v-model="localForm.region_code" 
            @change="fetchProvinces"
            class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            required
          >
            <option value="">Select Region</option>
            <option 
              v-for="region in regions" 
              :key="region.code" 
              :value="region.code"
            >
              {{ region.name }}
            </option>
          </select>
        </div>

        <!-- Province -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Province <span class="text-red-500">*</span></label>
          <select 
            v-model="localForm.province_code" 
            @change="fetchCities"
            class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            :disabled="!localForm.region_code"
            required
          >
            <option value="">Select Province</option>
            <option 
              v-for="province in provinces" 
              :key="province.code" 
              :value="province.code"
            >
              {{ province.name }}
            </option>
          </select>
        </div>

        <!-- City -->
        <div>
          <label class="block text-sm font-medium text-gray-700">City/Municipality <span class="text-red-500">*</span></label>
          <select 
            v-model="localForm.city_code" 
            @change="fetchBarangays"
            class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            :disabled="!localForm.province_code"
            required
          >
            <option value="">Select City/Municipality</option>
            <option 
              v-for="city in cities" 
              :key="city.code" 
              :value="city.code"
            >
              {{ city.name }}
            </option>
          </select>
        </div>

        <!-- Barangay -->
        <div>
          <label class="block text-sm font-medium text-gray-700">Barangay <span class="text-red-500">*</span></label>
          <select 
            v-model="localForm.barangay" 
            class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
            :disabled="!localForm.city_code"
            required
          >
            <option value="">Select Barangay</option>
            <option 
              v-for="barangay in barangays" 
              :key="barangay.name" 
              :value="barangay.name"
            >
              {{ barangay.name }}
            </option>
          </select>
        </div>
      </div>

      <!-- Street Address -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Street Address / House Number</label>
        <input 
          v-model="localForm.street_address" 
          type="text" 
          placeholder="e.g., 123 Sample Street, Subdivision Name"
          class="mt-1 w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>

      <!-- Postal Code -->
      <div class="md:w-1/3">
        <label class="block text-sm font-medium text-gray-700">Postal Code</label>
        <input 
          v-model="localForm.postal_code" 
          type="text" 
          placeholder="e.g., 1234"
          class="mt-1 w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
        />
      </div>
    </div>

    <!-- International Address -->
    <div v-else-if="localForm.address_type === 'international'" class="space-y-4">
      <!-- Country -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Country <span class="text-red-500">*</span></label>
        <select 
          v-model="localForm.country" 
          class="mt-1 block w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          required
        >
          <option value="">Select Country</option>
          <option 
            v-for="country in countries" 
            :key="country.code" 
            :value="country.name"
          >
            {{ country.name }}
          </option>
        </select>
      </div>

      <!-- Full Address -->
      <div>
        <label class="block text-sm font-medium text-gray-700">Full Address <span class="text-red-500">*</span></label>
        <textarea 
          v-model="localForm.full_address" 
          rows="3"
          placeholder="Enter complete address including street, city, state/province, postal code"
          class="mt-1 w-full border border-gray-300 rounded-md p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none"
          required
        ></textarea>
      </div>
    </div>

    <!-- Hidden fields for Philippines addresses (following Register.txt pattern) -->
    <input type="hidden" v-model="localForm.region_name" />
    <input type="hidden" v-model="localForm.province_name" />
    <input type="hidden" v-model="localForm.city_name" />
  </div>
</template>

<script setup>
import { defineProps, defineEmits, reactive, ref, watch, onMounted } from 'vue';

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  label: {
    type: String,
    default: 'Address'
  },
  required: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue']);

// Reactive data
const regions = ref([]);
const provinces = ref([]);
const cities = ref([]);
const barangays = ref([]);
const countries = ref([]);

// Initialize local form with default structure
const localForm = reactive({
  address_type: props.modelValue?.address_type || 'philippines',
  // Philippines fields
  region_code: props.modelValue?.region_code || '',
  region_name: props.modelValue?.region_name || '',
  province_code: props.modelValue?.province_code || '',
  province_name: props.modelValue?.province_name || '',
  city_code: props.modelValue?.city_code || '',
  city_name: props.modelValue?.city_name || '',
  barangay: props.modelValue?.barangay || '',
  street_address: props.modelValue?.street_address || '',
  postal_code: props.modelValue?.postal_code || '',
  // International fields
  country: props.modelValue?.country || '',
  full_address: props.modelValue?.full_address || ''
});

// Common countries list
const commonCountries = [
  { code: 'US', name: 'United States' },
  { code: 'CA', name: 'Canada' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'AU', name: 'Australia' },
  { code: 'SG', name: 'Singapore' },
  { code: 'JP', name: 'Japan' },
  { code: 'KR', name: 'South Korea' },
  { code: 'CN', name: 'China' },
  { code: 'DE', name: 'Germany' },
  { code: 'FR', name: 'France' },
  { code: 'IT', name: 'Italy' },
  { code: 'ES', name: 'Spain' },
  { code: 'NL', name: 'Netherlands' },
  { code: 'SE', name: 'Sweden' },
  { code: 'NO', name: 'Norway' },
  { code: 'DK', name: 'Denmark' },
  { code: 'FI', name: 'Finland' },
  { code: 'CH', name: 'Switzerland' },
  { code: 'AT', name: 'Austria' },
  { code: 'BE', name: 'Belgium' },
  { code: 'IE', name: 'Ireland' },
  { code: 'NZ', name: 'New Zealand' },
  { code: 'MY', name: 'Malaysia' },
  { code: 'TH', name: 'Thailand' },
  { code: 'VN', name: 'Vietnam' },
  { code: 'ID', name: 'Indonesia' },
  { code: 'IN', name: 'India' },
  { code: 'PK', name: 'Pakistan' },
  { code: 'BD', name: 'Bangladesh' },
  { code: 'LK', name: 'Sri Lanka' },
  { code: 'AE', name: 'United Arab Emirates' },
  { code: 'SA', name: 'Saudi Arabia' },
  { code: 'QA', name: 'Qatar' },
  { code: 'KW', name: 'Kuwait' },
  { code: 'BH', name: 'Bahrain' },
  { code: 'OM', name: 'Oman' },
  { code: 'IL', name: 'Israel' },
  { code: 'TR', name: 'Turkey' },
  { code: 'EG', name: 'Egypt' },
  { code: 'ZA', name: 'South Africa' },
  { code: 'NG', name: 'Nigeria' },
  { code: 'GH', name: 'Ghana' },
  { code: 'KE', name: 'Kenya' },
  { code: 'BR', name: 'Brazil' },
  { code: 'AR', name: 'Argentina' },
  { code: 'CL', name: 'Chile' },
  { code: 'MX', name: 'Mexico' },
  { code: 'CO', name: 'Colombia' },
  { code: 'PE', name: 'Peru' },
  { code: 'VE', name: 'Venezuela' },
  { code: 'EC', name: 'Ecuador' },
  { code: 'UY', name: 'Uruguay' },
  { code: 'PY', name: 'Paraguay' },
  { code: 'BO', name: 'Bolivia' },
  { code: 'RU', name: 'Russia' },
  { code: 'UA', name: 'Ukraine' },
  { code: 'PL', name: 'Poland' },
  { code: 'CZ', name: 'Czech Republic' },
  { code: 'HU', name: 'Hungary' },
  { code: 'SK', name: 'Slovakia' },
  { code: 'SI', name: 'Slovenia' },
  { code: 'HR', name: 'Croatia' },
  { code: 'RS', name: 'Serbia' },
  { code: 'BG', name: 'Bulgaria' },
  { code: 'RO', name: 'Romania' },
  { code: 'LT', name: 'Lithuania' },
  { code: 'LV', name: 'Latvia' },
  { code: 'EE', name: 'Estonia' }
];

// PSGC API functions (following Register.txt pattern)
const fetchRegions = async () => {
  try {
    const response = await fetch('https://psgc.gitlab.io/api/regions/');
    const data = await response.json();
    regions.value = data.sort((a, b) => a.name.localeCompare(b.name));
  } catch (error) {
    console.error('Error fetching regions:', error);
  }
};

const fetchProvinces = async () => {
  if (!localForm.region_code) return;
  
  // Store region name in hidden field (Register.txt pattern)
  const selectedRegion = regions.value.find(r => r.code === localForm.region_code);
  if (selectedRegion) {
    localForm.region_name = selectedRegion.name;
  }
  
  // Clear dependent fields
  localForm.province_code = '';
  localForm.province_name = '';
  localForm.city_code = '';
  localForm.city_name = '';
  localForm.barangay = '';
  provinces.value = [];
  cities.value = [];
  barangays.value = [];
  
  try {
    const response = await fetch(`https://psgc.gitlab.io/api/regions/${localForm.region_code}/provinces/`);
    const data = await response.json();
    provinces.value = data.sort((a, b) => a.name.localeCompare(b.name));
  } catch (error) {
    console.error('Error fetching provinces:', error);
  }
};

const fetchCities = async () => {
  if (!localForm.province_code) return;
  
  // Store province name in hidden field (Register.txt pattern)
  const selectedProvince = provinces.value.find(p => p.code === localForm.province_code);
  if (selectedProvince) {
    localForm.province_name = selectedProvince.name;
  }
  
  // Clear dependent fields
  localForm.city_code = '';
  localForm.city_name = '';
  localForm.barangay = '';
  cities.value = [];
  barangays.value = [];
  
  try {
    const response = await fetch(`https://psgc.gitlab.io/api/provinces/${localForm.province_code}/cities-municipalities/`);
    const data = await response.json();
    cities.value = data.sort((a, b) => a.name.localeCompare(b.name));
  } catch (error) {
    console.error('Error fetching cities:', error);
  }
};

const fetchBarangays = async () => {
  if (!localForm.city_code) return;
  
  // Store city name in hidden field (Register.txt pattern)
  const selectedCity = cities.value.find(c => c.code === localForm.city_code);
  if (selectedCity) {
    localForm.city_name = selectedCity.name;
  }
  
  // Clear dependent fields
  localForm.barangay = '';
  barangays.value = [];
  
  try {
    const response = await fetch(`https://psgc.gitlab.io/api/cities-municipalities/${localForm.city_code}/barangays/`);
    const data = await response.json();
    barangays.value = data.sort((a, b) => a.name.localeCompare(b.name));
  } catch (error) {
    console.error('Error fetching barangays:', error);
  }
};

// Watch for changes and emit updates
watch(
  localForm,
  (newVal) => {
    emit('update:modelValue', { ...newVal });
  },
  { deep: true }
);

// Watch for address type changes to clear fields
watch(() => localForm.address_type, (newType) => {
  if (newType === 'philippines') {
    // Clear international fields
    localForm.country = '';
    localForm.full_address = '';
  } else {
    // Clear Philippines fields
    localForm.region_code = '';
    localForm.region_name = '';
    localForm.province_code = '';
    localForm.province_name = '';
    localForm.city_code = '';
    localForm.city_name = '';
    localForm.barangay = '';
    localForm.street_address = '';
    localForm.postal_code = '';
  }
});

// Initialize data on mount
onMounted(() => {
  countries.value = commonCountries;
  fetchRegions();
  
  // If editing existing data, populate dropdowns
  if (localForm.region_code) {
    fetchProvinces();
  }
  if (localForm.province_code) {
    fetchCities();
  }
  if (localForm.city_code) {
    fetchBarangays();
  }
});
</script>