<script setup>
import { ref, onMounted } from 'vue';
import AlumniLayout from '../../components/layouts/AlumniLayout.vue';
// import api from '../../services/api';

const messages = ref([]);
const newMessage = ref('');
const selectedRecipient = ref('');
const showNewMessageModal = ref(false);
const searchQuery = ref('');

// Mock data for now
const mockMessages = ref([
  {
    id: 1,
    sender: 'John Smith',
    sender_email: 'john@example.com',
    subject: 'Alumni Reunion 2024',
    message: 'Hi everyone! Hope you can make it to our reunion this year.',
    timestamp: '2024-01-15 10:30:00',
    read: false,
    avatar: '👨‍💼'
  },
  {
    id: 2,
    sender: 'Jane Doe',
    sender_email: 'jane@example.com',
    subject: 'Job Opportunity',
    message: 'There\'s a great job opening at my company. Let me know if interested!',
    timestamp: '2024-01-14 15:45:00',
    read: true,
    avatar: '👩‍💼'
  },
  {
    id: 3,
    sender: 'Admin',
    sender_email: 'admin@alumni.com',
    subject: 'Welcome to Alumni Network',
    message: 'Welcome to our alumni network! Feel free to connect with fellow graduates.',
    timestamp: '2024-01-10 09:00:00',
    read: true,
    avatar: '🏛️'
  }
]);

const mockContacts = ref([
  { id: 1, name: 'John Smith', email: 'john@example.com', program: 'CS', year: '2020', avatar: '👨‍💼' },
  { id: 2, name: 'Jane Doe', email: 'jane@example.com', program: 'IT', year: '2019', avatar: '👩‍💼' },
  { id: 3, name: 'Robert Johnson', email: 'robert@example.com', program: 'Business', year: '2021', avatar: '👨‍💻' },
  { id: 4, name: 'Maria Garcia', email: 'maria@example.com', program: 'Engineering', year: '2020', avatar: '👩‍🔬' }
]);

const filteredMessages = ref([]);
const filteredContacts = ref([]);

const filterMessages = () => {
  if (!searchQuery.value) {
    filteredMessages.value = mockMessages.value;
    return;
  }
  
  filteredMessages.value = mockMessages.value.filter(message => 
    message.sender.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    message.subject.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    message.message.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
};

const filterContacts = () => {
  if (!searchQuery.value) {
    filteredContacts.value = mockContacts.value;
    return;
  }
  
  filteredContacts.value = mockContacts.value.filter(contact => 
    contact.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    contact.email.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    contact.program.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
};

const sendMessage = () => {
  if (!newMessage.value.trim() || !selectedRecipient.value) return;
  
  // Mock sending message
  const recipient = mockContacts.value.find(c => c.id === selectedRecipient.value);
  console.log('Sending message to:', recipient?.name, 'Message:', newMessage.value);
  
  // Add to messages (mock)
  mockMessages.value.unshift({
    id: Date.now(),
    sender: 'You',
    sender_email: 'you@example.com',
    subject: 'New Message',
    message: newMessage.value,
    timestamp: new Date().toISOString(),
    read: true,
    avatar: '👤',
    sent: true
  });
  
  // Reset form
  newMessage.value = '';
  selectedRecipient.value = '';
  showNewMessageModal.value = false;
  filterMessages();
};

const formatDate = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
};

onMounted(() => {
  filteredMessages.value = mockMessages.value;
  filteredContacts.value = mockContacts.value;
});
</script>

<template>
  <AlumniLayout>
    <div class="h-full">
      <div class="flex justify-between items-center mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-800">Messages</h1>
          <p class="text-gray-600">Connect with fellow alumni</p>
        </div>
        <button
          @click="showNewMessageModal = true"
          class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
        >
          <span>✏️</span>
          <span>New Message</span>
        </button>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
        <!-- Messages List -->
        <div class="lg:col-span-2 bg-white rounded-lg shadow-sm border overflow-hidden">
          <div class="p-4 border-b">
            <div class="flex items-center space-x-4 mb-4">
              <h2 class="text-lg font-semibold text-gray-800">Inbox</h2>
              <span class="bg-green-100 text-green-800 px-2 py-1 rounded-full text-xs font-medium">
                {{ filteredMessages.filter(m => !m.read).length }} unread
              </span>
            </div>
            <div class="relative">
              <input
                v-model="searchQuery"
                @input="filterMessages"
                type="text"
                placeholder="Search messages..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
              <span class="absolute left-3 top-2.5 text-gray-400">🔍</span>
            </div>
          </div>
          
          <div class="overflow-y-auto h-full">
            <div v-if="filteredMessages.length === 0" class="p-8 text-center text-gray-500">
              <span class="text-4xl mb-4 block">📭</span>
              <p>No messages found</p>
            </div>
            
            <div v-for="message in filteredMessages" :key="message.id" class="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
              <div class="p-4">
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                      <span class="text-lg">{{ message.avatar }}</span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between">
                      <h3 :class="[
                        'text-sm font-medium truncate',
                        message.read ? 'text-gray-600' : 'text-gray-900'
                      ]">
                        {{ message.sender }}
                        <span v-if="message.sent" class="text-green-600">(You)</span>
                      </h3>
                      <div class="flex items-center space-x-2">
                        <span v-if="!message.read" class="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span class="text-xs text-gray-500">
                          {{ formatDate(message.timestamp) }}
                        </span>
                      </div>
                    </div>
                    <p :class="[
                      'text-sm truncate mt-1',
                      message.read ? 'text-gray-500' : 'text-gray-700 font-medium'
                    ]">
                      {{ message.subject }}
                    </p>
                    <p class="text-xs text-gray-400 mt-1 truncate">
                      {{ message.message }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Contacts/Alumni List -->
        <div class="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div class="p-4 border-b">
            <h2 class="text-lg font-semibold text-gray-800 mb-4">Alumni Contacts</h2>
            <input
              v-model="searchQuery"
              @input="filterContacts"
              type="text"
              placeholder="Search contacts..."
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
            >
          </div>
          
          <div class="overflow-y-auto h-full">
            <div v-for="contact in filteredContacts" :key="contact.id" class="border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors">
              <div class="p-3">
                <div class="flex items-center space-x-3">
                  <div class="flex-shrink-0">
                    <div class="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <span class="text-sm">{{ contact.avatar }}</span>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h4 class="text-sm font-medium text-gray-900 truncate">{{ contact.name }}</h4>
                    <p class="text-xs text-gray-500">{{ contact.program }} '{{ contact.year }}</p>
                    <p class="text-xs text-gray-400 truncate">{{ contact.email }}</p>
                  </div>
                  <button
                    @click="selectedRecipient = contact.id; showNewMessageModal = true"
                    class="text-green-600 hover:text-green-800 p-1"
                    title="Send message"
                  >
                    💬
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- New Message Modal -->
      <div v-if="showNewMessageModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-semibold">New Message</h3>
            <button @click="showNewMessageModal = false" class="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>
          
          <form @submit.prevent="sendMessage">
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">To:</label>
              <select 
                v-model="selectedRecipient"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              >
                <option value="">Select recipient...</option>
                <option v-for="contact in mockContacts" :key="contact.id" :value="contact.id">
                  {{ contact.name }} ({{ contact.email }})
                </option>
              </select>
            </div>
            
            <div class="mb-4">
              <label class="block text-sm font-medium text-gray-700 mb-2">Message:</label>
              <textarea
                v-model="newMessage"
                rows="4"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Type your message here..."
                required
              ></textarea>
            </div>
            
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showNewMessageModal = false"
                class="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Send Message
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </AlumniLayout>
</template>

<style scoped>
/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
