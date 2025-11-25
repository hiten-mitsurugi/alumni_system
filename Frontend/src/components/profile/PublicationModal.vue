<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
    <div :class="[
      'w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-lg shadow-lg',
      themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
    ]">
      <div :class="[
        'p-6 border-b',
        themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
      ]">
        <h2 :class="[
          'text-xl font-semibold',
          themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
        ]">
          {{ publication ? 'Edit Publication' : 'Add Publication' }}
        </h2>
      </div>

      <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
        <!-- Title -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Publication Title *
          </label>
          <input
            v-model="formData.title"
            type="text"
            required
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., Modern Web Development Practices: A Comprehensive Study"
          />
        </div>

        <!-- Year and Place of Publication -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Year Published *
            </label>
            <input
              v-model="formData.year_published"
              type="number"
              required
              min="1900"
              :max="new Date().getFullYear() + 1"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
              placeholder="2023"
            />
          </div>
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Place of Publication *
            </label>
            <input
              v-model="formData.place_of_publication"
              type="text"
              required
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
              placeholder="e.g., Journal of Computer Science"
            />
          </div>
        </div>

        <!-- Authors Type and Publication Type -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Authors Type
            </label>
            <select
              v-model="formData.authors_type"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
            >
              <option value="">Select author type</option>
              <option value="primary">Primary Author</option>
              <option value="co_author">Co-author</option>
              <option value="corresponding">Corresponding Author</option>
              <option value="contributor">Contributor</option>
            </select>
          </div>
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Publication Type
            </label>
            <select
              v-model="formData.publication_type"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
            >
              <option value="">Select type</option>
              <option value="journal">Journal Article</option>
              <option value="conference">Conference Paper</option>
              <option value="book">Book</option>
              <option value="chapter">Book Chapter</option>
              <option value="thesis">Thesis/Dissertation</option>
              <option value="report">Research Report</option>
            </select>
          </div>
        </div>

        <!-- Journal Details (conditional) -->
        <div v-if="formData.publication_type === 'journal'" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Journal Name
            </label>
            <input
              v-model="formData.journal_name"
              type="text"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
              placeholder="International Journal of Web Technologies"
            />
          </div>
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Volume
            </label>
            <input
              v-model="formData.volume"
              type="text"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
              placeholder="15"
            />
          </div>
          <div>
            <label :class="[
              'block text-sm font-medium mb-2',
              themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
            ]">
              Issue
            </label>
            <input
              v-model="formData.issue"
              type="text"
              :class="[
                'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
                themeStore.isDarkMode 
                  ? 'bg-gray-700 border-gray-600 text-white' 
                  : 'bg-white border-gray-300 text-gray-900'
              ]"
              placeholder="3"
            />
          </div>
        </div>

        <!-- Pages -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Pages
          </label>
          <input
            v-model.number="formData.pages"
            type="number"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., 45"
          />
        </div>

        <!-- Co-authors -->
        <div>
          <label :class="[
            'block text-sm font-medium mb-2',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-700'
          ]">
            Co-authors
            <span class="text-xs text-gray-500">(Enter names separated by commas)</span>
          </label>
          <input
            v-model="coAuthorsInput"
            type="text"
            :class="[
              'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500',
              themeStore.isDarkMode 
                ? 'bg-gray-700 border-gray-600 text-white' 
                : 'bg-white border-gray-300 text-gray-900'
            ]"
            placeholder="e.g., Dr. Jane Smith, Prof. John Doe"
          />
          <div v-if="formData.co_authors && formData.co_authors.length > 0" class="mt-2 flex flex-wrap gap-2">
            <span 
              v-for="(author, index) in formData.co_authors" 
              :key="index"
              class="px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full flex items-center"
            >
              {{ author }}
              <button 
                type="button"
                @click="removeCoAuthor(index)"
                class="ml-1 text-green-600 hover:text-green-800"
              >
                ×
              </button>
            </span>
          </div>
        </div>



        <!-- Form Actions -->
        <div :class="[
          'flex justify-end space-x-3 pt-4 border-t',
          themeStore.isDarkMode ? 'border-gray-700' : 'border-gray-200'
        ]">
          <button
            type="button"
            @click="$emit('close')"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              themeStore.isDarkMode
                ? 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
            ]"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="!isFormValid"
            :class="[
              'px-4 py-2 text-sm font-medium rounded-md transition-colors',
              isFormValid
                ? 'bg-orange-600 text-white hover:bg-orange-700'
                : 'bg-gray-400 text-gray-200 cursor-not-allowed'
            ]"
          >
            {{ publication ? 'Update' : 'Save' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, defineProps, defineEmits } from 'vue'
import { useThemeStore } from '@/stores/theme'

const props = defineProps({
  publication: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'save'])

const themeStore = useThemeStore()

// Form data
const formData = ref({
  title: '',
  year_published: '',
  place_of_publication: '',
  authors_type: '',
  publication_type: '',
  journal_name: '',
  volume: '',
  issue: '',
  pages: '',
  co_authors: []
})

const coAuthorsInput = ref('')

const isFormValid = computed(() => {
  return formData.value.title.trim() && 
         formData.value.year_published && 
         formData.value.place_of_publication.trim()
})

// Watch co-authors input for comma-separated values
watch(coAuthorsInput, (newValue) => {
  if (newValue.includes(',')) {
    const authors = newValue.split(',').map(author => author.trim()).filter(author => author)
    const lastAuthor = authors.pop() || ''
    
    // Add complete authors to the array
    authors.forEach(author => {
      if (!formData.value.co_authors.includes(author)) {
        formData.value.co_authors.push(author)
      }
    })
    
    // Keep the last (incomplete) author in the input
    coAuthorsInput.value = lastAuthor
  }
})

const removeCoAuthor = (index) => {
  formData.value.co_authors.splice(index, 1)
}

// Watch for changes in publication prop to populate form
watch(() => props.publication, (newPublication) => {
  if (newPublication) {
    formData.value = {
      title: newPublication.title || '',
      year_published: newPublication.year_published || '',
      place_of_publication: newPublication.place_of_publication || '',
      authors_type: newPublication.authors_type || '',
      publication_type: newPublication.publication_type || '',
      journal_name: newPublication.journal_name || '',
      volume: newPublication.volume || '',
      issue: newPublication.issue || '',
      pages: newPublication.pages || '',
      // doi removed
      co_authors: newPublication.co_authors || [],
      // abstract removed
      // visibility removed
    }
    coAuthorsInput.value = ''
  } else {
    // Reset form for new publication
    formData.value = {
      title: '',
      year_published: '',
      place_of_publication: '',
      authors_type: '',
      publication_type: '',
      journal_name: '',
      volume: '',
      issue: '',
      pages: '',
      // doi removed
      co_authors: [],
      // abstract removed
      // visibility removed
    }
    coAuthorsInput.value = ''
  }
}, { immediate: true })

const handleSubmit = () => {
  if (!isFormValid.value) {
    return
  }

  // Add any remaining co-author from input
  if (coAuthorsInput.value.trim() && !formData.value.co_authors.includes(coAuthorsInput.value.trim())) {
    formData.value.co_authors.push(coAuthorsInput.value.trim())
  }

  // Clean up form data
  const cleanedData = { ...formData.value }
  
  // Remove empty strings for optional fields
  Object.keys(cleanedData).forEach(key => {
    if (cleanedData[key] === '' && key !== 'co_authors') {
      cleanedData[key] = null
    }
  })

  emit('save', cleanedData)
}
</script>