<template>
 <!-- 📱 RESPONSIVE: Mobile-first responsive design -->
 <div class="h-[calc(100vh-120px)] flex bg-slate-50 rounded-lg shadow-sm overflow-hidden relative border border-slate-200 transition-colors duration-200">
 
 <!-- 📱 MOBILE: Back Button Overlay (only visible on mobile when in chat view) -->
 <div v-if="isMobile && currentMobileView === 'chat'" 
 class="absolute top-4 left-4 z-50 md:hidden">
 <button @click="goBackMobile" 
 class="p-2 bg-white rounded-full shadow-lg hover:shadow-xl transition-all duration-200 border border-gray-200">
 <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
 </svg>
 </button>
 </div>

 <!-- 💻 DESKTOP / 📱 MOBILE: Conversations Panel -->
 <div :class="[
 'border-r border-slate-300 flex flex-col bg-white transition-all duration-150 ease-in-out',
 // Desktop: Always show with fixed width
 'md:w-80 md:block', // Reduced from w-96 to w-80 for better mobile fit
 // Mobile: Full width when showing list, hidden when showing chat/info
 isMobile ? (currentMobileView === 'list' ? 'w-full' : 'w-0 overflow-hidden') : 'w-80'
 ]">
 <div class="p-4 bg-white border-b border-slate-200 shadow-sm">
 <div class="flex items-center justify-between mb-4">
 <h2 class="text-xl font-semibold text-slate-800">Messages</h2>
 <div class="flex gap-2">
 <button @click="showPendingMessages = true"
 :class="[
 'relative p-2 rounded-lg transition-all duration-200',
 pendingMessages.length > 0 
 ? 'text-amber-600 bg-amber-50 hover:text-amber-700 hover:bg-amber-100' 
 : 'text-slate-500 hover:text-amber-600 hover:bg-amber-50'
 ]"
 title="Pending Message Requests">
 <!-- Message bubble icon with pending indicator -->
 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"
 :class="pendingMessages.length > 0 ? 'animate-pulse' : ''">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
 d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
 </svg>
 <!-- Notification badge -->
 <span v-if="pendingMessages.length > 0"
 class="absolute -top-1 -right-1 bg-amber-500 text-white text-xs rounded-full min-w-[18px] h-4 flex items-center justify-center font-medium shadow-sm">
 {{ pendingMessages.length > 99 ? '99+' : pendingMessages.length }}
 </span>
 </button>
 <button @click="showBlockedUsers = true"
 class="p-2 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
 title="Blocked Users">
 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <circle cx="12" cy="12" r="9" stroke-width="2"></circle>
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6"></path>
 </svg>
 </button>
 <button @click="showCreateGroup = true"
 class="p-2 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all duration-200"
 title="Create Group">
 <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M17 20h5v-2a3 3 0 00-5.196-2.121M17 20H7m10 0v-2c0-5.523-3.582-10-8-10s-8 4.477-8 10v2m8-10a3 3 0 110-6 3 3 0 010 6zm0 10a3 3 0 110-6 3 3 0 010 6z" />
 </svg>
 </button>
 </div>
 </div>
 <div class="relative">
 <svg @click="focusSearch"
 class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400 cursor-pointer" fill="none"
 stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
 </svg>
 <input ref="searchInput" v-model="searchQuery" @input="debouncedSearch" type="text"
 placeholder="Search mates or groups..."
 class="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all duration-200" />
 <div v-if="searchQuery && searchResults.length"
 class="absolute top-full left-0 right-0 mt-2 bg-white border border-slate-200 rounded-lg shadow-lg z-10 max-h-96 overflow-y-auto">
 <div v-for="result in searchResults" :key="result.id" @click="selectSearchResult(result)"
 class="flex items-center p-3 hover:bg-slate-50 cursor-pointer">
 <img :src="getProfilePictureUrl(result)" class="w-10 h-10 rounded-full object-cover" />

 <div>
 <p class="font-semibold text-slate-800">{{ result.type === 'user' ? `${result.first_name}
 ${result.last_name}` : result.name }}</p>
 <p class="text-sm text-slate-500">{{ result.type === 'user' ? result.username : 'Group' }}</p>
 </div>
 </div>
 <div v-if="searchQuery && searchResults.length === 0" class="p-3 text-gray-500">No results found</div>
 </div>
 </div>
 </div>
 <div class="flex-1 overflow-y-auto">
 <div v-for="conversation in filteredConversations" :key="conversation.id"
 @click="selectConversation(conversation)"
 :class="[
 'flex items-center p-4 cursor-pointer border-b border-gray-100 transition-all duration-200 hover:bg-white conversation-item panel-transition',
 selectedConversation?.id === conversation.id ? 'bg-white border-r-4 border-green-500 shadow-sm' : (conversation.unreadCount > 0 ? 'bg-green-50' : 'hover:shadow-sm')
 ]">
 <div v-if="conversation.type === 'private'" class="relative flex-shrink-0 mr-4">
 <img :src="getProfilePictureUrl(conversation.mate)" class="w-12 h-12 rounded-full object-cover" />
 <!-- Blocked indicator -->
 <div v-if="conversation.isBlockedByMe || conversation.isBlockedByThem" 
 class="absolute -bottom-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center border-2 border-white">
 <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
 <path fill-rule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clip-rule="evenodd"/>
 </svg>
 </div>
 <!-- Online status indicator (only for non-blocked users) -->
 <div v-else
 :class="['absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-white', getStatusColor(conversation.mate)]" />
 </div>

 <div v-else class="relative flex-shrink-0 mr-4">
 <img :src="getProfilePictureUrl(conversation.group) || '/default-group.png'" alt="Group Avatar"
 class="w-14 h-14 rounded-full object-cover border-2 border-white shadow-sm" />
 </div>
 <div class="flex-1 min-w-0">
 <div class="flex items-center justify-between mb-1">
 <h3 :class="['text-gray-900 truncate text-lg', conversation.unreadCount > 0 ? 'font-bold' : 'font-semibold']">{{ conversation.type === 'private' ?
 `${conversation.mate.first_name} ${conversation.mate.last_name}` : conversation.group?.name || 'Unnamed Group' }}</h3>
 <div class="flex items-center gap-2">
 <!-- Block status indicators -->
 <span v-if="conversation.isBlockedByMe" 
 class="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full" 
 title="You have blocked this user">
 Blocked
 </span>
 <span v-else-if="conversation.isBlockedByThem" 
 class="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded-full" 
 title="This user has blocked you">
 Blocked you
 </span>
 <svg v-if="conversation.isMuted" class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor"
 viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
 </svg>
 <span class="text-xs text-gray-500 font-medium">{{ formatTimestamp(conversation.timestamp) }}</span>
 </div>
 </div>
 <div class="flex items-center justify-between">
 <p class="text-sm text-gray-600 truncate pr-2"
 :class="{ 'italic text-gray-400': conversation.isBlockedByMe || conversation.isBlockedByThem }">
 {{ conversation.isBlockedByMe ? 'Messages blocked' : 
 conversation.isBlockedByThem ? 'You are blocked by this user' : 
 conversation.lastMessage }}
 </p>
 <div v-if="conversation.type === 'private' && !conversation.isBlockedByMe && !conversation.isBlockedByThem" class="flex flex-col items-end text-xs">
 <span :class="getStatusTextColor(conversation.mate)">{{ getStatusText(conversation.mate) }}</span>
 <span class="text-gray-400 mt-0.5">{{ formatLastSeen(conversation.mate) }}</span>
 </div>
 <span v-if="conversation.unreadCount > 0 && !conversation.isBlockedByMe && !conversation.isBlockedByThem"
 class="bg-green-500 text-white text-xs rounded-full px-2 py-1 min-w-[24px] text-center font-medium">{{
 conversation.unreadCount }}</span>
 </div>
 </div>
 </div>
 <div v-if="filteredConversations.length === 0 && !searchQuery" class="text-center py-12 px-4">
 <svg class="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
 <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
 d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
 </svg>
 <p class="text-gray-500">No conversations found</p>
 <div v-if="pendingMessages.length > 0" class="mt-4 p-3 bg-orange-50 rounded-lg border border-orange-200">
 <p class="text-orange-700 text-sm font-medium">
 📬 You have {{ pendingMessages.length }} pending message {{ pendingMessages.length === 1 ? 'request' : 'requests' }}
 </p>
 <button @click="showPendingMessages = true" 
 class="mt-2 text-orange-600 hover:text-orange-700 text-sm underline">
 View pending requests
 </button>
 </div>
 </div>
 </div>
 </div>
 
 <!-- 💻 DESKTOP / 📱 MOBILE: Main Content Area (Chat + Chat Info) -->
 <div :class="[
 'flex transition-all duration-150 ease-in-out',
 // Desktop: Always show with flex-1
 'md:flex-1',
 // Mobile: Full width when showing chat/info, hidden when showing list
 isMobile ? (currentMobileView !== 'list' ? 'flex-1' : 'w-0 overflow-hidden') : 'flex-1'
 ]">
 
 <!-- 📱 MOBILE / 💻 DESKTOP: Chat Area -->
 <div :class="[
 'flex flex-col transition-all duration-150 ease-in-out',
 // Desktop: Always flex-1, hide when chat info is shown
 'md:flex-1',
 // Mobile: Full width when showing chat, hidden when showing chat-info
 isMobile ? (currentMobileView === 'chat' ? 'flex-1' : (currentMobileView === 'chat-info' ? 'w-0 overflow-hidden' : 'flex-1')) : (showChatInfo ? 'flex-1' : 'flex-1')
 ]">
 <ChatArea v-if="selectedConversation" :conversation="selectedConversation" :messages="messages"
 :current-user="currentUser" @send-message="sendMessage" @message-action="handleMessageAction" @message-read="handleMessageRead" 
 @toggle-chat-info="toggleChatInfo" />
 <EmptyState v-else />
 </div>
 
 <!-- 💻 DESKTOP / 📱 MOBILE: Chat Info Panel -->
 <div :class="[
 'transition-all duration-150 ease-in-out border-l border-gray-200',
 // Desktop: Show/hide with fixed width - reduced from w-80 to w-72 for mobile
 'md:w-72',
 showChatInfo ? 'md:block' : 'md:hidden',
 // Mobile: Full width when showing chat-info, hidden otherwise
 isMobile ? (currentMobileView === 'chat-info' ? 'flex-1' : 'w-0 overflow-hidden') : ''
 ]">
 <ChatInfoPanel 
 v-if="selectedConversation && showChatInfo" 
 :conversation="selectedConversation" 
 :messages="messages"
 :current-user="currentUser"
 :member-request-notification-trigger="memberRequestNotificationTrigger"
 :group-member-update-trigger="groupMemberUpdateTrigger"
 @close="closeChatInfo"
 @mute="handleMute"
 @unmute="handleUnmute"
 @block="handleBlock"
 @unblock="handleUnblock"
 @scroll-to-message="scrollToMessage"
 @group-photo-updated="handleGroupPhotoUpdated"
 @leave-group="handleLeaveGroup"
 />
 </div>
 </div>
 
 <!-- 📱 MOBILE / 💻 DESKTOP: Modals (unchanged) -->
 <PendingMessagesModal v-if="showPendingMessages" :pending-messages="pendingMessages"
 @close="showPendingMessages = false" @accept="acceptPendingMessage" @reject="rejectPendingMessage" />
 <CreateGroupModal v-if="showCreateGroup" :available-mates="availableMates" @close="showCreateGroup = false"
 @create-group="createGroup" />
 <BlockedUsersModal 
 v-if="showBlockedUsers" 
 :show="showBlockedUsers"
 @close="showBlockedUsers = false" 
 @user-unblocked="handleUserUnblocked" />
 <ForwardModal
 v-if="showForwardModal"
 :message="messageToForward"
 @close="showForwardModal = false"
 @forward="handleForwardComplete"
 />
 </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, triggerRef } from 'vue';
import debounce from 'lodash/debounce';
import { useAuthStore } from '@/stores/auth';
import { useMessagingNotificationStore } from '@/stores/messagingNotifications';
import api from '../../services/api';
import messagingService from '../../services/messaging';
import ChatArea from '../../components/messaging/ChatArea.vue';
import EmptyState from '../../components/messaging/EmptyState.vue';
import PendingMessagesModal from '../../components/messaging/PendingMessagesModal.vue';
import CreateGroupModal from '../../components/messaging/CreateGroupModal.vue';
import ChatInfoPanel from '../../components/messaging/ChatInfoPanel.vue';
import BlockedUsersModal from '../../components/messaging/BlockedUsersModal.vue';
import ForwardModal from '../../components/messaging/ForwardModal.vue';

// === STORES ===
const authStore = useAuthStore();
const messagingNotificationStore = useMessagingNotificationStore();

// === STATE ===
const isAuthenticated = ref(false);
const currentUser = ref(null);
const conversations = ref([]);
const selectedConversation = ref(null);
const messages = ref([]);
const pendingMessages = ref([]);
const availableMates = ref([]);

const showPendingMessages = ref(false);
const showCreateGroup = ref(false);
const showChatInfo = ref(false);
const showBlockedUsers = ref(false);
const showForwardModal = ref(false);
const messageToForward = ref(null);
const searchQuery = ref('');
const searchResults = ref([]);
const searchInput = ref(null);

// Real-time notification triggers
const memberRequestNotificationTrigger = ref(0);
const groupMemberUpdateTrigger = ref(0);

const privateWs = ref(null);
const groupWs = ref(null);
const notificationWs = ref(null);

// � MOBILE RESPONSIVENESS STATE
const isMobile = ref(false);
const currentMobileView = ref('list'); // 'list', 'chat', 'chat-info'

// �🔧 FIX: Enhanced heartbeat system to track multiple WebSocket connections
// Heartbeat system to keep WebSocket connections alive
let heartbeatInterval = null;
let heartbeatIntervals = new Set(); // Track multiple WebSocket heartbeats
let connectionStates = new Map(); // Track connection health

function startHeartbeat(ws) {
 stopHeartbeat(); // Clear any existing interval
 heartbeatInterval = setInterval(() => {
 if (ws && ws.readyState === WebSocket.OPEN) {
 if (isDev) debugLog('Messaging.vue: Sending heartbeat ping');
 ws.send(JSON.stringify({ action: 'ping' }));
 }
 }, 30000); // Send ping every 30 seconds
}

// 🔧 FIX: Enhanced heartbeat for specific WebSocket types
function startTypedHeartbeat(ws, wsType) {
 const intervalId = setInterval(() => {
 if (ws && ws.readyState === WebSocket.OPEN) {
 ws.send(JSON.stringify({ action: 'ping' }));
 connectionStates.set(wsType, 'healthy');
 } else {
 connectionStates.set(wsType, 'disconnected');
 if (isDev) debugLog(`${wsType} WebSocket disconnected, stopping heartbeat`);
 clearInterval(intervalId);
 heartbeatIntervals.delete(intervalId);
 }
 }, 30000);
 
 heartbeatIntervals.add(intervalId);
 connectionStates.set(wsType, 'connected');
 
 if (isDev) debugLog(`Heartbeat setup for ${wsType} WebSocket`);
 return intervalId;
}

function stopHeartbeat() {
 if (heartbeatInterval) {
 clearInterval(heartbeatInterval);
 heartbeatInterval = null;
 }
}

// 🔧 FIX: Stop all heartbeat intervals
function stopAllHeartbeats() {
 stopHeartbeat();
 heartbeatIntervals.forEach(intervalId => clearInterval(intervalId));
 heartbeatIntervals.clear();
 connectionStates.clear();
}

// === HELPER FUNCTIONS ===
// 🔧 FIX: Performance optimization - reduce console logging in production
const isDev = import.meta.env.DEV;
const debugLog = isDev ? console.log : () => {};
const debugError = console.error; // Always log errors

// === Helper to always return correct avatar URL for user/group (same logic as AlumniNavbar)
const getProfilePictureUrl = (entity) => {
 const BASE_URL = 'http://127.0.0.1:8000'
 const pic = entity?.profile_picture || entity?.group_picture
 return pic
 ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
 : '/default-avatar.png'
};

// === COMPUTED ===
const filteredConversations = computed(() => {
 if (!searchQuery.value) return conversations.value;
 return conversations.value.filter(conv => {
 const name = conv.type === 'private'
 ? `${conv.mate.first_name} ${conv.mate.last_name}`
 : conv.group.name;
 return name.toLowerCase().includes(searchQuery.value.toLowerCase());
 });
});

// === AUTH & TOKEN ===
async function validateToken() {
 if (!authStore.token) return (isAuthenticated.value = false);
 try {
 await api.get('/user/');
 return (isAuthenticated.value = true);
 } catch (error) {
 // Only treat 401 errors as authentication issues
 // 403 errors might be blocking-related, not authentication issues
 if (error.response?.status === 401 && await authStore.tryRefreshToken()) {
 return (isAuthenticated.value = true);
 }
 // For 403 errors, check if it's actually an auth issue by examining the error message
 if (error.response?.status === 403) {
 const errorMessage = error.response?.data?.error || error.response?.data?.detail || '';
 const isAuthError = errorMessage.toLowerCase().includes('token') || 
 errorMessage.toLowerCase().includes('authentication') ||
 errorMessage.toLowerCase().includes('credential');
 
 if (isAuthError && await authStore.tryRefreshToken()) {
 return (isAuthenticated.value = true);
 }
 
 // If it's not an auth error (likely blocking), don't log out
 if (!isAuthError) {
 console.log('403 error not related to authentication, keeping user logged in');
 return (isAuthenticated.value = true);
 }
 }
 isAuthenticated.value = false;
 }
}

async function refreshToken() {
 try {
 if (!authStore.refreshToken) return null;
 // Use the auth store's built-in refresh method instead of custom logic
 const success = await authStore.tryRefreshToken();
 return success ? authStore.token : null;
 } catch (e) {
 console.error('Token refresh failed in messaging component:', e);
 return null;
 }
}

const getValidToken = async () => authStore.token || await refreshToken();

// === FETCH DATA ===
const fetchCurrentUser = async () => {
 try { currentUser.value = (await api.get('/user/')).data; } catch (e) { console.error('User fetch error', e); }
};

const fetchConversations = async () => {
 try {
 // Fetch both private conversations and group conversations
 const [privateConversations, groupConversations] = await Promise.all([
 messagingService.getConversations().catch(err => {
 console.error('Error fetching private conversations:', err);
 return [];
 }),
 messagingService.getGroupConversations().catch(err => {
 console.error('Error fetching group conversations:', err);
 return [];
 })
 ]);
 
 // Transform private conversations
 const transformedPrivateConversations = (Array.isArray(privateConversations) ? privateConversations : []).map(conv => ({
 ...conv,
 id: conv.id || conv.mate.id,
 type: 'private',
 timestamp: conv.timestamp || conv.lastMessageTime || new Date().toISOString()
 }));
 
 // Transform group conversations to match the expected format
 const transformedGroupConversations = (Array.isArray(groupConversations) ? groupConversations : []).map(group => ({
 id: group.id,
 type: 'group',
 group: group.group || group, // Handle both nested and flat group structure
 lastMessage: group.lastMessage || '', // Use backend-provided lastMessage
 timestamp: group.timestamp || group.updated_at || group.created_at || new Date().toISOString(),
 unreadCount: group.unreadCount || 0 // Use backend-provided unreadCount
 }));
 
 // Combine and sort by timestamp
 const allConversations = [...transformedPrivateConversations, ...transformedGroupConversations];
 conversations.value = allConversations.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
 
 console.log('Messaging.vue: Fetched conversations:', conversations.value);
 console.log('Messaging.vue: Private conversations:', transformedPrivateConversations.length);
 console.log('Messaging.vue: Group conversations:', transformedGroupConversations.length);
 } catch (e) { 
 console.error('Conv fetch error', e);
 // Handle blocking-related errors gracefully
 if (e.response?.status === 403) {
 console.log('Some conversations may be hidden due to blocking');
 }
 }
};

const fetchMessages = async conv => {
 try {
 const data = conv.type === 'private'
 ? await messagingService.getMessages(conv.mate.id)
 : await messagingService.getGroupMessages(conv.group?.id);
 messages.value = data;
 } catch (e) { 
 console.error('Messages fetch error', e);
 // Handle blocking-related errors
 if (e.response?.status === 403) {
 console.log('Cannot access messages due to blocking');
 messages.value = [];
 // Don't show alert - just silently handle the blocking
 // The chat area will show the blocking message instead
 }
 }
};

const fetchPendingMessages = async () => {
 try {
 const { data } = await api.get('/message/requests/');
 pendingMessages.value = (data || []).map(req => ({
 id: req.id,
 name: `${req.sender.first_name} ${req.sender.last_name}`,
 avatar: getProfilePictureUrl(req.sender),
 message: 'Message request',
 timestamp: req.timestamp
 }));
 } catch (e) { console.error('Pending fetch error', e); }
};

const fetchAvailableMates = async () => {
 try {
 const { data } = await api.get('/message/search/');
 availableMates.value = (Array.isArray(data.users) ? data.users : []).map(u => ({
 ...u,
 profile_picture: getProfilePictureUrl(u)
 }));
 } catch (e) { console.error('Mates fetch error', e); }
};

// === SEARCH ===
async function search() {
 if (!searchQuery.value) return (searchResults.value = []);
 try {
 const { data } = await api.get(`/message/search/?q=${encodeURIComponent(searchQuery.value)}`);
 const users = (data.users || []).map(u => ({
 type: 'user',
 ...u,
 profile_picture: getProfilePictureUrl(u)
 }));
 const groups = (data.groups || []).map(g => ({ type: 'group', ...g }));
 searchResults.value = [...users, ...groups];
 } catch (e) { searchResults.value = []; }
}
const debouncedSearch = debounce(search, 300);

const focusSearch = () => searchQuery.value ? (searchQuery.value = searchResults.value = '') : searchInput.value?.focus();

// === AUTO-SELECT LAST CONVERSATION ===
const selectLastConversation = () => {
 if (conversations.value.length > 0) {
 // Sort conversations by timestamp (most recent first)
 const sortedConversations = [...conversations.value].sort((a, b) => {
 const timestampA = new Date(a.timestamp || 0).getTime();
 const timestampB = new Date(b.timestamp || 0).getTime();
 return timestampB - timestampA; // Descending order (newest first)
 });
 
 // Select the most recent conversation
 const lastConversation = sortedConversations[0];
 if (lastConversation) {
 console.log('Messaging.vue: Auto-selecting last conversation:', lastConversation);
 selectConversation(lastConversation);
 }
 }
};

// === CONVERSATION HANDLERS ===
async function selectSearchResult(r) {
 if (r.type === 'user') {
 let conv = conversations.value.find(c => c.type === 'private' && c.mate.id === r.id);
 if (!conv) {
 conv = { type: 'private', id: r.id, mate: r, lastMessage: '', timestamp: null, unreadCount: 0 };
 conversations.value.unshift(conv);
 }
 selectConversation(conv);
 } else if (r.type === 'group') {
 let group = conversations.value.find(c => c.type === 'group' && c.group.id === r.id);
 if (!group) {
 // Check if user is already a member of this group (admin/creator check)
 const isUserMember = r.members && r.members.some(member => member.id === currentUser.value.id);
 
 if (isUserMember) {
 // User is already a member (admin/creator), just fetch conversations to get the group
 console.log('User is already a member of this group, fetching conversations');
 await fetchConversations();
 group = conversations.value.find(c => c.type === 'group' && c.group.id === r.id);
 } else {
 // User is not a member, try to join the group
 try {
 await api.post(`/message/group/${r.id}/manage/`, { action: 'add_member', user_id: currentUser.value.id });
 await fetchConversations();
 group = conversations.value.find(c => c.type === 'group' && c.group.id === r.id);
 } catch (e) { 
 console.error('Join group error', e);
 // Show error message to user if join fails
 if (e.response?.data?.error) {
 alert(e.response.data.error);
 }
 }
 }
 }
 if (group) selectConversation(group);
 }
 searchQuery.value = '';
 searchResults.value = [];
}

function updateConversation(msg) {
 // 🔧 FIX: More efficient conversation finding and updating
 const conv = conversations.value.find(c =>
 (c.type === 'private' && c.mate.id === msg.sender.id) ||
 (c.type === 'group' && c.group.id === msg.group)
 );
 
 if (conv) {
 // 🔧 FIX: Only update if values actually changed to prevent unnecessary re-renders
 let hasChanges = false;
 
 if (conv.lastMessage !== msg.content) {
 conv.lastMessage = msg.content;
 hasChanges = true;
 }
 
 if (conv.timestamp !== msg.timestamp) {
 conv.timestamp = msg.timestamp;
 hasChanges = true;
 }
 
 // 📋 REFERENCE: Apply private message logic to groups
 // Private logic: if (selectedConversation.value?.id !== conv.id) conv.unreadCount++;
 // Group logic: Same logic - increment unread count if conversation not selected
 if (selectedConversation.value?.id !== conv.id) {
 // Only increment for messages not from current user (same as private messages)
 if (msg.sender?.id !== currentUser.value.id) {
 const oldCount = conv.unreadCount || 0;
 conv.unreadCount = oldCount + 1;
 hasChanges = true;
 }
 }
 
 // 🔧 FIX: Only trigger reactivity if something actually changed
 if (hasChanges && isDev) {
 debugLog('Conversation updated:', conv.id, 'unread:', conv.unreadCount);
 }
 } else if (msg.sender?.id !== currentUser.value.id) {
 // 🔧 FIX: Debounced fetch to prevent too many API calls
 clearTimeout(window.fetchConversationsTimeout);
 window.fetchConversationsTimeout = setTimeout(() => {
 fetchConversations();
 }, 500);
 }
}

// 📱 MOBILE RESPONSIVENESS METHODS
function checkScreenSize() {
 isMobile.value = window.innerWidth < 768; // md breakpoint
}

function goBackMobile() {
 if (currentMobileView.value === 'chat-info') {
 currentMobileView.value = 'chat';
 } else if (currentMobileView.value === 'chat') {
 currentMobileView.value = 'list';
 // Close chat info when going back to list
 showChatInfo.value = false;
 }
}

function toggleChatInfo() {
 if (isMobile.value) {
 // Mobile: Switch to chat info view
 showChatInfo.value = !showChatInfo.value;
 if (showChatInfo.value) {
 currentMobileView.value = 'chat-info';
 } else {
 currentMobileView.value = 'chat';
 }
 } else {
 // Desktop: Toggle panel visibility
 showChatInfo.value = !showChatInfo.value;
 }
}

function closeChatInfo() {
 showChatInfo.value = false;
 if (isMobile.value) {
 currentMobileView.value = 'chat';
 }
}

async function selectConversation(conv) {
 // 🔧 FIX: Prevent multiple simultaneous conversation selections
 if (conv.id === selectedConversation.value?.id) {
 console.log('Messaging.vue: Same conversation already selected, skipping');
 return;
 }
 
 console.log('Messaging.vue: Selecting conversation:', conv.id);
 
 // 🔧 FIX: Optimize conversation switching to reduce lag
 selectedConversation.value = conv;
 
 // Clear messages immediately to prevent showing wrong messages during load
 messages.value = [];
 
 try {
 // 🔧 FIX: Fetch messages with timeout to prevent hanging
 const fetchPromise = fetchMessages(conv);
 const timeoutPromise = new Promise((_, reject) => 
 setTimeout(() => reject(new Error('Message fetch timeout')), 10000)
 );
 
 await Promise.race([fetchPromise, timeoutPromise]);
 
 // Setup WebSocket and mark as read properly
 if (conv.type === 'group') {
 // 🔧 FIX: Ensure group WebSocket setup doesn't block UI
 setupGroupWebSocket(conv).catch(err => {
 console.error('Group WebSocket setup failed:', err);
 });
 } else {
 // 🔧 FIX: Properly close group WebSocket when switching to private
 if (groupWs.value) {
 groupWs.value.close();
 groupWs.value = null;
 }
 
 // For private messages, mark as read immediately since private WS is already connected
 if (privateWs.value?.readyState === WebSocket.OPEN) {
 privateWs.value.send(JSON.stringify({ action: 'mark_as_read', receiver_id: conv.mate.id }));
 }
 }

 // Reset unread count when opening the conversation
 if (typeof conv.unreadCount === 'number' && conv.unreadCount > 0) {
 conv.unreadCount = 0;
 // 🔧 FIX: Debounced reactivity update to reduce lag
 clearTimeout(window.unreadUpdateTimeout);
 window.unreadUpdateTimeout = setTimeout(() => {
 conversations.value = [...conversations.value];
 }, 10); // Reduced from 50ms to 10ms for faster response
 }

 // 🔔 NOTIFICATION: Refresh notification counts when conversation is opened
 // This ensures the sidebar badge is updated after messages are read
 setTimeout(async () => {
 try {
 await messagingNotificationStore.forceRefresh();
 console.log('🔔 Messaging.vue: Notification counts refreshed after opening conversation');
 } catch (error) {
 console.error('🔔 Messaging.vue: Failed to refresh notification counts:', error);
 }
 }, 100); // Reduced delay from 1000ms to 100ms for faster response
 
 } catch (error) {
 console.error('Error selecting conversation:', error);
 // Don't break the UI if conversation selection fails
 }
 
 // 📱 MOBILE: Switch to chat view when a conversation is selected
 if (isMobile.value) {
 currentMobileView.value = 'chat';
 // Close chat info when selecting a new conversation on mobile
 showChatInfo.value = false;
 }
}

// === MESSAGE ACTIONS ===
async function sendMessage(data) {
 console.log('Messaging.vue: sendMessage called with:', data);
 
 try {
 // Prevent double sending by checking if already processing
 if (data._processing) {
 console.log('Messaging.vue: Message already being processed, skipping');
 return;
 }
 data._processing = true;
 
 // Upload attachments
 const attachmentIds = await uploadAttachments(data.attachments);
 console.log('Messaging.vue: Attachment IDs:', attachmentIds);

 // Validate required data
 if (!currentUser.value) {
 console.error('Messaging.vue: Error: currentUser is null');
 return;
 }
 if (!selectedConversation.value || !selectedConversation.value.type) {
 console.error('Messaging.vue: Error: selectedConversation is invalid:', selectedConversation.value);
 return;
 }

 // Create unique temporary message ID to prevent duplicates
 const tempId = `temp-${Date.now()}-${Math.random()}`;
 
 // Create temporary message for UI
 const newMessage = {
 id: tempId,
 sender: currentUser.value,
 content: data.content,
 attachments: data.attachments.map(file => ({
 url: URL.createObjectURL(file),
 name: file.name,
 type: file.type
 })),
 timestamp: new Date().toISOString(),
 is_read: false,
 // ✅ FIX: Add reply relationship to temporary message for immediate display
 reply_to: data.reply_to_id ? messages.value.find(m => m.id === data.reply_to_id) : null,
 reply_to_id: data.reply_to_id || null,
 _isTemporary: true // Mark as temporary
 };
 
 console.log('Messaging.vue: Optimistically adding message to UI:', newMessage);
 messages.value.push(newMessage);

 // Prepare WebSocket payload
 const payload = {
 action: 'send_message',
 content: data.content,
 attachment_ids: attachmentIds,
 reply_to_id: data.reply_to_id,
 receiver_id: selectedConversation.value.mate?.id,
 temp_id: tempId // Include temp ID for deduplication
 };

 // Send via WebSocket
 if (selectedConversation.value.type === 'private') {
 if (!selectedConversation.value.mate?.id) {
 console.error('Messaging.vue: Error: mate.id is missing');
 messages.value = messages.value.filter(m => m.id !== tempId);
 return;
 }
 if (privateWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging.vue: Sending private WS payload:', payload);
 privateWs.value.send(JSON.stringify(payload));
 } else {
 console.error('Messaging.vue: Private WebSocket not open:', privateWs.value?.readyState);
 messages.value = messages.value.filter(m => m.id !== tempId);
 }
 } else if (selectedConversation.value.type === 'group') {
 if (!selectedConversation.value.group?.id) {
 console.error('Messaging.vue: Error: group.id is missing');
 messages.value = messages.value.filter(m => m.id !== tempId);
 return;
 }
 if (groupWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging.vue: Sending group WS payload:', payload);
 groupWs.value.send(JSON.stringify(payload));
 } else {
 console.error('Messaging.vue: Group WebSocket not open:', groupWs.value?.readyState);
 messages.value = messages.value.filter(m => m.id !== tempId);
 }
 } else {
 console.error('Messaging.vue: Invalid conversation type:', selectedConversation.value.type);
 messages.value = messages.value.filter(m => m.id !== tempId);
 }
 } catch (e) {
 console.error('Messaging.vue: Error in sendMessage:', e);
 // Remove temporary message on error
 if (data._processing) {
 const tempId = `temp-${Date.now()}-${Math.random()}`;
 messages.value = messages.value.filter(m => m.id !== tempId);
 }
 }
}

async function uploadAttachments(attachments) {
 console.log('Messaging.vue: Uploading attachments:', attachments);
 const ids = [];
 for (const att of attachments) {
 const formData = new FormData();
 formData.append('file', att);
 try {
 const response = await api.post('/message/upload/', formData, {
 headers: { 'Content-Type': 'multipart/form-data' }
 });
 console.log('Messaging.vue: Uploaded file:', att.name, 'ID:', response.data.id);
 ids.push(response.data.id);
 } catch (e) {
 console.error('Messaging.vue: Upload error for file:', att.name, e);
 throw e;
 }
 }
 return ids;
}

// Handle message actions from MessageBubble
async function handleMessageAction(actionData) {
 console.log('Messaging: Message action received:', actionData)
 const { action, message, newContent } = actionData
 
 try {
 switch (action) {
 case 'reply':
 // TODO: Set reply state in MessageInput
 console.log('Messaging: Reply to message:', message.id)
 break
 
 case 'forward':
 // Open forward modal
 console.log('Messaging: Forward message:', message.id)
 messageToForward.value = message
 showForwardModal.value = true
 break
 
 case 'pin':
 case 'unpin':
 // Pin/unpin message via WebSocket for real-time updates
 if (selectedConversation.value?.type === 'private') {
 if (privateWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging: Sending pin via WebSocket for message:', message.id)
 privateWs.value.send(JSON.stringify({
 action: 'pin_message',
 message_id: message.id
 }))
 } else {
 console.error('Messaging: Private WebSocket not open for pin')
 }
 } else if (selectedConversation.value?.type === 'group') {
 if (groupWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging: Sending group pin via WebSocket for message:', message.id)
 groupWs.value.send(JSON.stringify({
 action: 'pin_message',
 message_id: message.id
 }))
 } else {
 console.error('Messaging: Group WebSocket not open for pin')
 }
 }
 break
 
 case 'bump':
 // Bump message via WebSocket for real-time delivery
 if (selectedConversation.value?.type === 'private') {
 if (privateWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging: Sending bump via WebSocket for message:', message.id)
 privateWs.value.send(JSON.stringify({
 action: 'bump_message',
 original_message_id: message.id,
 receiver_id: selectedConversation.value.mate.id
 }))
 } else {
 console.error('Messaging: Private WebSocket not open for bump')
 }
 } else if (selectedConversation.value?.type === 'group') {
 if (groupWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging: Sending group bump via WebSocket for message:', message.id)
 groupWs.value.send(JSON.stringify({
 action: 'bump_message',
 original_message_id: message.id
 }))
 } else {
 console.error('Messaging: Group WebSocket not open for bump')
 }
 }
 break
 
 case 'edit':
 // Get the original content for potential rollback
 const originalContent = message.content;
 
 // Optimistically update the message content immediately for the sender
 const editMessageIndex = messages.value.findIndex(m => m.id === message.id);
 if (editMessageIndex !== -1) {
 const optimisticUpdate = {
 ...messages.value[editMessageIndex],
 content: newContent,
 edited_at: new Date().toISOString()
 };
 messages.value.splice(editMessageIndex, 1, optimisticUpdate);
 
 // Force reactivity
 nextTick(() => {
 messages.value = [...messages.value];
 console.log('✅ Optimistic edit: Updated message locally for immediate feedback');
 });
 }
 
 // Send edit via WebSocket for real-time delivery to other participants
 try {
 if (selectedConversation.value?.type === 'private') {
 if (privateWs.value?.readyState === WebSocket.OPEN) {
 const editPayload = {
 action: 'edit_message',
 message_id: message.id,
 new_content: newContent
 };
 console.log('🔴 SENDING EDIT: Private WebSocket payload:', editPayload)
 privateWs.value.send(JSON.stringify(editPayload))
 } else {
 throw new Error('Private WebSocket not open for edit')
 }
 } else if (selectedConversation.value?.type === 'group') {
 if (groupWs.value?.readyState === WebSocket.OPEN) {
 const editPayload = {
 action: 'edit_message',
 message_id: message.id,
 new_content: newContent
 };
 console.log('🔴 SENDING GROUP EDIT: Group WebSocket payload:', editPayload)
 groupWs.value.send(JSON.stringify(editPayload))
 } else {
 throw new Error('Group WebSocket not open for edit')
 }
 }
 } catch (error) {
 console.error('Messaging: Error sending edit via WebSocket:', error)
 
 // Rollback optimistic update on error
 if (editMessageIndex !== -1) {
 const rollbackUpdate = {
 ...messages.value[editMessageIndex],
 content: originalContent
 };
 messages.value.splice(editMessageIndex, 1, rollbackUpdate);
 nextTick(() => {
 messages.value = [...messages.value];
 console.log('❌ Edit failed: Rolled back optimistic update');
 });
 }
 }
 break
 
 case 'delete':
 // Delete message via WebSocket for real-time delivery
 if (selectedConversation.value?.type === 'private') {
 if (privateWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging: Sending delete via WebSocket for message:', message.id)
 privateWs.value.send(JSON.stringify({
 action: 'delete_message',
 message_id: message.id
 }))
 } else {
 console.error('Messaging: Private WebSocket not open for delete')
 }
 } else if (selectedConversation.value?.type === 'group') {
 if (groupWs.value?.readyState === WebSocket.OPEN) {
 console.log('Messaging: Sending group delete via WebSocket for message:', message.id)
 groupWs.value.send(JSON.stringify({
 action: 'delete_message',
 message_id: message.id
 }))
 } else {
 console.error('Messaging: Group WebSocket not open for delete')
 }
 }
 break
 
 case 'select':
 // TODO: Add to selection state for bulk actions
 console.log('Messaging: Selected message:', message.id)
 break
 
 case 'reaction_added':
 case 'reaction_updated':
 case 'reaction_removed':
 // Handle reaction updates - refresh the specific message reactions
 console.log('Messaging: Handling reaction update for message:', actionData.messageId)
 
 // The API call was already made by MessageBubble, just refresh the message
 // in a real app, this might fetch updated reaction stats from backend
 break
 
 default:
 console.warn('Messaging: Unknown message action:', action)
 }
 } catch (error) {
 console.error('Messaging: Error handling message action:', error)
 // TODO: Show error toast to user
 }
}

// Handle immediate message read feedback from ChatArea
function handleMessageRead(data) {
 console.log('📖 Handling immediate message read feedback:', data);
 
 const { messageId, readBy } = data;
 
 // Find the message and immediately update its read_by
 const messageIndex = messages.value.findIndex(m => m.id === messageId);
 if (messageIndex !== -1) {
 const message = messages.value[messageIndex];
 
 // Create a new message object with updated read_by to force reactivity
 const updatedMessage = {
 ...message,
 read_by: readBy || message.read_by
 };
 
 // Replace the message in the array
 messages.value[messageIndex] = updatedMessage;
 
 // Force Vue reactivity
 nextTick(() => {
 messages.value = [...messages.value];
 console.log('✅ Immediate read feedback: Updated message read status in UI');
 });
 }
}

// Send reaction via WebSocket for real-time delivery
function sendReaction(messageId, reactionType, isRemoving = false) {
 try {
 const action = isRemoving ? 'remove_reaction' : 'add_reaction';
 const payload = {
 action: action,
 message_id: messageId,
 reaction_type: reactionType
 };
 
 console.log(`Messaging: Sending ${action} via WebSocket:`, payload);
 
 if (selectedConversation.value?.type === 'private') {
 if (privateWs.value?.readyState === WebSocket.OPEN) {
 privateWs.value.send(JSON.stringify(payload));
 } else {
 console.error('Messaging: Private WebSocket not open for reaction');
 }
 } else if (selectedConversation.value?.type === 'group') {
 if (groupWs.value?.readyState === WebSocket.OPEN) {
 groupWs.value.send(JSON.stringify(payload));
 } else {
 console.error('Messaging: Group WebSocket not open for reaction');
 }
 }
 } catch (error) {
 console.error('Messaging: Error sending reaction:', error);
 }
}

const createGroup = async (groupData) => {
 try {
 let requestData;
 let config = {};
 
 // Check if it's FormData (new format with file upload support)
 if (groupData instanceof FormData) {
 requestData = groupData;
 // For FormData, don't set Content-Type header - let browser set it with boundary
 config.headers = {};
 } else {
 // Legacy format for backward compatibility
 requestData = { name: groupData.name, members: groupData.members };
 config.headers = { 'Content-Type': 'application/json' };
 }
 
 const { data } = await api.post('/message/group/create/', requestData, config);
 
 // Transform the group data into the conversation format expected by the frontend
 const groupConversation = {
 id: data.id,
 type: 'group',
 group: data, // The group data from backend
 lastMessage: '',
 timestamp: data.created_at || new Date().toISOString(),
 unreadCount: 0
 };
 
 conversations.value.unshift(groupConversation);
 showCreateGroup.value = false;
 selectConversation(groupConversation);
 } catch (e) { 
 console.error('Group create error', e);
 console.error('Error response:', e.response);
 console.error('Error status:', e.response?.status);
 console.error('Error data:', e.response?.data);
 
 // Show error to user
 if (e.response?.data?.error) {
 alert(e.response.data.error);
 } else {
 alert('Failed to create group. Please try again.');
 }
 }
};

const acceptPendingMessage = async (id) => {
 try {
 await api.post('/message/requests/', { action: 'accept', request_id: id });
 pendingMessages.value = pendingMessages.value.filter(m => m.id !== id);
 fetchConversations();
 } catch (e) { console.error('Accept error', e); }
};

const rejectPendingMessage = async (id) => {
 try {
 await api.post('/message/requests/', { action: 'decline', request_id: id });
 pendingMessages.value = pendingMessages.value.filter(m => m.id !== id);
 fetchConversations();
 } catch (e) { console.error('Reject error', e); }
};

// === BLOCK/UNBLOCK HANDLERS ===
const handleUserUnblocked = (user) => {
 console.log('🔓 User unblocked from BlockedUsersModal:', user);
 
 // Immediately update conversations to remove blocking status
 conversations.value.forEach(conv => {
 if (conv.type === 'private' && conv.mate.id === user.id) {
 console.log('🔓 Immediately updating conversation blocking status for:', conv.mate.first_name);
 conv.isBlockedByMe = false;
 conv.canSendMessage = true;
 // Update the conversation preview text if it was showing blocking message
 if (conv.lastMessage === 'Messages blocked') {
 conv.lastMessage = 'Start a conversation';
 }
 }
 });
 
 // Update selected conversation if it matches the unblocked user
 if (selectedConversation.value?.type === 'private' && 
 selectedConversation.value.mate.id === user.id) {
 console.log('🔓 Immediately updating selected conversation blocking status');
 selectedConversation.value.isBlockedByMe = false;
 selectedConversation.value.canSendMessage = true;
 }
 
 // Force Vue reactivity to update the UI immediately
 nextTick(() => {
 conversations.value = [...conversations.value];
 console.log('✅ Real-time: Conversation blocking status updated immediately for:', user.first_name, user.last_name);
 });
 
 // Still refresh conversations to ensure data consistency, but UI already updated
 fetchConversations();
};

// === CHAT INFO HANDLERS ===
const handleMute = () => {
 console.log('Chat muted');
 // Update conversation mute status if needed
 if (selectedConversation.value) {
 selectedConversation.value.isMuted = true;
 }
};

const handleUnmute = () => {
 console.log('Chat unmuted');
 // Update conversation mute status if needed
 if (selectedConversation.value) {
 selectedConversation.value.isMuted = false;
 }
};

const handleBlock = () => {
 console.log('User blocked');
 // The conversation will automatically be hidden from the list
 // due to backend filtering in fetchConversations
 fetchConversations();
 // Close the current conversation since it's now blocked
 if (selectedConversation.value) {
 selectedConversation.value = null;
 messages.value = [];
 showChatInfo.value = false;
 }
};

const handleUnblock = () => {
 console.log('🔓 User unblocked from ChatInfoPanel');
 
 // Immediately update selected conversation blocking status
 if (selectedConversation.value) {
 console.log('🔓 Immediately updating selected conversation after unblock');
 selectedConversation.value.isBlockedByMe = false;
 selectedConversation.value.canSendMessage = true;
 }
 
 // Update the conversation in the conversations list as well
 if (selectedConversation.value) {
 const conv = conversations.value.find(c => 
 c.type === 'private' && c.mate.id === selectedConversation.value.mate.id
 );
 if (conv) {
 conv.isBlockedByMe = false;
 conv.canSendMessage = true;
 // Update the conversation preview text if it was showing blocking message
 if (conv.lastMessage === 'Messages blocked') {
 conv.lastMessage = 'Start a conversation';
 }
 }
 }
 
 // Force Vue reactivity to update UI immediately
 nextTick(() => {
 conversations.value = [...conversations.value];
 console.log('✅ Real-time: Conversation unblocked immediately via ChatInfoPanel');
 });
 
 // Refresh conversations to ensure data consistency
 fetchConversations();
};

const scrollToMessage = (messageId) => {
 console.log('Messaging: Scrolling to pinned message:', messageId);
 
 // Find the message element and scroll to it
 const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
 if (messageElement) {
 // Scroll to the message
 messageElement.scrollIntoView({ 
 behavior: 'smooth', 
 block: 'center' 
 });
 
 // Add visual highlight effect specifically for pinned messages
 messageElement.classList.add('highlight-pinned-message');
 
 // Remove highlight after 3 seconds
 setTimeout(() => {
 messageElement.classList.remove('highlight-pinned-message');
 }, 3000);
 
 console.log('Messaging: Successfully scrolled to and highlighted pinned message');
 } else {
 console.warn('Messaging: Message element not found for ID:', messageId);
 }
};

const handleGroupPhotoUpdated = (data) => {
 console.log('Messaging: Group photo updated:', data);
 
 // Update the conversation in the conversations list
 const conversationIndex = conversations.value.findIndex(conv => 
 conv.type === 'group' && conv.group.id === data.groupId
 );
 
 if (conversationIndex !== -1) {
 conversations.value[conversationIndex].group.group_picture = data.newPhotoUrl;
 
 // Also update the selected conversation if it's the same group
 if (selectedConversation.value && 
 selectedConversation.value.type === 'group' && 
 selectedConversation.value.group.id === data.groupId) {
 selectedConversation.value.group.group_picture = data.newPhotoUrl;
 }
 
 // Force reactivity update
 nextTick(() => {
 conversations.value = [...conversations.value];
 console.log('✅ Messaging: Group photo updated in conversation list and selected conversation');
 });
 }
};

const handleLeaveGroup = (data) => {
 console.log('Messaging: User left group:', data);
 
 // Remove the conversation from the list
 const conversationIndex = conversations.value.findIndex(conv => 
 conv.type === 'group' && conv.group.id === data.groupId
 );
 
 if (conversationIndex !== -1) {
 conversations.value.splice(conversationIndex, 1);
 
 // If this was the selected conversation, clear it
 if (selectedConversation.value && 
 selectedConversation.value.type === 'group' && 
 selectedConversation.value.group.id === data.groupId) {
 selectedConversation.value = null;
 messages.value = [];
 showChatInfo.value = false;
 }
 
 console.log('✅ Messaging: Group removed from conversation list');
 }
};

// === WEBSOCKETS ===
function setupWebSockets() {
 getValidToken().then(token => {
 if (!token) return (isAuthenticated.value = false);
 
 // Set up private messaging WebSocket
 privateWs.value = new WebSocket(`ws://localhost:8000/ws/private/?token=${token}`);

 privateWs.value.onopen = () => {
 console.log('Messaging.vue: Private WS connected');
 // Start heartbeat to keep connection alive
 startHeartbeat(privateWs.value);
 };
 privateWs.value.onclose = () => {
 console.log('Messaging.vue: Private WS closed');
 stopHeartbeat();
 };
 privateWs.value.onerror = async (error) => {
 console.error('Messaging.vue: Private WS error:', error);
 stopHeartbeat();
 // Don't automatically logout on WebSocket errors
 // WebSocket can fail for many reasons (network, blocking, etc.)
 // Only reconnect if we still have valid authentication
 console.log('Messaging.vue: WebSocket error occurred, but keeping user logged in');
 };
 privateWs.value.onmessage = (e) => {
 const data = JSON.parse(e.data);
 console.log('🔵 WebSocket RECEIVED:', data);
 
 // 👁️ WebSocket DEBUG: Special logging for message_read_update events
 if (data.type === 'message_read_update') {
 console.log('👁️ WebSocket DEBUG: Received message_read_update event!');
 console.log('👁️ WebSocket DEBUG: Message ID:', data.message_id);
 console.log('👁️ WebSocket DEBUG: User ID:', data.user_id);
 console.log('👁️ WebSocket DEBUG: Read By Data:', data.read_by);
 console.log('👁️ WebSocket DEBUG: Full Event:', data);
 }
 
 // Special debugging for message_read_update events
 if (data.type === 'message_read_update') {
 console.log('👁️ WEBSOCKET: Received message_read_update event!');
 console.log('👁️ WEBSOCKET: Message ID:', data.message_id);
 console.log('👁️ WEBSOCKET: User ID:', data.user_id);
 console.log('👁️ WEBSOCKET: Read by data:', data.read_by);
 console.log('👁️ WEBSOCKET: Full event data:', data);
 }
 
 // Handle pong responses
 if (data.action === 'pong') {
 console.log('Messaging.vue: Received pong from server');
 return;
 }
 
 // ✅ Special debugging for edit events
 if (data.type === 'message_edited') {
 console.log('🔴 EDIT EVENT: Received message_edited via private WebSocket');
 console.log('🔴 EDIT EVENT: Message ID:', data.message_id);
 console.log('🔴 EDIT EVENT: New content:', data.new_content);
 console.log('🔴 EDIT EVENT: Event data:', data);
 }
 
 // ✅ FIX: Special handling for messages with reply_to data
 if (data.type === 'chat_message' && data.message) {
 if (data.message.reply_to) {
 console.log('🔵 WebSocket: Incoming message HAS reply_to data');
 console.log('🔵 WebSocket: Reply content:', data.message.reply_to.content);
 console.log('🔵 WebSocket: Reply sender:', data.message.reply_to.sender?.first_name);
 } else if (data.message.reply_to_id) {
 console.log('🔵 WebSocket: Incoming message has reply_to_id:', data.message.reply_to_id);
 } else {
 console.log('🔵 WebSocket: Incoming message has NO reply data');
 }
 }
 
 handleWsMessage(data, 'private');
 };
 
 // Set up notification WebSocket for real-time blocking/unblocking events
 setupNotificationWebSocket(token);
 });
}

function setupNotificationWebSocket(token) {
 console.log('🔔 Setting up notification WebSocket...');
 notificationWs.value = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);
 
 notificationWs.value.onopen = () => {
 console.log('🔔 Messaging.vue: Notification WS connected successfully!');
 };
 
 notificationWs.value.onclose = () => {
 console.log('🔔 Messaging.vue: Notification WS closed');
 };
 
 notificationWs.value.onerror = (error) => {
 console.error('🔔 Messaging.vue: Notification WS error:', error);
 };
 
 notificationWs.value.onmessage = (e) => {
 const data = JSON.parse(e.data);
 console.log('🔔 Notification WebSocket RECEIVED:', data);
 
 // Handle blocking/unblocking notifications
 if (data.type === 'user_unblocked' || data.type === 'user_blocked') {
 console.log('🔔 Processing blocking/unblocking event:', data.type);
 handleWsMessage(data, 'notification');
 } 
 // Handle status update notifications
 else if (data.type === 'status_update') {
 console.log('🔔 Processing status update event:', data);
 handleWsMessage(data, 'notification');
 } 
 // Handle group creation notifications
 else if (data.type === 'group_created') {
 console.log('🔔 Processing group creation event:', data);
 handleGroupCreatedNotification(data);
 }
 // Handle group member left notifications
 else if (data.type === 'group_member_left') {
 console.log('🔔 Processing group member left event:', data);
 handleGroupMemberLeftNotification(data);
 }
 // Handle group member added notifications
 else if (data.type === 'group_member_added') {
 console.log('🔔 Processing group member added event:', data);
 handleGroupMemberAddedNotification(data);
 } else if (data.type === 'group_message_preview') {
 // 📋 REFERENCE: Use same logic as private messages
 // Instead of duplicate logic, use the standardized updateConversation function
 console.log('🔔 Processing group_message_preview:', data);
 const msg = data.message;
 
 // Use the same updateConversation function that handles both private and group messages
 updateConversation(msg);
 
 console.log('📬 Real-time: Group conversation updated using private message reference logic');
 } else {
 console.log('🔔 Received other notification:', data.type);
 }
 };
}

function setupGroupWebSocket(conv) {
 // 🔧 FIX: Properly close existing connection to prevent multiple connections
 if (groupWs.value) {
 console.log('Messaging.vue: Closing existing group WebSocket');
 groupWs.value.close();
 groupWs.value = null;
 }
 
 return new Promise((resolve) => {
 getValidToken().then(token => {
 if (!token) {
 resolve();
 return;
 }
 
 console.log('Messaging.vue: Setting up group WebSocket for group:', conv.group.id);
 groupWs.value = new WebSocket(`ws://localhost:8000/ws/group/${conv.group.id}/?token=${token}`);
 
 groupWs.value.onopen = () => {
 console.log('Messaging.vue: Group WS connected');
 startHeartbeat(groupWs.value);
 
 // 📋 REFERENCE: Apply private message logic - mark as read when connection opens
 // Send mark_as_read immediately when WebSocket connects (same timing as private messages)
 console.log('🔥 Messaging.vue: Sending group mark_as_read on connection for group:', conv.group.id);
 const markReadPayload = { 
 action: 'mark_as_read', 
 group_id: conv.group.id 
 };
 console.log('🔥 Group mark_as_read payload:', markReadPayload);
 groupWs.value.send(JSON.stringify(markReadPayload));
 
 resolve(); // Resolve promise when connected and marked as read
 };
 
 groupWs.value.onclose = () => {
 console.log('Messaging.vue: Group WS closed');
 stopHeartbeat();
 };
 
 groupWs.value.onmessage = e => {
 const data = JSON.parse(e.data);
 console.log('🟢 Group WebSocket RECEIVED:', data);
 
 // Special debugging for message_read_update events
 if (data.type === 'message_read_update') {
 console.log('👁️ GROUP WEBSOCKET: Received message_read_update event!');
 console.log('👁️ GROUP WEBSOCKET: Message ID:', data.message_id);
 console.log('👁️ GROUP WEBSOCKET: User ID:', data.user_id);
 console.log('👁️ GROUP WEBSOCKET: Read by data:', data.read_by);
 console.log('👁️ GROUP WEBSOCKET: Full event data:', data);
 }
 
 // Handle pong responses
 if (data.action === 'pong') {
 console.log('Messaging.vue: Received pong from group server');
 return;
 }
 
 // ✅ Special debugging for edit events
 if (data.type === 'message_edited') {
 console.log('🔴 GROUP EDIT EVENT: Received message_edited via group WebSocket');
 console.log('🔴 GROUP EDIT EVENT: Message ID:', data.message_id);
 console.log('🔴 GROUP EDIT EVENT: New content:', data.new_content);
 console.log('🔴 GROUP EDIT EVENT: Event data:', data);
 }
 
 // 🔧 FIX: Additional validation to ensure message belongs to current group
 if (data.type === 'chat_message' && data.message) {
 if (data.message.group !== conv.group.id) {
 console.log('❌ Group WebSocket: Message not for current group, ignoring');
 return;
 }
 
 if (data.message.reply_to) {
 console.log('🟢 Group WebSocket: Incoming message HAS reply_to data');
 console.log('🟢 Group WebSocket: Reply content:', data.message.reply_to.content);
 } else if (data.message.reply_to_id) {
 console.log('🟢 Group WebSocket: Incoming message has reply_to_id:', data.message.reply_to_id);
 }
 }
 
 handleWsMessage(data, 'group');
 };
 
 groupWs.value.onerror = async (error) => {
 console.error('Messaging.vue: Group WS error:', error);
 stopHeartbeat();
 // 🔧 FIX: Clean up on error to prevent connection leaks
 if (groupWs.value) {
 groupWs.value.close();
 groupWs.value = null;
 }
 resolve(); // Resolve even on error to prevent hanging
 };
 });
 });
}

function handleWsMessage(data, scope) {
 console.log('Messaging.vue: Handling WebSocket message:', data, 'scope:', scope);
 
 // Special debugging for message_read_update events
 if (data.type === 'message_read_update') {
 console.log('🎯 HANDLER: Processing message_read_update event in handleWsMessage');
 console.log('🎯 HANDLER: Event data:', data);
 }
 
 // Handle error messages from backend
 if (data.error) {
 console.error('🔴 WebSocket Error:', data.error);
 
 // Handle blocking errors specifically
 if (data.blocked) {
 console.log('🚫 User is blocked, showing blocking message in chat area');
 
 // Add a system message to show the blocking error in chat
 const blockingMessage = {
 id: `system-${Date.now()}`,
 content: data.error,
 timestamp: new Date().toISOString(),
 isSystemMessage: true,
 blockingType: data.type, // 'blocked_by_me' or 'blocked_by_them'
 sender: { 
 id: 'system', 
 first_name: 'System', 
 last_name: '' 
 }
 };
 
 messages.value.push(blockingMessage);
 
 // Update conversation blocking status
 if (selectedConversation.value && data.type) {
 if (data.type === 'blocked_by_me') {
 selectedConversation.value.isBlockedByMe = true;
 } else if (data.type === 'blocked_by_them') {
 selectedConversation.value.isBlockedByThem = true;
 }
 selectedConversation.value.canSendMessage = false;
 }
 }
 
 // Remove any temporary messages on error
 if (data.temp_id) {
 messages.value = messages.value.filter(m => m.id !== data.temp_id);
 }
 
 return;
 }
 
 const actions = {
 chat_message: (data) => {
 console.log('Messaging.vue: Processing chat_message:', data);
 
 // DEBUG: Log reply information in detail
 if (data.message.reply_to) {
 console.log('🔵 WebSocket: Message HAS reply_to data:', data.message.reply_to)
 console.log('🔵 WebSocket: Reply_to content:', data.message.reply_to.content)
 console.log('🔵 WebSocket: Reply_to sender:', data.message.reply_to.sender)
 console.log('🔵 WebSocket: Reply_to ID:', data.message.reply_to.id)
 } else if (data.message.reply_to_id) {
 console.log('🔵 WebSocket: Message has reply_to_id but no reply_to object:', data.message.reply_to_id)
 } else {
 console.log('🔴 WebSocket: Message has NO reply_to data')
 }
 
 // Remove temporary messages (both generic temp and specific temp_id)
 if (data.temp_id) {
 messages.value = messages.value.filter(m => m.id !== data.temp_id);
 console.log('✅ Removed specific temporary message with ID:', data.temp_id);
 } else {
 // Remove any generic temporary messages
 messages.value = messages.value.filter(m => !m._isTemporary && !m.id.startsWith('temp-'));
 console.log('✅ Removed generic temporary messages');
 }
 
 // Add message to current conversation if it's selected
 if (scope === 'private' && selectedConversation.value?.type === 'private') {
 const senderId = data.message.sender.id;
 const receiverId = data.message.receiver.id;
 const currentUserId = currentUser.value.id;
 const selectedUserId = selectedConversation.value.mate.id;
 
 console.log('Messaging.vue: Message participants - sender:', senderId, 'receiver:', receiverId, 'current:', currentUserId, 'selected:', selectedUserId);
 
 // 🔧 FIX: More strict message filtering to prevent cross-contamination
 const isMessageForCurrentConversation = 
 (senderId === currentUserId && receiverId === selectedUserId) || 
 (senderId === selectedUserId && receiverId === currentUserId);
 
 // 🔧 FIX: Additional validation to ensure message belongs to this conversation
 if (isMessageForCurrentConversation && data.message.receiver && data.message.sender) {
 console.log('✅ Messaging.vue: Adding message to conversation (REAL-TIME)');
 
 // 🔧 FIX: Prevent duplicate messages with more comprehensive check
 const existingMessage = messages.value.find(m => 
 m.id === data.message.id || 
 (m.content === data.message.content && 
 Math.abs(new Date(m.timestamp) - new Date(data.message.timestamp)) < 1000)
 );
 if (existingMessage) {
 console.log('� ️ Message already exists or duplicate detected, skipping:', data.message.id);
 return;
 }
 
 // ✅ FIX: Create a deep copy to ensure reactivity
 const newMessage = JSON.parse(JSON.stringify(data.message));
 
 // ✅ FIX: Ensure reply_to data is preserved
 if (data.message.reply_to) {
 console.log('✅ WebSocket: Preserving reply_to data for real-time display');
 newMessage.reply_to = data.message.reply_to;
 }
 
 // Add the new message
 messages.value.push(newMessage);
 
 // 🔧 FIX: Optimized reactivity update to reduce lag
 nextTick(() => {
 // Only trigger reactivity if needed - reduced frequency to prevent lag
 if (newMessage.reply_to) {
 console.log('✅ Real-time: Message with reply_to added to UI:', newMessage.id);
 }
 
 // 🔧 FIX: Debounced auto-scroll to reduce performance impact
 clearTimeout(window.autoScrollTimeout);
 window.autoScrollTimeout = setTimeout(() => {
 const chatArea = document.querySelector('.chat-messages-container');
 if (chatArea) {
 chatArea.scrollTop = chatArea.scrollHeight;
 }
 }, 100);
 });
 } else {
 console.log('❌ Messaging.vue: Message NOT for current conversation - filtering out');
 }
 }
 
 if (scope === 'group' && selectedConversation.value?.type === 'group' && 
 selectedConversation.value?.group.id === data.message.group) {
 console.log('Messaging.vue: Adding group message to conversation');
 
 // 🔧 FIX: Enhanced duplicate detection for group messages
 const existingMessage = messages.value.find(m => 
 m.id === data.message.id || 
 (m.content === data.message.content && 
 m.sender.id === data.message.sender.id &&
 Math.abs(new Date(m.timestamp) - new Date(data.message.timestamp)) < 1000)
 );
 if (existingMessage) {
 console.log('� ️ Group message already exists or duplicate detected, skipping:', data.message.id);
 return;
 }
 
 // 🔧 FIX: Ensure message belongs to current group
 if (data.message.group !== selectedConversation.value.group.id) {
 console.log('❌ Group message not for current group - filtering out');
 return;
 }
 
 messages.value.push(data.message);
 
 // 🔧 FIX: Optimized reactivity for group messages
 nextTick(() => {
 // Debounced auto-scroll for performance
 clearTimeout(window.groupAutoScrollTimeout);
 window.groupAutoScrollTimeout = setTimeout(() => {
 const chatArea = document.querySelector('.chat-messages-container');
 if (chatArea) chatArea.scrollTop = chatArea.scrollHeight;
 }, 100);
 });
 }
 
 // Always update conversation list with latest message
 updateConversation(data.message);
 },
 status_update: (data) => {
 console.log('🟢 Messaging.vue: Processing status_update:', data);
 // Update user status in conversations list
 const userId = data.user_id;
 const newStatus = data.status;
 const lastSeen = data.last_seen;
 
 console.log(`🟢 Status update: User ${userId} → ${newStatus} at ${lastSeen}`);
 
 // Update conversations list
 let conversationUpdated = false;
 conversations.value.forEach(conv => {
 if (conv.type === 'private' && conv.mate.id === userId) {
 if (!conv.mate.profile) {
 conv.mate.profile = {};
 }
 conv.mate.profile.status = newStatus;
 conv.mate.profile.last_seen = lastSeen;
 conversationUpdated = true;
 console.log(`🟢 Updated conversation ${conv.mate.first_name} ${conv.mate.last_name} status to ${newStatus}`);
 }
 });
 
 // Update selected conversation if it matches
 if (selectedConversation.value?.type === 'private' && 
 selectedConversation.value.mate.id === userId) {
 if (!selectedConversation.value.mate.profile) {
 selectedConversation.value.mate.profile = {};
 }
 selectedConversation.value.mate.profile.status = newStatus;
 selectedConversation.value.mate.profile.last_seen = lastSeen;
 console.log(`🟢 Updated selected conversation status to ${newStatus}`);
 }
 
 // Update available mates list if needed
 if (availableMates.value.some(mate => mate.id === userId)) {
 availableMates.value.forEach(mate => {
 if (mate.id === userId) {
 if (!mate.profile) {
 mate.profile = {};
 }
 mate.profile.status = newStatus;
 mate.profile.last_seen = lastSeen;
 console.log(`🟢 Updated available mate ${mate.first_name} ${mate.last_name} status to ${newStatus}`);
 }
 });
 }
 
 // Force Vue reactivity to update UI immediately
 if (conversationUpdated) {
 nextTick(() => {
 conversations.value = [...conversations.value];
 console.log('🟢 ✅ Real-time: Status indicators updated immediately');
 });
 }
 },
 reaction_added: (data) => {
 const m = messages.value.find(m => m.id === data.message_id);
 if (m) (m.reactions ||= []).push({ user: { id: data.user_id }, emoji: data.emoji });
 },
 message_edited: (data) => {
 console.log('🔴 REAL-TIME EDIT: Received message_edited event:', data)
 const messageIndex = messages.value.findIndex(m => m.id === data.message_id);
 if (messageIndex !== -1) {
 console.log(`🔴 REAL-TIME EDIT: Found message at index ${messageIndex}`)
 console.log(`🔴 REAL-TIME EDIT: Updating content from "${messages.value[messageIndex].content}" to "${data.new_content}"`)
 
 // Create a new object to trigger Vue reactivity
 const updatedMessage = {
 ...messages.value[messageIndex],
 content: data.new_content,
 edited_at: data.edited_at || new Date().toISOString()
 };
 
 // Replace the message at the specific index to trigger reactivity
 messages.value.splice(messageIndex, 1, updatedMessage);
 
 // Force Vue reactivity with multiple strategies
 nextTick(() => {
 // Force array reactivity
 messages.value = [...messages.value];
 console.log('✅ REAL-TIME EDIT: Message content updated in UI:', data.message_id);
 console.log('✅ REAL-TIME EDIT: New content:', data.new_content);
 console.log('✅ REAL-TIME EDIT: UI should now show updated message');
 });
 } else {
 console.warn('🔴 REAL-TIME EDIT: Message not found for editing:', data.message_id);
 console.warn('🔴 REAL-TIME EDIT: Available message IDs:', messages.value.map(m => m.id));
 }
 },
 message_deleted: (data) => {
 console.log('Messaging: Received message_deleted event:', data)
 messages.value = messages.value.filter(m => m.id !== data.message_id)
 },
 message_pinned: (data) => {
 console.log('📌 Messaging: Received message_pinned event:', data)
 const messageIndex = messages.value.findIndex(m => m.id === data.message_id)
 if (messageIndex !== -1) {
 console.log(`📌 Messaging: Found message at index ${messageIndex}`)
 console.log(`📌 Messaging: Updating pin status to ${data.is_pinned}`)
 
 // Create a new object to trigger Vue reactivity
 const updatedMessage = {
 ...messages.value[messageIndex],
 is_pinned: data.is_pinned
 }
 
 // Replace the message at the specific index to trigger reactivity
 messages.value.splice(messageIndex, 1, updatedMessage)
 
 // Force Vue reactivity
 nextTick(() => {
 messages.value = [...messages.value]
 const action = data.is_pinned ? 'pinned' : 'unpinned'
 console.log(`✅ Pin: Message ${action} successfully:`, data.message_id)
 })
 } else {
 console.warn('📌 Messaging: Message not found for pin update:', data.message_id)
 }
 },
 messages_read: (data) => {
 // 📋 REFERENCE: Private message read logic
 messages.value.forEach(m => { 
 if (m.sender.id === selectedConversation.value?.mate.id) m.is_read = true; 
 });
 },
 group_messages_read: (data) => {
 console.log('🔄 Messaging.vue: Group messages marked as read by user:', data.user_id, 'in group:', data.group_id);
 
 // Handle two scenarios for real-time updates:
 // 1. If I'm in the same group chat - mark messages as read locally
 // 2. Mark messages I SENT as "read" when others mark them as read (real-time feedback)
 
 if (selectedConversation.value?.type === 'group' && 
 selectedConversation.value.group.id === parseInt(data.group_id)) {
 
 // Scenario 1: I'm viewing this group chat - mark incoming messages as read
 if (data.user_id === currentUser.value.id) {
 // This is me marking messages as read - mark messages from others
 console.log('✅ I marked group messages as read - updating my local view');
 messages.value.forEach(m => { 
 if (m.sender.id !== currentUser.value.id) {
 m.is_read = true;
 console.log('✅ Group message marked as read:', m.id);
 }
 });
 } else {
 // Scenario 2: Someone else marked messages as read - mark MY messages as read (real-time feedback)
 console.log('📬 Real-time: User', data.user_id, 'marked messages as read - updating read status for my messages');
 messages.value.forEach(m => {
 if (m.sender.id === currentUser.value.id) {
 m.is_read = true;
 console.log('📬 Real-time: My message marked as read by user', data.user_id, '- message:', m.id);
 }
 });
 }
 
 // Force Vue reactivity update
 nextTick(() => {
 messages.value = [...messages.value];
 console.log('✅ Real-time: Updated message read status in UI');
 });
 }
 
 // Always refresh conversation list to sync unread counts from backend
 console.log('🔄 Refreshing group conversations to sync unread count from backend');
 fetchConversations();
 },
 message_request: (data) => {
 console.log('Messaging.vue: Received message request:', data);
 fetchPendingMessages(); // Refresh pending messages
 // Also add to conversations if not exists
 updateConversationWithRequest(data.message);
 },
 request_accepted: (data) => {
 console.log('Messaging.vue: Message request was accepted:', data);
 fetchConversations(); // Refresh conversations
 fetchPendingMessages(); // Update pending messages count
 // If this user sent the request, the conversation should now be available
 },
 pending: () => fetchPendingMessages(),
 error: (data) => {
 console.error('Messaging.vue: WebSocket error received:', data);
 // Remove the temporary message if there was an error
 messages.value = messages.value.filter(m => !m.id.startsWith('temp-'));
 
 // If this was an edit error, we might need to revert optimistic updates
 if (data.error && data.error.includes('edit')) {
 console.error('Edit failed, consider reverting optimistic update');
 // TODO: Add logic to revert optimistic edit updates if needed
 }
 },
 status: (data) => {
 console.log('Messaging.vue: WebSocket status:', data);
 if (data.status === 'connected') {
 console.log('Messaging.vue: WebSocket connected successfully');
 } else if (data.status === 'success' && data.message) {
 // Message was sent successfully, temp message will be replaced by real-time message
 console.log('Messaging.vue: Message sent successfully');
 } else if (data.status === 'success' && data.action === 'message_edited') {
 console.log('✅ Edit confirmation: Message edited successfully:', data.message_id);
 // The actual content update should come through message_edited event
 } else if (data.status === 'success' && data.action === 'message_deleted') {
 console.log('✅ Delete confirmation: Message deleted successfully:', data.message_id);
 // The actual removal should come through message_deleted event
 } else if (data.status === 'pending') {
 console.log('Messaging.vue: Message request sent, waiting for acceptance');
 }
 },
 connected: (data) => {
 console.log('Messaging.vue: WebSocket connection established');
 },
 user_unblocked: (data) => {
 console.log('🔓 Real-time: User unblocked event received:', data);
 
 // This handler is for when the CURRENT USER gets unblocked by someone else
 // Update conversations to remove "Blocked you" status
 conversations.value.forEach(conv => {
 if (conv.type === 'private' && conv.mate.id === data.unblocked_by) {
 console.log('🔓 Real-time: Removing "blocked you" status from conversation with:', conv.mate.first_name);
 conv.isBlockedByThem = false;
 conv.canSendMessage = true;
 // Update the conversation preview text if it was showing blocking message
 if (conv.lastMessage === 'You are blocked by this user') {
 conv.lastMessage = 'Start a conversation';
 }
 }
 });
 
 // Update selected conversation if it matches
 if (selectedConversation.value?.type === 'private' && 
 selectedConversation.value.mate.id === data.unblocked_by) {
 console.log('🔓 Real-time: Removing "blocked you" status from selected conversation');
 selectedConversation.value.isBlockedByThem = false;
 selectedConversation.value.canSendMessage = true;
 }
 
 // Force Vue reactivity to update UI immediately
 nextTick(() => {
 conversations.value = [...conversations.value];
 console.log('✅ Real-time: User unblocked status updated immediately');
 });
 },
 user_blocked: (data) => {
 console.log('🚫 Real-time: User blocked event received:', data);
 
 // This handler is for when the CURRENT USER gets blocked by someone else
 // Update conversations to show "Blocked you" status
 conversations.value.forEach(conv => {
 if (conv.type === 'private' && conv.mate.id === data.blocked_by) {
 console.log('🚫 Real-time: Adding "blocked you" status to conversation with:', conv.mate.first_name);
 conv.isBlockedByThem = true;
 conv.canSendMessage = false;
 conv.lastMessage = 'You are blocked by this user';
 }
 });
 
 // Update selected conversation if it matches
 if (selectedConversation.value?.type === 'private' && 
 selectedConversation.value.mate.id === data.blocked_by) {
 console.log('🚫 Real-time: Adding "blocked you" status to selected conversation');
 selectedConversation.value.isBlockedByThem = true;
 selectedConversation.value.canSendMessage = false;
 
 // Add a system message to the chat to notify the user
 const blockingMessage = {
 id: `system-${Date.now()}`,
 content: 'You have been blocked by this user. You cannot send messages.',
 timestamp: new Date().toISOString(),
 isSystemMessage: true,
 sender: { 
 id: 'system', 
 first_name: 'System', 
 last_name: '' 
 }
 };
 messages.value.push(blockingMessage);
 }
 
 // Force Vue reactivity to update UI immediately
 nextTick(() => {
 conversations.value = [...conversations.value];
 console.log('✅ Real-time: User blocked status updated immediately');
 });
 },
 member_request_notification: (data) => {
 console.log('🔔 Real-time: Member request notification received:', data);
 
 // Trigger reactive update for ChatInfoPanel
 if (selectedConversation.value?.type === 'group' && 
 selectedConversation.value.group.id === data.group_id) {
 console.log('🔔 Real-time: Triggering pending requests refresh for current group');
 memberRequestNotificationTrigger.value++;
 }
 },
 group_added_notification: (data) => {
 console.log('🔔 Real-time: Group added notification received:', data);
 
 // Add system message to the chat if this is the current group
 if (selectedConversation.value?.type === 'group' && 
 selectedConversation.value.group.id === data.group_id) {
 const systemMessage = {
 id: `system-${Date.now()}`,
 content: `${data.added_user_name} was added to the group`,
 timestamp: new Date().toISOString(),
 isSystemMessage: true,
 sender: { 
 id: 'system', 
 first_name: 'System', 
 last_name: '' 
 }
 };
 messages.value.push(systemMessage);
 
 // Trigger group members refresh
 groupMemberUpdateTrigger.value++;
 }
 
 // If the current user was added to a new group, refresh conversations
 if (data.added_user_id === authStore.user.id) {
 console.log('🔔 Real-time: Current user was added to a group, refreshing conversations');
 fetchConversations();
 }
 },
 request_response_notification: (data) => {
 console.log('🔔 Real-time: Request response notification received:', data);
 
 // Show notification to requester about approval/rejection
 if (data.requester_id === authStore.user.id) {
 const action = data.status === 'approved' ? 'approved' : 'rejected';
 const systemMessage = {
 id: `system-${Date.now()}`,
 content: `Your request to add ${data.target_user_name} to the group was ${action}`,
 timestamp: new Date().toISOString(),
 isSystemMessage: true,
 sender: { 
 id: 'system', 
 first_name: 'System', 
 last_name: '' 
 }
 };
 
 // Add to current conversation if it's the same group
 if (selectedConversation.value?.type === 'group' && 
 selectedConversation.value.group.id === data.group_id) {
 messages.value.push(systemMessage);
 }
 
 // Refresh conversations if user was approved (new member will show)
 if (data.status === 'approved') {
 fetchConversations();
 }
 }
 
 // If current user is admin in the group, trigger refresh of pending requests
 if (selectedConversation.value?.type === 'group' && 
 selectedConversation.value.group.id === data.group_id &&
 selectedConversation.value.group?.admins?.some(admin => admin.id === authStore.user.id)) {
 console.log('🔔 Real-time: Admin received request response, refreshing pending requests');
 memberRequestNotificationTrigger.value++;
 }
 },
 message_reaction: (data) => {
 console.log('👍 Real-time: Message reaction received:', data);
 
 // Find and update the message with the new reaction data
 const messageToUpdate = messages.value.find(m => m.id === data.message_id);
 if (messageToUpdate) {
 console.log('👍 Real-time: Updating message reactions for:', data.message_id);
 
 // Update the reaction_stats on the message
 if (data.reaction_stats) {
 messageToUpdate.reaction_stats = data.reaction_stats;
 }
 
 // Force reactivity update
 nextTick(() => {
 messages.value = [...messages.value];
 console.log('✅ Real-time: Message reactions updated in UI');
 });
 
 // Update conversation last activity (optional)
 updateConversation({
 sender: { id: data.user_id, first_name: data.user_name },
 content: `${data.user_name} reacted ${data.emoji}`,
 timestamp: data.timestamp
 });
 } else {
 console.warn('👍 Real-time: Message not found for reaction update:', data.message_id);
 }
 },
 message_read_update: (data) => {
 console.log('👁️ Real-time: Received message_read_update:', data);
 console.log('👁️ Real-time: Current messages count:', messages.value.length);
 console.log('👁️ Real-time: Looking for message_id:', data.message_id);
 
 // Find the message and update its read_by array
 const messageIndex = messages.value.findIndex(m => m.id === data.message_id);
 console.log('👁️ Real-time: Found message at index:', messageIndex);
 
 if (messageIndex !== -1) {
 const message = messages.value[messageIndex];
 console.log('👁️ Real-time: Current message read_by:', message.read_by);
 
 // Use the complete read_by array from the backend
 if (data.read_by) {
 // Create a completely new read_by array to ensure reactivity
 const newReadBy = [...data.read_by];
 console.log('👁️ Real-time: Updated complete read_by array for message:', data.message_id, 'with users:', newReadBy.map(r => r.first_name));
 
 // Create a completely new message object to force Vue reactivity
 const updatedMessage = {
 ...message,
 read_by: newReadBy
 };
 
 // Replace the message in the array
 messages.value[messageIndex] = updatedMessage;
 
 // Force Vue reactivity with multiple approaches
 nextTick(() => {
 // Force re-render by creating new array reference
 messages.value = [...messages.value];
 console.log('✅ Real-time: Message read status FORCEFULLY updated in UI');
 console.log('✅ Real-time: New read_by count:', updatedMessage.read_by.length);
 });
 
 } else {
 // Fallback to old format for backwards compatibility
 const currentReadBy = message.read_by ? [...message.read_by] : [];
 
 const reader = data.reader || {
 id: data.user_id,
 first_name: data.user_name?.split(' ')[0] || 'Unknown',
 last_name: data.user_name?.split(' ')[1] || '',
 profile_picture: data.user_profile_picture
 };
 
 // Check if this user has already read this message
 const existingReadIndex = currentReadBy.findIndex(r => r.id === reader.id);
 
 if (existingReadIndex === -1) {
 // Add new read record
 currentReadBy.push({
 id: reader.id,
 first_name: reader.first_name,
 last_name: reader.last_name,
 profile_picture: reader.profile_picture,
 read_at: data.read_at
 });
 
 console.log('👁️ Real-time: Added read status for user:', reader.first_name, 'to message:', data.message_id);
 } else {
 // Update existing read record
 currentReadBy[existingReadIndex].read_at = data.read_at;
 console.log('👁️ Real-time: Updated read status for user:', reader.first_name, 'on message:', data.message_id);
 }
 
 // Create a completely new message object to force Vue reactivity
 const updatedMessage = {
 ...message,
 read_by: currentReadBy
 };
 
 // Replace the message in the array
 messages.value[messageIndex] = updatedMessage;
 
 // Force Vue reactivity
 nextTick(() => {
 messages.value = [...messages.value];
 console.log('✅ Real-time: Message read status updated in UI');
 });
 }
 } else {
 console.warn('👁️ Real-time: Message not found for read update:', data.message_id);
 console.warn('👁️ Real-time: Available message IDs:', messages.value.map(m => m.id));
 }
 }
 };
 
 const action = actions[data.type || data.status];
 if (action) {
 console.log('🎯 Messaging.vue: Executing action for type:', data.type || data.status);
 action(data);
 } else {
 console.warn('Messaging.vue: Unknown WebSocket message type:', data.type || data.status, data);
 }
}

// Function to update conversations when a new message request is received
function updateConversationWithRequest(messageRequest) {
 // This function can be expanded to add new conversations from message requests
 console.log('Updating conversation with request:', messageRequest);
}

// Function to handle real-time group creation notifications
function handleGroupCreatedNotification(data) {
 console.log('🎉 Real-time: Group created notification received:', data);
 
 try {
 // Transform the group data to match the conversation format
 const newGroupConversation = {
 id: data.group.id,
 type: 'group',
 group: data.group,
 lastMessage: `Added to group by ${data.creator.first_name} ${data.creator.last_name}`,
 timestamp: data.group.created_at || new Date().toISOString(),
 unreadCount: 0
 };
 
 // Check if this group is already in the conversations list
 const existingGroupIndex = conversations.value.findIndex(conv => 
 conv.type === 'group' && conv.group.id === data.group.id
 );
 
 if (existingGroupIndex === -1) {
 // Add the new group to the top of the conversations list
 conversations.value.unshift(newGroupConversation);
 
 // Force Vue reactivity
 nextTick(() => {
 conversations.value = [...conversations.value];
 console.log('✅ Real-time: New group added to conversation list:', data.group.name);
 });
 
 } else {
 console.log('Group already exists in conversations, skipping duplicate');
 }
 
 } catch (error) {
 console.error('Error handling group created notification:', error);
 }
}

// Function to handle real-time group member left notifications
function handleGroupMemberLeftNotification(data) {
 console.log('👋 Real-time: Group member left notification received:', data);
 
 try {
 // Check if this is for the current user (they left the group or were removed)
 if (data.user_left_group || data.group_id) {
 // Find the group conversation
 const conversationIndex = conversations.value.findIndex(conv => 
 conv.type === 'group' && conv.group.id === data.group_id
 );
 
 if (conversationIndex !== -1) {
 // Remove the group from the conversation list (user left or was removed from group)
 conversations.value.splice(conversationIndex, 1);
 
 // If this was the selected conversation, clear it
 if (selectedConversation.value && 
 selectedConversation.value.type === 'group' && 
 selectedConversation.value.group.id === data.group_id) {
 selectedConversation.value = null;
 messages.value = [];
 showChatInfo.value = false;
 }
 
 console.log('✅ Real-time: Removed group from conversation list after leaving/being removed');
 }
 } 
 // Handle system message for remaining members
 else if (data.system_message && data.left_user) {
 // Find the group conversation
 const conversationIndex = conversations.value.findIndex(conv => 
 conv.type === 'group' && conv.group.id === data.group_id
 );
 
 if (conversationIndex !== -1) {
 const conversation = conversations.value[conversationIndex];
 
 // Update the last message to show the system message
 conversation.lastMessage = data.system_message.content;
 conversation.timestamp = data.system_message.timestamp;
 
 console.log('✅ Real-time: Updated group conversation with member left message');
 
 // If this conversation is currently selected, add the system message to messages
 if (selectedConversation.value && 
 selectedConversation.value.type === 'group' && 
 selectedConversation.value.group.id === data.group_id) {
 
 const systemMessage = {
 id: data.system_message.id,
 content: data.system_message.content,
 timestamp: data.system_message.timestamp,
 sender: null,
 group: data.group_id,
 isSystemMessage: true
 };
 
 // Add the system message to the current messages
 messages.value.push(systemMessage);
 
 // Scroll to bottom to show the new message
 nextTick(() => {
 scrollToBottom();
 });
 }
 }
 }
 
 } catch (error) {
 console.error('Error handling group member left notification:', error);
 }
}

// Function to handle real-time group member added notifications
function handleGroupMemberAddedNotification(data) {
 console.log('➕ Real-time: Group member added notification received:', data);
 
 try {
 // Handle system message for existing members seeing the addition
 if (data.system_message && data.added_user) {
 // Find the group conversation
 const conversationIndex = conversations.value.findIndex(conv => 
 conv.type === 'group' && conv.group.id === data.group_id
 );
 
 if (conversationIndex !== -1) {
 const conversation = conversations.value[conversationIndex];
 
 // Update the last message to show the system message
 conversation.lastMessage = data.system_message.content;
 conversation.timestamp = data.system_message.timestamp;
 
 console.log('✅ Real-time: Updated group conversation with member added message');
 
 // If this conversation is currently selected, add the system message to messages
 if (selectedConversation.value && 
 selectedConversation.value.type === 'group' && 
 selectedConversation.value.group.id === data.group_id) {
 
 const systemMessage = {
 id: data.system_message.id,
 content: data.system_message.content,
 timestamp: data.system_message.timestamp,
 sender: null,
 group: data.group_id,
 isSystemMessage: true
 };
 
 // Add the system message to the current messages
 messages.value.push(systemMessage);
 
 // Scroll to bottom to show the new message
 nextTick(() => {
 scrollToBottom();
 });
 }
 
 // Move this conversation to the top of the list
 conversations.value.splice(conversationIndex, 1);
 conversations.value.unshift(conversation);
 
 console.log('✅ Real-time: Group member added message processed');
 }
 }
 
 } catch (error) {
 console.error('Error handling group member added notification:', error);
 }
}

// === UTILS ===
const formatTimestamp = ts => ts ? new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

// Status helper functions for online/offline indicators
const getStatusColor = (user) => {
 if (!user?.profile?.last_seen) {
 console.log(`getStatusColor: User ${user?.id} has no last_seen, returning gray`);
 return 'bg-gray-400'; // Default offline color
 }
 const isActive = isRecentlyActive(user);
 const color = isActive ? 'bg-green-500' : 'bg-gray-400';
 console.log(`getStatusColor: User ${user.id} (${user.first_name}) → ${color} (isActive: ${isActive})`);
 return color;
};

const getStatusTextColor = (user) => {
 const isActive = isRecentlyActive(user);
 return isActive ? 'text-green-600' : 'text-gray-500';
};

const getStatusText = (user) => {
 if (!user?.profile?.last_seen) return 'Offline';
 const isActive = isRecentlyActive(user);
 return isActive ? 'Online' : 'Offline';
};

const isRecentlyActive = (user) => {
 if (!user?.profile?.last_seen) {
 console.log(`isRecentlyActive: User ${user?.id} has no last_seen`);
 return false;
 }
 const lastSeen = new Date(user.profile.last_seen);
 const now = new Date();
 const diffMinutes = (now - lastSeen) / (1000 * 60);
 // Consider active if seen within last 2 minutes AND status is online
 const isRecent = diffMinutes <= 2;
 const isOnlineStatus = user.profile.status === 'online';
 const result = isRecent && isOnlineStatus;
 console.log(`isRecentlyActive for user ${user.id} (${user.first_name}): lastSeen=${lastSeen.toISOString()}, diffMinutes=${diffMinutes.toFixed(2)}, status=${user.profile.status}, isRecent=${isRecent}, isOnlineStatus=${isOnlineStatus}, result=${result}`);
 return result;
};

const formatLastSeen = (user) => {
 if (!user?.profile?.last_seen) return 'Never seen';
 
 const lastSeen = new Date(user.profile.last_seen);
 const now = new Date();
 const diffMinutes = (now - lastSeen) / (1000 * 60);
 
 if (diffMinutes < 1) return 'Just now';
 if (diffMinutes < 60) return `${Math.floor(diffMinutes)} minutes ago`;
 
 const diffHours = diffMinutes / 60;
 if (diffHours < 24) return `${Math.floor(diffHours)} hours ago`;
 
 const diffDays = diffHours / 24;
 if (diffDays < 7) return `${Math.floor(diffDays)} days ago`;
 
 return lastSeen.toLocaleDateString();
};

// === STATUS UPDATES ===
const handleGlobalStatusUpdate = (event) => {
 const data = event.detail;
 console.log('Messaging.vue: Received global status update from window event:', data);
 console.log('Messaging.vue: Current conversations before update:', conversations.value);
 console.log('Messaging.vue: Selected conversation before update:', selectedConversation.value);
 
 if (data.type === 'status_update') {
 const { user_id, status, last_seen } = data;
 console.log(`Messaging.vue: Processing status update for user ${user_id} to ${status}`);
 
 triggerRef(availableMates);
 }
};

// Handle forward completion
function handleForwardComplete(result) {
 showForwardModal.value = false
 messageToForward.value = null
 
 if (result.success) {
 // Show success toast/notification
 console.log('✅ Message forwarded successfully:', result.message)
 // You can add a toast notification here if you have one
 } else {
 // Show error toast/notification
 console.error('❌ Failed to forward message:', result.message)
 // You can add an error toast notification here if you have one
 }
}

// === LIFECYCLE ===
onMounted(async () => {
 console.log('Messaging.vue: Component mounted');
 
 if (await validateToken()) {
 await fetchCurrentUser();
 await Promise.all([
 fetchConversations(),
 fetchPendingMessages(),
 fetchAvailableMates()
 ]);
 
 setupWebSockets();
 selectLastConversation();
 
 // 🔔 NOTIFICATION: Initialize messaging notification store
 // This ensures notification counts are ready when the messaging view is loaded
 try {
 await messagingNotificationStore.initialize();
 console.log('🔔 Messaging.vue: Notification store initialized successfully');
 } catch (error) {
 console.error('🔔 Messaging.vue: Failed to initialize notification store:', error);
 }
 
 // Listen for global status updates
 window.addEventListener('statusUpdate', handleGlobalStatusUpdate);
 
 // 📱 MOBILE: Initialize screen size detection
 checkScreenSize();
 window.addEventListener('resize', checkScreenSize);
 } else {
 console.log('Messaging.vue: Token validation failed');
 }
});

onUnmounted(() => {
 if (isDev) debugLog('Messaging.vue: Component unmounting - cleaning up resources');
 
 // 🔧 FIX: Comprehensive cleanup to prevent memory leaks and lag
 
 // Stop all heartbeat intervals (enhanced system)
 stopAllHeartbeats();
 
 // Close all WebSocket connections with proper close codes
 if (privateWs.value) {
 privateWs.value.close(1000, 'Component unmounting');
 privateWs.value = null;
 }
 
 if (groupWs.value) {
 groupWs.value.close(1000, 'Component unmounting');
 groupWs.value = null;
 }
 
 if (notificationWs.value) {
 notificationWs.value.close(1000, 'Component unmounting');
 notificationWs.value = null;
 }
 
 // Clear timeouts to prevent memory leaks
 clearTimeout(window.autoScrollTimeout);
 clearTimeout(window.groupAutoScrollTimeout);
 clearTimeout(window.unreadUpdateTimeout);
 clearTimeout(window.fetchConversationsTimeout);
 clearTimeout(window.scrollTimeout);
 clearTimeout(window.selectConversationTimeout);
 
 // Remove global event listeners
 window.removeEventListener('statusUpdate', handleGlobalStatusUpdate);
 window.removeEventListener('user-status-update', handleGlobalStatusUpdate);
 
 // 📱 MOBILE: Remove screen size detection listener
 window.removeEventListener('resize', checkScreenSize);
 
 // Clear reactive data to free memory
 conversations.value = [];
 messages.value = [];
 searchResults.value = [];
 pendingMessages.value = [];
 selectedConversation.value = null;
 
 if (isDev) debugLog('Messaging.vue: Cleanup completed - all resources freed');
});
</script>

<style scoped>
/* Pinned message highlight effect */
:deep(.highlight-pinned-message) {
 background-color: rgba(245, 158, 11, 0.2) !important;
 border-left: 4px solid #f59e0b !important;
 box-shadow: 0 0 20px rgba(245, 158, 11, 0.3) !important;
 transform: scale(1.02) !important;
 transition: all 0.3s ease-in-out !important;
}

/* Smooth transition for all message bubbles */
:deep(.message-bubble) {
 transition: all 0.3s ease-in-out;
}

/* 📱 MOBILE RESPONSIVENESS: Smooth transitions and mobile-optimized layout */
@media (max-width: 767px) {
 /* Ensure mobile panels don't create horizontal scroll */
 .mobile-panel {
 min-width: 0;
 }
 
 /* Mobile-specific back button styling */
 .mobile-back-button {
 backdrop-filter: blur(10px);
 background-color: rgba(255, 255, 255, 0.95);
 }
 
 /* Mobile optimization for conversation list */
 .conversation-item:active {
 background-color: #f3f4f6;
 transform: scale(0.98);
 }
 
 /* Mobile touch targets */
 .conversation-item {
 min-height: 72px;
 padding: 16px;
 }
 
 /* Mobile header adjustments */
 .mobile-header {
 padding-left: 60px; /* Space for back button */
 }
}

/* Smooth panel transitions - faster for better mobile experience */
.panel-transition {
 transition: width 0.15s cubic-bezier(0.4, 0, 0.2, 1), 
 opacity 0.15s ease-in-out,
 transform 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced mobile experience */
@media (max-width: 767px) {
 /* Touch-friendly scrollbars on mobile */
 ::-webkit-scrollbar {
 width: 4px;
 }
 
 ::-webkit-scrollbar-track {
 background: transparent;
 }
 
 ::-webkit-scrollbar-thumb {
 background: rgba(156, 163, 175, 0.5);
 border-radius: 2px;
 }
 
 /* Improve text selection on mobile */
 .conversation-item {
 -webkit-touch-callout: none;
 -webkit-user-select: none;
 user-select: none;
 }
}
</style>
