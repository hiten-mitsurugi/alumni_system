<script setup>
import { Eye, Trash2 } from 'lucide-vue-next';

defineProps({
  post: {
    type: Object,
    required: true,
  },
  showApprovalActions: {
    type: Boolean,
    default: false,
  },
  onView: Function,
  onDelete: Function,
  onApprove: Function,
  onReject: Function,
});
</script>

<template>
  <div class="bg-white shadow-md rounded-lg flex mb-4">
    <!-- Image Placeholder -->
    <div class="w-32 h-32 bg-gray-200 flex items-center justify-center rounded-l-lg">
      <span class="text-gray-400">📷</span>
    </div>

    <!-- Content -->
    <div class="flex-1 p-4 flex flex-col justify-between">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <h3 class="text-lg font-bold">{{ post.title }}</h3>
          <span :class="{
            'bg-green-100 text-green-800': post.category.toLowerCase() === 'news',
            'bg-purple-100 text-purple-800': post.category.toLowerCase() === 'event',
            'bg-yellow-100 text-yellow-800': post.category.toLowerCase() === 'discussion' || post.category.toLowerCase() === 'job',
          }" class="text-sm px-2 py-1 rounded">
            {{ post.category }}
          </span>
          <span v-if="post.status" class="bg-yellow-100 text-yellow-800 text-sm px-2 py-1 rounded">
            {{ post.status }}
          </span>
        </div>
        <p class="text-gray-700 mb-2">{{ post.content || post.description }}</p>
        <p class="text-sm text-gray-500">
          Posted by {{ post.author || post.posted_by }} ({{ post.author_details }}) • {{ post.date }}
        </p>
      </div>

      <!-- Actions -->
      <div class="flex justify-end gap-2 mt-2">
        <button @click="onView(post)" class="flex items-center gap-1 text-gray-500 hover:text-gray-700">
          <Eye class="w-5 h-5" /> View
        </button>
        <button @click="onDelete(post)" class="flex items-center gap-1 text-gray-500 hover:text-gray-700">
          <Trash2 class="w-5 h-5" /> Delete
        </button>
        <template v-if="showApprovalActions">
          <button @click="onApprove(post)" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
            Approve
          </button>
          <button @click="onReject(post)" class="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
            Reject
          </button>
        </template>
      </div>
    </div>
  </div>
</template>