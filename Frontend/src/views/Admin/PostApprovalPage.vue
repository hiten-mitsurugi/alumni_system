<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Reactive data
const pendingPosts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('newest')
const hasMore = ref(false)
const currentPage = ref(1)

// Stats
const approvedToday = ref(0)
const declinedToday = ref(0)
const activeUsers = ref(0)

// Modal state
const showDeclineForm = ref(false)
const selectedPost = ref(null)
const declineReason = ref('')

// Messages
const successMessage = ref('')
const errorMessage = ref('')

// Computed
const filteredPosts = computed(() => {
  let filtered = [...pendingPosts.value]
  
  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(post => 
      post.content.toLowerCase().includes(query) ||
      post.user.full_name?.toLowerCase().includes(query) ||
      `${post.user.first_name} ${post.user.last_name}`.toLowerCase().includes(query) ||
      (post.title && post.title.toLowerCase().includes(query))
    )
  }
  
  // Category filter
  if (selectedCategory.value) {
    filtered = filtered.filter(post => post.content_category === selectedCategory.value)
  }
  
  // Sort
  switch (sortBy.value) {
    case 'oldest':
      filtered.sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
      break
    case 'author':
      filtered.sort((a, b) => `${a.user.first_name} ${a.user.last_name}`.localeCompare(`${b.user.first_name} ${b.user.last_name}`))
      break
    default: // newest
      filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  }
  
  return filtered
})

// Methods
const fetchPendingPosts = async (page = 1) => {
  try {
    loading.value = true
    const response = await axios.get(`${BASE_URL}/api/posts/pending/`, {
      headers: { Authorization: `Bearer ${authStore.token}` },
      params: { page }
    })
    
    if (page === 1) {
      pendingPosts.value = response.data.results || response.data
    } else {
      pendingPosts.value = [...pendingPosts.value, ...(response.data.results || response.data)]
    }
    
    hasMore.value = response.data.next ? true : false
    
  } catch (error) {
    console.error('Error fetching pending posts:', error)
    errorMessage.value = 'Failed to load pending posts. Please try again.'
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  try {
    // These would be separate API endpoints for stats
    // For now, we'll use mock data or calculate from existing data
    approvedToday.value = 12
    declinedToday.value = 3
    activeUsers.value = 45
  } catch (error) {
    console.error('Error fetching stats:', error)
  }
}

const approvePost = async (postId) => {
  try {
    await axios.post(`${BASE_URL}/api/posts/${postId}/approve/`, {}, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    // Remove from pending list
    pendingPosts.value = pendingPosts.value.filter(post => post.id !== postId)
    
    successMessage.value = 'Post approved successfully!'
    approvedToday.value += 1
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
  } catch (error) {
    console.error('Error approving post:', error)
    errorMessage.value = 'Failed to approve post. Please try again.'
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  }
}

const declinePost = (post) => {
  selectedPost.value = post
  showDeclineForm.value = true
  declineReason.value = ''
}

const hideDeclineModal = () => {
  showDeclineForm.value = false
  selectedPost.value = null
  declineReason.value = ''
}

const confirmDecline = async () => {
  try {
    await axios.put(`${BASE_URL}/api/posts/${selectedPost.value.id}/decline/`, {
      reason: declineReason.value
    }, {
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    // Remove from pending list
    pendingPosts.value = pendingPosts.value.filter(post => post.id !== selectedPost.value.id)
    
    successMessage.value = 'Post declined successfully!'
    declinedToday.value += 1
    
    hideDeclineModal()
    
    // Clear success message after 3 seconds
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
    
  } catch (error) {
    console.error('Error declining post:', error)
    errorMessage.value = 'Failed to decline post. Please try again.'
    setTimeout(() => {
      errorMessage.value = ''
    }, 5000)
  }
}

const refreshPosts = () => {
  currentPage.value = 1
  fetchPendingPosts(1)
  fetchStats()
}

const loadMore = () => {
  currentPage.value += 1
  fetchPendingPosts(currentPage.value)
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatTimeAgo = (dateString) => {
  const now = new Date()
  const postDate = new Date(dateString)
  const diffMs = now - postDate
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 60) {
    return `${diffMins} minutes ago`
  } else if (diffHours < 24) {
    return `${diffHours} hours ago`
  } else {
    return `${diffDays} days ago`
  }
}

// Watchers
let searchTimeout = null

watch([searchQuery, selectedCategory, sortBy], () => {
  // Debounce search
  if (searchQuery.value) {
    clearTimeout(searchTimeout)
    searchTimeout = setTimeout(() => {
      // Re-filter happens automatically via computed property
    }, 300)
  }
})

// Lifecycle
onMounted(() => {
  fetchPendingPosts()
  fetchStats()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Post Approval</h1>
        <p class="text-gray-600">Review and approve pending posts from alumni and users</p>
        
        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-yellow-100 rounded-lg">
                <svg class="h-6 w-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Pending</p>
                <p class="text-2xl font-semibold text-gray-900">{{ pendingPosts.length }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-green-100 rounded-lg">
                <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Approved Today</p>
                <p class="text-2xl font-semibold text-gray-900">{{ approvedToday }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-red-100 rounded-lg">
                <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Declined Today</p>
                <p class="text-2xl font-semibold text-gray-900">{{ declinedToday }}</p>
              </div>
            </div>
          </div>
          
          <div class="bg-white rounded-lg p-4 shadow-sm border">
            <div class="flex items-center">
              <div class="p-2 bg-blue-100 rounded-lg">
                <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm font-medium text-gray-600">Active Users</p>
                <p class="text-2xl font-semibold text-gray-900">{{ activeUsers }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div class="flex flex-wrap gap-4 items-center">
          <div class="flex-1 min-w-64">
            <input 
              v-model="searchQuery"
              type="text"
              placeholder="Search posts by content, author..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <select 
            v-model="selectedCategory" 
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Categories</option>
            <option value="event">Event</option>
            <option value="news">News</option>
            <option value="discussion">Discussion</option>
            <option value="announcement">Announcement</option>
            <option value="job">Job</option>
            <option value="others">Others</option>
          </select>
          
          <select 
            v-model="sortBy" 
            class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="author">By Author</option>
          </select>
          
          <button 
            @click="refreshPosts"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Refresh
          </button>
        </div>
      </div>

      <!-- Posts List -->
      <div class="space-y-6">
        <div 
          v-if="loading" 
          class="flex justify-center items-center py-12"
        >
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span class="ml-3 text-gray-600">Loading pending posts...</span>
        </div>
        
        <div 
          v-else-if="filteredPosts.length === 0" 
          class="text-center py-12 bg-white rounded-lg shadow-sm border"
        >
          <svg class="h-12 w-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <h3 class="text-lg font-medium text-gray-900 mb-2">No pending posts</h3>
          <p class="text-gray-600">All posts have been reviewed. Great job!</p>
        </div>
        
        <div 
          v-else 
          v-for="post in filteredPosts" 
          :key="post.id"
          class="bg-white rounded-lg shadow-sm border overflow-hidden"
        >
          <!-- Post Card -->
          <div class="p-6">
            <!-- Author Info -->
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center space-x-3">
                <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-gray-700">
                    {{ post.user.first_name[0] }}{{ post.user.last_name[0] }}
                  </span>
                </div>
                <div>
                  <p class="font-semibold text-gray-900">{{ post.user.first_name }} {{ post.user.last_name }}</p>
                  <p class="text-sm text-gray-500">{{ formatDate(post.created_at) }}</p>
                </div>
              </div>
              
              <div class="flex items-center space-x-2">
                <span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                  {{ post.content_category.toUpperCase() }}
                </span>
                <span class="px-2 py-1 bg-orange-100 text-orange-800 text-xs font-medium rounded-full">
                  PENDING
                </span>
              </div>
            </div>
            
            <!-- Post Content -->
            <div class="mb-4">
              <h3 v-if="post.title" class="text-lg font-semibold text-gray-900 mb-2">{{ post.title }}</h3>
              <p class="text-gray-700 whitespace-pre-wrap">{{ post.content }}</p>
            </div>
            
            <!-- Post Image -->
            <div v-if="post.image" class="mb-4">
              <img 
                :src="post.image" 
                :alt="post.title || 'Post image'"
                class="rounded-lg max-w-full h-auto max-h-96 object-cover"
              />
            </div>
            
            <!-- Action Buttons -->
            <div class="flex items-center justify-between pt-4 border-t border-gray-200">
              <div class="flex items-center space-x-4 text-sm text-gray-500">
                <span>Posted {{ formatTimeAgo(post.created_at) }}</span>
                <span>•</span>
                <span>Category: {{ post.content_category }}</span>
              </div>
              
              <div class="flex items-center space-x-3">
                <button 
                  @click="declinePost(post)"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  Decline
                </button>
                
                <button 
                  @click="approvePost(post.id)"
                  class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                  </svg>
                  Approve
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div 
        v-if="hasMore && !loading" 
        class="text-center mt-8"
      >
        <button 
          @click="loadMore"
          class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Load More Posts
        </button>
      </div>
    </div>

    <!-- Decline Modal -->
    <div 
      v-if="showDeclineForm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="hideDeclineModal"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Decline Post</h3>
        <p class="text-gray-600 mb-4">Please provide a reason for declining this post:</p>
        
        <textarea
          v-model="declineReason"
          placeholder="Enter reason for decline..."
          class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
          rows="4"
        ></textarea>
        
        <div class="flex items-center justify-end space-x-3 mt-6">
          <button 
            @click="hideDeclineModal"
            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
          
          <button 
            @click="confirmDecline"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Decline Post
          </button>
        </div>
      </div>
    </div>

    <!-- Success/Error Messages -->
    <div 
      v-if="successMessage"
      class="fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50"
    >
      {{ successMessage }}
      <button @click="successMessage = ''" class="ml-2 text-green-700 hover:text-green-900">×</button>
    </div>
    
    <div 
      v-if="errorMessage"
      class="fixed top-4 right-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded z-50"
    >
      {{ errorMessage }}
      <button @click="errorMessage = ''" class="ml-2 text-red-700 hover:text-red-900">×</button>
    </div>
  </div>
</template>