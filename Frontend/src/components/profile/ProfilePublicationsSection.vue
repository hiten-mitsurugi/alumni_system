<template>
  <div :class="[
    'rounded-lg shadow-lg p-6 transition-colors duration-200',
    themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
  ]">
    <SectionPrivacyControl 
      title="Related Publications"
      :is-own-profile="isOwnProfile"
      :section-visibility="sectionVisibility"
      @add="$emit('add')"
      @visibility-changed="handleVisibilityChange"
    />

    <div v-if="publications && publications.length > 0" class="space-y-4">
      <div 
        v-for="publication in publications" 
        :key="publication.id"
        class="group border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0 w-3 h-3 bg-emerald-600 rounded-full"></div>
              <h3 :class="[
                'text-lg font-semibold',
                themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
              ]">{{ publication.title }}</h3>
            </div>
            
            <div class="ml-6 mt-2 space-y-2">
              <!-- Authors -->
              <div v-if="publication.authors" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Authors:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ publication.authors }}</span>
              </div>
              
              <!-- Publication Type -->
              <div v-if="publication.publication_type" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Type:</span>
                <span :class="[
                  'px-2 py-1 rounded-full text-xs',
                  getPublicationTypeClass(publication.publication_type)
                ]">{{ formatPublicationType(publication.publication_type) }}</span>
              </div>
              
              <!-- Date Published -->
              <div v-if="publication.date_published" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Published:</span>
                <span :class="[
                  'px-2 py-1 rounded bg-emerald-100 text-emerald-800 text-xs font-semibold'
                ]">{{ formatDate(publication.date_published) }}</span>
              </div>
              
              <!-- Publisher -->
              <div v-if="publication.publisher" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">Publisher:</span>
                <span :class="[
                  themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
                ]">{{ publication.publisher }}</span>
              </div>
              
              <!-- URL -->
              <div v-if="publication.url" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">URL:</span>
                <a 
                  :href="publication.url"
                  target="_blank"
                  class="text-blue-600 hover:text-blue-800 underline text-xs break-all"
                >{{ publication.url }}</a>
              </div>
              
              <!-- DOI -->
              <div v-if="publication.doi" class="flex items-center text-sm">
                <span :class="[
                  'font-medium mr-2',
                  themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
                ]">DOI:</span>
                <a 
                  :href="'https://doi.org/' + publication.doi"
                  target="_blank"
                  class="text-blue-600 hover:text-blue-800 underline font-mono text-xs"
                >{{ publication.doi }}</a>
              </div>
            </div>
          </div>
          
          <!-- Edit/Delete buttons for own profile -->
          <div v-if="isOwnProfile" class="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              @click="$emit('edit', publication)"
              class="p-2 text-gray-400 hover:text-blue-600 transition-colors"
              title="Edit publication"
            >
              <PencilIcon class="w-4 h-4" />
            </button>
            <button 
              @click="$emit('delete', publication.id)"
              class="p-2 text-gray-400 hover:text-red-600 transition-colors"
              title="Delete publication"
            >
              <TrashIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-8">
      <div class="mx-auto w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mb-4">
        <svg class="w-8 h-8 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <p :class="[
        'text-lg font-medium',
        themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-900'
      ]">No publications</p>
      <p :class="[
        'text-sm mt-2',
        themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-600'
      ]">{{ isOwnProfile ? 'Add your related publications to showcase your research and academic contributions' : 'This user hasn\'t added any publications yet' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import SectionPrivacyControl from '@/components/profile/SectionPrivacyControl.vue'

defineProps({
  publications: {
    type: Array,
    default: () => []
  },
  isOwnProfile: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add', 'edit', 'delete', 'visibility-changed'])

const themeStore = useThemeStore()
const sectionVisibility = ref('connections_only')

const handleVisibilityChange = (visibility) => {
  sectionVisibility.value = visibility
  emit('visibility-changed', { section: 'publications', visibility })
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

const getPublicationTypeClass = (type) => {
  const classes = {
    'journal': 'bg-emerald-100 text-emerald-800',
    'conference': 'bg-blue-100 text-blue-800',
    'book': 'bg-purple-100 text-purple-800',
    'chapter': 'bg-indigo-100 text-indigo-800',
    'thesis': 'bg-red-100 text-red-800',
    'report': 'bg-yellow-100 text-yellow-800'
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const formatPublicationType = (type) => {
  const types = {
    'journal': 'Journal Article',
    'conference': 'Conference Paper',
    'book': 'Book',
    'chapter': 'Book Chapter',
    'thesis': 'Thesis/Dissertation',
    'report': 'Research Report'
  }
  return types[type] || type
}
</script>