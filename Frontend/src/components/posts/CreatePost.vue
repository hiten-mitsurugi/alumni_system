<template>
  <div class="create-post-card">
    <div :class="[
      'rounded-lg shadow-lg p-6',
      themeStore.isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'
    ]">
      <!-- Header -->
      <div class="flex items-center mb-4">
        <div class="w-10 h-10 rounded-full overflow-hidden bg-gray-300 mr-3">
          <img
            v-if="userStore.user.profile_picture"
            :src="userStore.user.profile_picture"
            :alt="userStore.user.first_name"
            class="w-full h-full object-cover"
          />
          <div
            v-else
            :class="[
              'w-full h-full flex items-center justify-center text-sm font-medium',
              themeStore.isDark ? 'bg-gray-600 text-gray-300' : 'bg-gray-400 text-white'
            ]"
          >
            {{ userStore.user.first_name?.[0] }}{{ userStore.user.last_name?.[0] }}
          </div>
        </div>
        <h3 :class="[
          'text-lg font-medium',
          themeStore.isDark ? 'text-white' : 'text-gray-900'
        ]">
          Create a Post
        </h3>
      </div>

      <!-- Post form -->
      <form @submit.prevent="handleSubmit">
        <!-- Content textarea with mentions -->
        <div class="mb-4">
          <MentionTextarea
            v-model="postContent"
            @mention="handleMention"
            @submit="handleSubmit"
            :placeholder="'What\'s on your mind? Use @ to mention alumni...'"
            :rows="4"
          />
          <div class="mt-2 text-sm" :class="themeStore.isDark ? 'text-gray-400' : 'text-gray-500'">
            {{ postContent.length }}/2000 characters
          </div>
        </div>

        <!-- Media upload section -->
        <div class="mb-4">
          <div class="flex flex-wrap gap-2 mb-3">
            <button
              type="button"
              @click="$refs.imageInput.click()"
              :class="[
                'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                themeStore.isDark 
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
              </svg>
              Photo
            </button>
            
            <button
              type="button"
              @click="$refs.videoInput.click()"
              :class="[
                'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                themeStore.isDark 
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 6a2 2 0 012-2h6l2 2h6a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V6zM14.553 7.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z"/>
              </svg>
              Video
            </button>

            <button
              type="button"
              @click="$refs.fileInput.click()"
              :class="[
                'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200',
                themeStore.isDark 
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8 2a2 2 0 00-2 2v12a2 2 0 002 2h8a2 2 0 002-2V7.414A2 2 0 0016.586 6L14 3.414A2 2 0 0012.586 3H8zm0 2h4.586L16 7.414V16H8V4z"/>
              </svg>
              File
            </button>
          </div>

          <!-- Hidden file inputs -->
          <input
            ref="imageInput"
            type="file"
            accept="image/*"
            multiple
            class="hidden"
            @change="handleFileSelect($event, 'image')"
          />
          <input
            ref="videoInput"
            type="file"
            accept="video/*"
            class="hidden"
            @change="handleFileSelect($event, 'video')"
          />
          <input
            ref="fileInput"
            type="file"
            multiple
            class="hidden"
            @change="handleFileSelect($event, 'file')"
          />

          <!-- File previews -->
          <div v-if="selectedFiles.length > 0" class="space-y-2">
            <div
              v-for="(file, index) in selectedFiles"
              :key="index"
              :class="[
                'flex items-center p-3 rounded-lg border',
                themeStore.isDark ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'
              ]"
            >
              <!-- File preview -->
              <div class="flex-shrink-0 w-12 h-12 mr-3 rounded-lg overflow-hidden bg-gray-300">
                <img
                  v-if="file.type === 'image' && file.preview"
                  :src="file.preview"
                  class="w-full h-full object-cover"
                  :alt="file.name"
                />
                <div
                  v-else
                  :class="[
                    'w-full h-full flex items-center justify-center text-xs font-medium',
                    themeStore.isDark ? 'bg-gray-600 text-gray-300' : 'bg-gray-400 text-white'
                  ]"
                >
                  {{ file.name.split('.').pop()?.toUpperCase() }}
                </div>
              </div>

              <!-- File info -->
              <div class="flex-1 min-w-0">
                <p :class="[
                  'text-sm font-medium truncate',
                  themeStore.isDark ? 'text-white' : 'text-gray-900'
                ]">
                  {{ file.name }}
                </p>
                <p :class="[
                  'text-xs',
                  themeStore.isDark ? 'text-gray-400' : 'text-gray-500'
                ]">
                  {{ formatFileSize(file.size) }} • {{ file.type }}
                </p>
              </div>

              <!-- Remove button -->
              <button
                type="button"
                @click="removeFile(index)"
                class="flex-shrink-0 ml-2 p-1 rounded-full text-gray-400 hover:text-red-500 transition-colors duration-200"
              >
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- Mentioned users display -->
        <div v-if="mentionedUsers.length > 0" class="mb-4">
          <p class="text-sm font-medium mb-2" :class="themeStore.isDark ? 'text-gray-300' : 'text-gray-700'">
            Mentioning:
          </p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="user in mentionedUsers"
              :key="user.id"
              :class="[
                'inline-flex items-center px-2 py-1 rounded-full text-xs font-medium',
                'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
              ]"
            >
              @{{ user.username }}
            </span>
          </div>
        </div>

        <!-- Action buttons -->
        <div class="flex justify-between items-center">
          <div class="flex space-x-2">
            <button
              type="button"
              @click="resetForm"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                themeStore.isDark 
                  ? 'text-gray-300 hover:text-white hover:bg-gray-700' 
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
              ]"
            >
              Clear
            </button>
          </div>

          <div class="flex space-x-2">
            <button
              type="button"
              @click="saveDraft"
              :disabled="!postContent.trim() || loading"
              :class="[
                'px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                postContent.trim() && !loading
                  ? (themeStore.isDark 
                      ? 'text-gray-300 hover:text-white hover:bg-gray-700 border border-gray-600' 
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50 border border-gray-300')
                  : 'text-gray-400 cursor-not-allowed border border-gray-300'
              ]"
            >
              Save Draft
            </button>

            <button
              type="submit"
              :disabled="!postContent.trim() || loading || postContent.length > 2000"
              :class="[
                'px-6 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                postContent.trim() && !loading && postContent.length <= 2000
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              ]"
            >
              <span v-if="loading">Publishing...</span>
              <span v-else>Publish</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'
import MentionTextarea from '@/components/common/MentionTextarea.vue'
import api from '@/services/api'

// Stores
const themeStore = useThemeStore()
const userStore = useUserStore()

// Reactive data
const postContent = ref('')
const selectedFiles = ref([])
const mentionedUsers = ref([])
const loading = ref(false)

// Props
const props = defineProps({
  initialContent: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['post-created', 'draft-saved'])

// Initialize with any initial content
if (props.initialContent) {
  postContent.value = props.initialContent
}

// Methods
const handleMention = (mentionData) => {
  const existingUser = mentionedUsers.value.find(u => u.id === mentionData.user.id)
  if (!existingUser) {
    mentionedUsers.value.push(mentionData.user)
  }
}

const handleFileSelect = (event, fileType) => {
  const files = Array.from(event.target.files)
  
  files.forEach(file => {
    const fileData = {
      file: file,
      name: file.name,
      size: file.size,
      type: fileType,
      preview: null
    }
    
    // Create preview for images
    if (fileType === 'image') {
      const reader = new FileReader()
      reader.onload = (e) => {
        fileData.preview = e.target.result
      }
      reader.readAsDataURL(file)
    }
    
    selectedFiles.value.push(fileData)
  })
  
  // Reset file input
  event.target.value = ''
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const extractMentions = (content) => {
  const mentionPattern = /@(\w+)/g
  const mentions = []
  let match
  
  while ((match = mentionPattern.exec(content)) !== null) {
    const username = match[1]
    const user = mentionedUsers.value.find(u => u.username === username)
    if (user) {
      mentions.push({
        user_id: user.id,
        username: user.username,
        start_position: match.index,
        end_position: match.index + match[0].length
      })
    }
  }
  
  return mentions
}

const handleSubmit = async () => {
  if (!postContent.value.trim() || loading.value) return
  
  loading.value = true
  
  try {
    const formData = new FormData()
    
    // Add basic post data
    formData.append('content', postContent.value)
    
    // Add mentions
    const mentions = extractMentions(postContent.value)
    formData.append('mentions', JSON.stringify(mentions))
    
    // Add files
    selectedFiles.value.forEach((fileData, index) => {
      formData.append(`files[${index}]`, fileData.file)
      formData.append(`file_types[${index}]`, fileData.type)
    })
    
    const response = await api.post('/posts/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data.success) {
      emit('post-created', response.data.post)
      resetForm()
      
      // Show success message (you might want to use a toast notification here)
      console.log('Post created successfully!')
    }
    
  } catch (error) {
    console.error('Error creating post:', error)
    // Handle error (show error message to user)
  } finally {
    loading.value = false
  }
}

const saveDraft = async () => {
  if (!postContent.value.trim() || loading.value) return
  
  try {
    const draftData = {
      content: postContent.value,
      mentions: extractMentions(postContent.value),
      files: selectedFiles.value.map(f => ({
        name: f.name,
        size: f.size,
        type: f.type
      }))
    }
    
    // Save to localStorage as a simple draft system
    const drafts = JSON.parse(localStorage.getItem('post_drafts') || '[]')
    drafts.push({
      id: Date.now(),
      ...draftData,
      created_at: new Date().toISOString()
    })
    localStorage.setItem('post_drafts', JSON.stringify(drafts))
    
    emit('draft-saved', draftData)
    console.log('Draft saved successfully!')
    
  } catch (error) {
    console.error('Error saving draft:', error)
  }
}

const resetForm = () => {
  postContent.value = ''
  selectedFiles.value = []
  mentionedUsers.value = []
}
</script>

<style scoped>
.create-post-card {
  max-width: 600px;
}
</style>