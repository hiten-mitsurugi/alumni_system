<template>
  <div 
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 bg-opacity-50"
    @click.self="$emit('close')"
  >
    <div 
      :class="[
        'w-full max-w-4xl max-h-[90vh] rounded-lg shadow-xl overflow-hidden flex flex-col',
        themeStore.isDarkMode ? 'bg-gray-800' : 'bg-white'
      ]"
    >
      <!-- Header -->
      <div :class="[
        'px-6 py-4 border-b flex items-center justify-between',
        themeStore.isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-orange-100 border-gray-200'
      ]">
        <div>
          <h2 :class="[
            'text-xl font-bold',
            themeStore.isDarkMode ? 'text-white' : 'text-gray-900'
          ]">
            Your Submitted Responses
          </h2>
          <p :class="[
            'text-sm mt-1',
            themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'
          ]">
            {{ formName }}
          </p>
        </div>
        <button
          @click="$emit('close')"
          :class="[
            'p-2 rounded-lg transition-colors',
            themeStore.isDarkMode 
              ? 'hover:bg-gray-600 text-gray-300' 
              : 'hover:bg-gray-200 text-gray-600'
          ]"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex-1 flex items-center justify-center py-12">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600 mx-auto mb-4"></div>
          <p :class="themeStore.isDarkMode ? 'text-gray-300' : 'text-gray-600'">
            Loading your responses...
          </p>
        </div>
      </div>

      <!-- Content -->
      <div v-else class="flex-1 overflow-y-auto p-6">
        <ResponsesContent
          :categories="categories"
          :responses="responses"
        />
      </div>

      <!-- Footer -->
      <div :class="[
        'px-6 py-4 border-t flex justify-end',
        themeStore.isDarkMode ? 'bg-gray-750 border-gray-700' : 'bg-gray-50 border-gray-200'
      ]">
        <button
          @click="$emit('close')"
          class="px-6 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useThemeStore } from '@/stores/theme'
import ResponsesContent from './ResponsesContent.vue'
import surveyService from '@/services/surveyService'

const props = defineProps({
  show: Boolean,
  formId: Number,
  formName: String,
  formCategories: Array // Add this to receive categories directly
})

const emit = defineEmits(['close'])

const themeStore = useThemeStore()
const loading = ref(false)
const categories = ref([])
const responses = ref({})

const loadResponses = async () => {
  if (!props.formId) {
    console.warn('⚠️ No form ID provided')
    return
  }
  
  loading.value = true
  try {
    console.log('🔍 Loading responses for form ID:', props.formId)
    console.log('📂 Form categories:', props.formCategories)
    
    // Fetch user's responses
    const responsesData = await surveyService.getMyResponses()
    console.log('📦 All user responses from API:', responsesData.data)
    
    // Get all question IDs from the categories for THIS form
    const formQuestionIds = new Set()
    if (props.formCategories && Array.isArray(props.formCategories)) {
      props.formCategories.forEach(category => {
        if (category.questions && Array.isArray(category.questions)) {
          category.questions.forEach(question => {
            formQuestionIds.add(question.id)
          })
        }
      })
    }
    console.log('🎯 Question IDs in this form:', Array.from(formQuestionIds))
    
    // Map responses by question ID
    const responseMap = {}
    if (responsesData.data && Array.isArray(responsesData.data)) {
      responsesData.data.forEach(resp => {
        // Get question ID - handle both object and direct ID
        const questionId = typeof resp.question === 'object' ? resp.question.id : resp.question
        
        console.log('🔎 Processing response:', {
          questionId: questionId,
          form: resp.form,
          targetForm: props.formId,
          isInThisForm: formQuestionIds.has(questionId),
          responseData: resp.response_data
        })
        
        // Use question ID matching instead of form ID matching for better compatibility
        if (questionId && formQuestionIds.has(questionId)) {
          console.log('✅ Mapping response for question:', questionId)
          
          // Handle different response_data structures
          let responseValue = resp.response_data
          
          // If response_data is an object with a 'value' property, use it
          if (resp.response_data && typeof resp.response_data === 'object' && 'value' in resp.response_data) {
            responseValue = resp.response_data.value
          }
          // If response_data is a string that looks like JSON, try to parse it
          else if (typeof resp.response_data === 'string') {
            try {
              const parsed = JSON.parse(resp.response_data)
              responseValue = parsed.value !== undefined ? parsed.value : parsed
            } catch (e) {
              // Not JSON, use as is
              responseValue = resp.response_data
            }
          }
          
          responseMap[questionId] = responseValue
          console.log('💾 Stored response:', questionId, '=', responseValue)
        }
      })
    }
    
    console.log('📋 Final response map:', responseMap)
    console.log('📊 Total responses mapped:', Object.keys(responseMap).length)
    responses.value = responseMap
    
    // Use categories passed from parent (they contain the questions)
    if (props.formCategories && props.formCategories.length > 0) {
      categories.value = props.formCategories
      console.log('✅ Categories loaded:', props.formCategories.length)
    } else {
      console.warn('⚠️ No categories provided')
    }
    
  } catch (error) {
    console.error('❌ Error loading responses:', error)
  } finally {
    loading.value = false
  }
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    loadResponses()
  }
})
</script>
