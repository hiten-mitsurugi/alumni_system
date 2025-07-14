<template>
  <div class="p-4 border-t border-gray-200 bg-white">
    <!-- Attachment Preview Area -->
    <div v-if="selectedFiles.length > 0" class="mb-3 p-2 border border-gray-200 bg-gray-50 rounded-lg">
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(file, index) in selectedFiles"
          :key="index"
          class="flex items-center bg-gray-200 text-gray-800 text-sm px-3 py-1 rounded-full shadow-sm"
        >
          <template v-if="file.type && file.type.startsWith('image/')">
            <img :src="file.previewUrl" :alt="file.name" class="w-8 h-8 object-cover rounded mr-2" />
          </template>
          <template v-else>
            <PaperclipIcon class="w-4 h-4 mr-1" />
          </template>
          <span class="truncate">{{ file.name }}</span>
          <button @click="removeFile(index)" class="ml-2 text-gray-600 hover:text-red-500 transition-colors duration-200">
            <XIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <div class="flex items-center space-x-3">
      <!-- Hidden File Input -->
      <input type="file" multiple @change="handleFileChange" ref="fileInput" class="hidden" accept="image/*,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document" />

      <!-- Attachment Button -->
      <button
        @click="triggerFileInput"
        class="p-3 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-full transition-colors duration-200 flex-shrink-0"
        title="Attach files"
      >
        <PaperclipIcon class="w-6 h-6" />
        <span class="sr-only">Attach files</span>
      </button>

      <div class="flex-1 relative">
        <input
          v-model="newMessage"
          @keyup.enter="sendMessage"
          type="text"
          placeholder="Type a message..."
          class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all duration-200"
        />
      </div>

      <!-- Send Button -->
      <button
        @click="sendMessage"
        :disabled="!newMessage.trim() && selectedFiles.length === 0"
        class="p-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex-shrink-0"
      >
        <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
        </svg>
        <span class="sr-only">Send message</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import { PaperclipIcon, XIcon } from 'lucide-vue-next'

const emit = defineEmits(['send-message'])

const newMessage = ref('')
const selectedFiles = ref([])
const fileInput = ref(null)

const sendMessage = () => {
  if (newMessage.value.trim() || selectedFiles.value.length > 0) {
    emit('send-message', {
      content: newMessage.value.trim(),
      attachments: selectedFiles.value.map(file => ({
        name: file.name,
        size: file.size,
        type: file.type,
        url: file.previewUrl // Use the previewUrl for display in MessageBubble
      }))
    })
    newMessage.value = ''
    clearSelectedFiles()
  }
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileChange = (event) => {
  const files = Array.from(event.target.files).map(file => {
    const previewUrl = file.type.startsWith('image/') ? URL.createObjectURL(file) : null;
    return {
      file, // Keep the original File object if needed for actual upload
      name: file.name,
      size: file.size,
      type: file.type,
      previewUrl // Temporary URL for client-side image preview
    };
  });
  selectedFiles.value = files;
}

const removeFile = (index) => {
  const fileToRemove = selectedFiles.value[index];
  if (fileToRemove && fileToRemove.previewUrl) {
    URL.revokeObjectURL(fileToRemove.previewUrl); // Clean up the object URL
  }
  selectedFiles.value.splice(index, 1);
  if (selectedFiles.value.length === 0 && fileInput.value) {
    fileInput.value.value = ''; // Clear the file input element
  }
}

const clearSelectedFiles = () => {
  selectedFiles.value.forEach(file => {
    if (file.previewUrl) {
      URL.revokeObjectURL(file.previewUrl);
    }
  });
  selectedFiles.value = [];
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

// Clean up object URLs when component is unmounted
onUnmounted(() => {
  clearSelectedFiles();
});
</script>
