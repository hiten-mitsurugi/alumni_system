<template>
  <div>
    <div class="w-96 bg-white border-l border-gray-200 flex flex-col">
    <!-- Header -->
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-800">Chat Info</h3>
        <button @click="$emit('close')" class="p-1 rounded-lg hover:bg-gray-100 transition-colors">
          <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-scroll chat-info-scroll" ref="scrollContainer">
      <!-- User/Group Profile Section -->
      <div class="p-4 border-b border-gray-200">
        <div class="text-center">
          <div class="relative inline-block">
            <img 
              :src="currentAvatarUrl"
              :key="conversation.type === 'group' ? conversation.group?.group_picture : conversation.mate?.profile_picture"
              alt="Profile"
              class="w-20 h-20 rounded-full object-cover mx-auto mb-3"
            />
            <!-- Change group photo button (only for group admins) -->
            <button 
              v-if="conversation.type === 'group' && isGroupAdmin"
              @click="triggerGroupPhotoUpload"
              class="absolute bottom-1 right-1 w-6 h-6 bg-green-600 rounded-full flex items-center justify-center text-white hover:bg-green-700 transition-colors shadow-lg"
              title="Change group photo"
            >
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
            <!-- Online status for private chats -->
            <div v-if="conversation.type === 'private'" 
                 :class="['absolute bottom-2 right-2 w-4 h-4 rounded-full border-2 border-white', getStatusColor(conversation.mate)]">
            </div>
          </div>
          <!-- Hidden file input for group photo upload -->
          <input 
            ref="groupPhotoInput" 
            type="file" 
            accept="image/*" 
            class="hidden" 
            @change="handleGroupPhotoUpload"
          />
          <h4 class="font-semibold text-gray-900 text-lg">
            {{ conversation.type === 'private' 
                ? `${conversation.mate.first_name} ${conversation.mate.last_name}` 
                : conversation.group?.name || 'Group' }}
          </h4>
          <p v-if="conversation.type === 'private'" class="text-sm text-gray-500">
            @{{ conversation.mate.username }}
          </p>
          <p v-if="conversation.type === 'private'" :class="['text-sm mt-1', getStatusTextColor(conversation.mate)]">
            {{ getStatusText(conversation.mate) }}
          </p>
          <p v-else class="text-sm text-gray-500 mt-1">
            {{ conversation.group?.members?.length || 0 }} members
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="p-4 border-b border-gray-200">
        <div class="grid grid-cols-2 gap-3">
          <!-- Block/Unblock (only for private chats) -->
          <button 
            v-if="conversation.type === 'private'"
            @click="toggleBlock"
            :class="[
              'flex flex-col items-center p-3 rounded-lg transition-all duration-200',
              isBlocked 
                ? 'bg-red-50 text-red-600 hover:bg-red-100' 
                : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
            ]"
          >
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="9" stroke-width="2"></circle>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6"></path>
            </svg>
            <span class="text-xs font-medium">{{ isBlocked ? 'Unblock' : 'Block' }}</span>
          </button>

          <!-- Search Messages -->
          <button 
            @click="showSearchMessages = true"
            class="flex flex-col items-center p-3 rounded-lg bg-gray-50 text-gray-600 hover:bg-gray-100 transition-all duration-200"
          >
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <span class="text-xs font-medium">Search</span>
          </button>

          <!-- Leave Group (only for group chats) -->
          <button 
            v-if="conversation.type === 'group'"
            @click="leaveGroup"
            class="flex flex-col items-center p-3 rounded-lg bg-red-50 text-red-600 hover:bg-red-100 transition-all duration-200"
          >
            <svg class="w-6 h-6 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span class="text-xs font-medium">Leave</span>
          </button>
        </div>
      </div>

      <!-- Group Members (only for groups) -->
      <div v-if="conversation.type === 'group'" class="border-b border-gray-200">
        <button 
          @click="showGroupMembers = !showGroupMembers"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M17 20h5v-2a3 3 0 00-5.196-2.121M17 20H7m10 0v-2c0-5.523-3.582-10-8-10s-8 4.477-8 10v2m8-10a3 3 0 110-6 3 3 0 010 6zm0 10a3 3 0 110-6 3 3 0 010 6z" />
            </svg>
            <span class="font-medium text-gray-900">Members</span>
            <span class="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
              {{ groupMembers.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showGroupMembers ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <!-- Members List -->
        <div v-if="showGroupMembers" class="max-h-64 overflow-y-auto">
          <div v-if="groupMembers.length === 0" class="p-4 text-center text-gray-500 text-sm">
            No members found
            <div class="text-xs mt-1">Debug: API called, response processed</div>
          </div>
          <div 
            v-for="member in groupMembers" 
            :key="member.id"
            class="p-3 mx-3 mb-2 bg-green-50 rounded-lg hover:bg-green-100 transition-all duration-200 border border-green-200"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div class="relative">
                  <img 
                    :src="getProfilePictureUrl(member)" 
                    alt="Member avatar"
                    class="w-10 h-10 rounded-full object-cover"
                  />
                  <!-- Online status indicator -->
                  <div :class="['absolute bottom-0 right-0 w-3 h-3 rounded-full border-2 border-white', getStatusColor(member)]" />
                </div>
                <div>
                  <p class="font-medium text-gray-900 text-sm">{{ member.first_name }} {{ member.last_name }}</p>
                  <p class="text-xs text-gray-500">@{{ member.username }}</p>
                </div>
              </div>
              <div class="flex items-center gap-2">
                <!-- Admin badge -->
                <span 
                  v-if="isGroupCreator(member)"
                  class="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-full font-medium"
                >
                  Admin
                </span>
                
                <!-- Remove member button for admins -->
                <button 
                  v-if="isGroupAdmin && member.id !== currentUser.id && !isGroupCreator(member)"
                  @click="removeMember(member)"
                  class="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Remove member"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Add Member Section (for all members, but different behavior) -->
          <div class="p-3 mx-3 mb-2">
            <div v-if="!showAddMemberForm" class="text-center">
              <button 
                @click="showAddMemberForm = true"
                class="w-full flex items-center justify-center gap-2 p-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                {{ isGroupAdmin ? 'Add Member' : 'Request to Add Member' }}
              </button>
            </div>
            
            <!-- Add Member Form -->
            <div v-if="showAddMemberForm" class="space-y-3">
              <div class="relative">
                <input 
                  v-model="memberSearchQuery"
                  @input="searchAvailableMembers"
                  type="text"
                  placeholder="Search users to add..."
                  class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                />
                <svg class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              
              <!-- Optional message for non-admins -->
              <div v-if="!isGroupAdmin" class="space-y-2">
                <label class="block text-sm font-medium text-gray-700">Optional message to admins:</label>
                <textarea 
                  v-model="requestMessage"
                  placeholder="Why should this person be added to the group?"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                  rows="2"
                ></textarea>
              </div>

              <!-- Available Users -->
              <div v-if="availableUsers.length > 0" class="max-h-32 overflow-y-auto space-y-2">
                <div 
                  v-for="user in availableUsers" 
                  :key="user.id"
                  class="flex items-center justify-between p-2 bg-white rounded border hover:bg-gray-50 transition-colors"
                >
                  <div class="flex items-center gap-2">
                    <img 
                      :src="getProfilePictureUrl(user)" 
                      alt="User avatar"
                      class="w-6 h-6 rounded-full object-cover"
                    />
                    <div>
                      <p class="font-medium text-gray-900 text-xs">{{ user.first_name }} {{ user.last_name }}</p>
                      <p class="text-xs text-gray-500">@{{ user.username }}</p>
                    </div>
                  </div>
                  <button 
                    @click="addMemberToGroup(user)"
                    class="px-2 py-1 bg-green-600 text-white text-xs rounded hover:bg-green-700 transition-colors"
                  >
                    Add
                  </button>
                </div>
              </div>
              
              <div v-if="memberSearchQuery && availableUsers.length === 0" class="text-center text-gray-500 text-xs py-2">
                No users found
              </div>
              
              <button 
                @click="cancelAddMember"
                class="w-full p-2 text-gray-600 hover:text-gray-800 text-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Pending Member Requests (for admins only) -->
      <div v-if="conversation.type === 'group' && isGroupAdmin && pendingRequests.length > 0" class="border-b border-gray-200">
        <button 
          @click="showPendingRequests = !showPendingRequests"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="font-medium text-gray-900">Pending Requests</span>
            <span class="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
              {{ pendingRequests.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showPendingRequests ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <!-- Pending Requests List -->
        <div v-if="showPendingRequests" class="max-h-64 overflow-y-auto">
          <div 
            v-for="request in pendingRequests" 
            :key="request.id"
            class="p-4 mx-3 mb-2 bg-orange-50 rounded-lg border border-orange-200"
          >
            <div class="space-y-3">
              <!-- Request Info -->
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <img 
                    :src="getProfilePictureUrl(request.requested_user)" 
                    alt="User avatar"
                    class="w-10 h-10 rounded-full object-cover"
                  />
                  <div>
                    <div class="font-medium text-gray-900">
                      {{ request.requested_user.first_name }} {{ request.requested_user.last_name }}
                    </div>
                    <div class="text-sm text-gray-500">
                      Requested by {{ request.requester.first_name }} {{ request.requester.last_name }}
                    </div>
                  </div>
                </div>
                <div class="text-xs text-gray-500">
                  {{ formatDate(request.created_at) }}
                </div>
              </div>
              
              <!-- Request Message -->
              <div v-if="request.message" class="text-sm text-gray-700 bg-white p-2 rounded border">
                "{{ request.message }}"
              </div>
              
              <!-- Action Buttons -->
              <div class="flex gap-2">
                <button 
                  @click="handleMemberRequest(request.id, 'approve')"
                  class="flex-1 px-3 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 transition-colors"
                >
                  Approve
                </button>
                <button 
                  @click="handleMemberRequest(request.id, 'reject')"
                  class="flex-1 px-3 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors"
                >
                  Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pinned Messages -->
      <div class="border-b border-gray-200">
        <button 
          @click="showPinnedMessages = !showPinnedMessages"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-amber-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
            <span class="font-medium text-gray-900">Pinned Messages</span>
            <span class="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-full">
              {{ pinnedMessages.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showPinnedMessages ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
        
        <!-- Pinned Messages List -->
        <div v-if="showPinnedMessages" class="max-h-48 overflow-y-auto">
          <div v-if="pinnedMessages.length === 0" class="p-4 text-center text-gray-500 text-sm">
            No pinned messages
          </div>
          <div 
            v-for="message in pinnedMessages" 
            :key="message.id"
            class="p-3 mx-3 mb-2 bg-amber-50 rounded-lg cursor-pointer hover:bg-amber-100 transition-all duration-200 border border-amber-200 group relative"
            @click="scrollToMessage(message.id)"
          >
            <!-- Pin icon indicator -->
            <div class="absolute top-2 right-2">
              <svg class="w-3 h-3 text-amber-600 opacity-70 group-hover:opacity-100 transition-opacity" fill="currentColor" viewBox="0 0 24 24">
                <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </div>
            <div class="flex items-start gap-2 pr-6">
              <img :src="getProfilePictureUrl(message.sender)" class="w-6 h-6 rounded-full object-cover" />
              <div class="flex-1 min-w-0">
                <p class="text-xs text-amber-700 font-medium">{{ message.sender.first_name }}</p>
                <p class="text-sm text-gray-800 line-clamp-2">{{ message.content }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ formatDate(message.timestamp) }}</p>
              </div>
            </div>
            <!-- Click indicator -->
            <div class="text-center mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <p class="text-xs text-amber-600 font-medium">Click to jump to message</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Shared Images -->
      <div class="border-b border-gray-200">
        <button 
          @click="showSharedImages = !showSharedImages"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="font-medium text-gray-900">Shared Images</span>
            <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
              {{ sharedImages.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showSharedImages ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Shared Images Grid -->
        <div v-if="showSharedImages" class="p-3">
          <div v-if="sharedImages.length === 0" class="text-center text-gray-500 text-sm py-4">
            No shared images
          </div>
          <div class="grid grid-cols-3 gap-2">
            <div 
              v-for="image in sharedImages.slice(0, 9)" 
              :key="image.id"
              class="aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer hover:opacity-80 transition-opacity"
              @click="openMedia(image)"
            >
              <img 
                :src="image.url" 
                :alt="image.name"
                class="w-full h-full object-cover"
              />
            </div>
          </div>
          <button 
            v-if="sharedImages.length > 9" 
            class="w-full mt-3 p-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
            @click="showAllImages = true"
          >
            View All ({{ sharedImages.length }})
          </button>
        </div>
      </div>

      <!-- Shared Links -->
      <div class="border-b border-gray-200">
        <button 
          @click="showSharedLinks = !showSharedLinks"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <span class="font-medium text-gray-900">Shared Links</span>
            <span class="bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded-full">
              {{ sharedLinks.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showSharedLinks ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Shared Links List -->
        <div v-if="showSharedLinks" class="max-h-48 overflow-y-auto">
          <div v-if="sharedLinks.length === 0" class="p-4 text-center text-gray-500 text-sm">
            No shared links
          </div>
          <a 
            v-for="link in sharedLinks" 
            :key="link.id"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="block p-3 mx-3 mb-2 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors"
          >
            <div class="flex items-start gap-3">
              <!-- Link preview image if available -->
              <div v-if="link.image_url" class="w-12 h-8 flex-shrink-0 rounded overflow-hidden bg-gray-200">
                <img 
                  :src="link.image_url" 
                  :alt="link.title"
                  class="w-full h-full object-cover"
                  @error="handleImageError"
                />
              </div>
              <!-- Default icon if no image -->
              <svg v-else class="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ link.title || link.url }}</p>
                <p v-if="link.description" class="text-xs text-gray-600 line-clamp-2 mt-1">{{ link.description }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <p class="text-xs text-gray-500">{{ link.domain }}</p>
                  <span class="text-xs text-gray-400">•</span>
                  <p class="text-xs text-gray-400">{{ formatDate(link.timestamp) }}</p>
                </div>
              </div>
            </div>
          </a>
        </div>
      </div>

      <!-- Shared Files -->
      <div>
        <button 
          @click="showSharedFiles = !showSharedFiles"
          class="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <span class="font-medium text-gray-900">Shared Files</span>
            <span class="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
              {{ sharedFiles.length }}
            </span>
          </div>
          <svg 
            :class="['w-4 h-4 text-gray-400 transition-transform', showSharedFiles ? 'rotate-180' : '']" 
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        <!-- Shared Files List -->
        <div v-if="showSharedFiles" class="max-h-48 overflow-y-auto">
          <div v-if="sharedFiles.length === 0" class="p-4 text-center text-gray-500 text-sm">
            No shared files
          </div>
          <div 
            v-for="file in sharedFiles" 
            :key="file.id"
            class="p-3 mx-3 mb-2 bg-orange-50 rounded-lg cursor-pointer hover:bg-orange-100 transition-colors"
            @click="downloadFile(file)"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-orange-200 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-orange-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ file.name }}</p>
                <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }} • {{ formatDate(file.timestamp) }}</p>
              </div>
              <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
    <!-- Search Messages Modal -->
    <div v-if="showSearchMessages" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50" @click.self="showSearchMessages = false">
      <div class="bg-white w-full max-w-lg rounded-lg shadow-xl overflow-hidden">
        <div class="p-4 border-b border-gray-200 flex items-center justify-between">
          <h4 class="text-base font-semibold">Search Messages</h4>
          <button @click="showSearchMessages = false" class="p-1 rounded hover:bg-gray-100">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-4">
          <div class="relative">
            <input
              v-model="messageSearchQuery"
              @keyup.enter="performMessageSearch"
              type="text"
              placeholder="Search in this conversation"
              class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
            <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <div class="mt-3 flex gap-2">
            <button @click="performMessageSearch" class="px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700">Search</button>
            <button @click="clearMessageSearch" class="px-3 py-2 border rounded text-gray-700 hover:bg-gray-50">Clear</button>
          </div>
        </div>
        <div class="border-t max-h-80 overflow-y-auto">
          <div v-if="messageSearchLoading" class="p-4 text-gray-500">Searching…</div>
          <div v-else-if="messageSearchResults.length === 0" class="p-4 text-gray-500">No results</div>
          <div v-else>
            <div
              v-for="hit in messageSearchResults"
              :key="hit.id"
              class="px-4 py-3 border-b hover:bg-gray-50 cursor-pointer"
              @click="jumpToMessage(hit.id)"
            >
              <div class="text-sm text-gray-500 flex items-center gap-2">
                <span class="font-medium">{{ hit.sender.first_name }} {{ hit.sender.last_name }}</span>
                <span>•</span>
                <span>{{ formatDate(hit.timestamp) }}</span>
              </div>
              <div class="text-gray-800 text-sm mt-1">
                {{ hit.content_snippet }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- End Search Messages Modal -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import api from '../../services/api'
import messagingService from '../../services/messaging'

// Props
const props = defineProps({
  conversation: {
    type: Object,
    required: true
  },
  messages: {
    type: Array,
    default: () => []
  },
  currentUser: {
    type: Object,
    required: true
  },
  memberRequestNotificationTrigger: {
    type: Number,
    default: 0
  },
  groupMemberUpdateTrigger: {
    type: Number,
    default: 0
  }
})

// Emits
const emit = defineEmits(['close', 'block', 'unblock', 'scroll-to-message', 'group-photo-updated', 'leave-group'])

// State
const isBlocked = ref(false)
const pinnedMessages = ref([])
const sharedImages = ref([])
const sharedLinks = ref([])
const sharedFiles = ref([])

// UI State
const showPinnedMessages = ref(true) // Start expanded for better UX
const showSharedImages = ref(false)
const showSharedLinks = ref(false)
const showSharedFiles = ref(false)
const showSearchMessages = ref(false)
const showGroupMembers = ref(false)
const showAddMemberForm = ref(false)
const showAllImages = ref(false)

// Message search state (for Search Messages modal)
const messageSearchQuery = ref('')
const messageSearchResults = ref([])
const messageSearchLoading = ref(false)

// Group management state
const groupMembers = ref([])
const availableUsers = ref([])
const memberSearchQuery = ref('')
const selectedNewMember = ref(null)
const requestMessage = ref('')
const pendingRequests = ref([])
const showPendingRequests = ref(false)
const isGroupAdmin = ref(false)

// Group photo upload refs
const groupPhotoInput = ref(null)

// Computed properties for reactive avatar URL
const currentAvatarUrl = computed(() => {
  if (props.conversation.type === 'private') {
    return getProfilePictureUrl(props.conversation.mate)
  } else {
    return getProfilePictureUrl(props.conversation.group) || '/default-group.png'
  }
})

// Helper functions
const getProfilePictureUrl = (entity) => {
  const BASE_URL = 'http://127.0.0.1:8000'
  const pic = entity?.profile_picture || entity?.group_picture
  return pic
    ? (pic.startsWith('http') ? pic : `${BASE_URL}${pic}`)
    : '/default-avatar.png'
}

const getStatusColor = (user) => {
  if (!user?.profile?.last_seen) return 'bg-gray-400'
  return isRecentlyActive(user) ? 'bg-green-500' : 'bg-gray-400'
}

const getStatusTextColor = (user) => {
  return isRecentlyActive(user) ? 'text-green-600' : 'text-gray-500'
}

const getStatusText = (user) => {
  if (!user?.profile?.last_seen) return 'Offline'
  return isRecentlyActive(user) ? 'Online' : 'Offline'
}

const isRecentlyActive = (user) => {
  if (!user?.profile?.last_seen) return false
  const lastSeen = new Date(user.profile.last_seen)
  const now = new Date()
  const diffMinutes = (now - lastSeen) / (1000 * 60)
  const isRecent = diffMinutes <= 2
  const isOnlineStatus = user.profile.status === 'online'
  return isRecent && isOnlineStatus
}

const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Group management functions
const isGroupCreator = (user) => {
  // Check if user is in the admins list (since groups use admins field instead of created_by)
  return props.conversation.group?.admins?.some(admin => admin.id === user.id) || false
}

const checkGroupAdminStatus = () => {
  if (props.conversation.type !== 'group') {
    isGroupAdmin.value = false
    return
  }
  
  // User is admin if they are in the admins list
  const admins = props.conversation.group?.admins || []
  const currentUserId = props.currentUser?.id
  
  console.log('🔥 ChatInfoPanel: Checking admin status:')
  console.log('🔥 ChatInfoPanel: Current user ID:', currentUserId)
  console.log('🔥 ChatInfoPanel: Group admins:', admins)
  console.log('🔥 ChatInfoPanel: Admin IDs:', admins.map(admin => admin.id))
  
  isGroupAdmin.value = admins.some(admin => admin.id === currentUserId) || false
  console.log('🔥 ChatInfoPanel: Final admin status:', isGroupAdmin.value)
}

// API functions
const fetchChatInfo = async () => {
  try {
    console.log('ChatInfoPanel: fetchChatInfo called')
    console.log('ChatInfoPanel: Current conversation:', props.conversation)
    console.log('ChatInfoPanel: Conversation type:', props.conversation?.type)
    console.log('ChatInfoPanel: Conversation group:', props.conversation?.group)
    
    // Check if user is blocked (only for private chats)
    if (props.conversation.type === 'private') {
      isBlocked.value = await messagingService.isUserBlocked(props.conversation.mate.id)
    }

    // For group chats, check admin status and fetch members
    if (props.conversation.type === 'group') {
      console.log('ChatInfoPanel: Group conversation detected, fetching members')
      console.log('ChatInfoPanel: Group ID:', props.conversation.group?.id)
      checkGroupAdminStatus()
      await fetchGroupMembers()
      
      // If admin, also fetch pending requests
      if (isGroupAdmin.value) {
        await fetchPendingRequests()
      }
    }

    // Fetch pinned messages
    await fetchPinnedMessages()

    // Process shared content from messages
    processSharedContent()
  } catch (error) {
    console.error('Error fetching chat info:', error)
  }
}

const fetchGroupMembers = async () => {
  try {
    if (props.conversation.type !== 'group') {
      console.log('ChatInfoPanel: Not a group conversation, type:', props.conversation.type)
      return
    }
    
    console.log('ChatInfoPanel: Fetching members for group:', props.conversation.group.id)
    console.log('ChatInfoPanel: Group data:', props.conversation.group)
    
    const { data } = await api.get(`/message/group/${props.conversation.group.id}/members/`)
    console.log('ChatInfoPanel: Raw API response:', data)
    
    // The backend returns full GroupChatSerializer data, not just {members: [...]}
    // So the members are at data.members and admins are at data.admins
    groupMembers.value = data.members || []
    
    // Update the conversation's group admin data to ensure isGroupAdmin is computed correctly
    if (props.conversation.group && data.admins) {
      props.conversation.group.admins = data.admins
      console.log('ChatInfoPanel: Updated admins data:', data.admins)
      
      // Recompute admin status after updating admin data
      checkGroupAdminStatus()
    }
    
    console.log('ChatInfoPanel: Group members fetched:', groupMembers.value.length)
    console.log('ChatInfoPanel: Members array:', groupMembers.value)
    console.log('ChatInfoPanel: Admins array:', data.admins)
  } catch (error) {
    console.error('Error fetching group members:', error)
    console.error('Error response:', error.response?.data)
    groupMembers.value = []
  }
}

const searchAvailableMembers = async () => {
  if (!memberSearchQuery.value.trim()) {
    availableUsers.value = []
    return
  }

  try {
    const { data } = await api.get(`/message/search/?q=${encodeURIComponent(memberSearchQuery.value)}`)
    // Filter out users who are already members
    const memberIds = groupMembers.value.map(member => member.id)
    availableUsers.value = (data.users || []).filter(user => !memberIds.includes(user.id))
  } catch (error) {
    console.error('Error searching users:', error)
    availableUsers.value = []
  }
}

const fetchPinnedMessages = async () => {
  try {
    // Filter pinned messages from current conversation and sort by newest first
    pinnedMessages.value = props.messages
      .filter(message => message.is_pinned)
      .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    console.log('ChatInfoPanel: Found pinned messages:', pinnedMessages.value.length)
  } catch (error) {
    console.error('Error fetching pinned messages:', error)
  }
}

const processSharedContent = () => {
  const images = []
  const links = []
  const files = []

  console.log('ChatInfoPanel: Processing shared content from messages:', props.messages.length)

  props.messages.forEach(message => {
    // Process attachments
    if (message.attachments && message.attachments.length > 0) {
      console.log('ChatInfoPanel: Processing attachments for message:', message.id, message.attachments)
      
      message.attachments.forEach(attachment => {
        console.log('ChatInfoPanel: Processing attachment:', attachment)
        
        // Build the attachment data
        const attachmentData = {
          id: attachment.id,
          url: attachment.file, // This comes from the serializer
          name: attachment.file_name || 'Unnamed file',
          type: attachment.file_type || 'application/octet-stream',
          size: attachment.file_size || 0,
          timestamp: message.timestamp,
          messageId: message.id
        }
        
        console.log('ChatInfoPanel: Built attachment data:', attachmentData)
        
        // Only images go to shared images
        if (attachment.file_type?.startsWith('image/')) {
          images.push(attachmentData)
          console.log('ChatInfoPanel: Added to images')
        } else {
          // All non-image files (PDFs, Word docs, videos, etc.) go to shared files
          files.push(attachmentData)
          console.log('ChatInfoPanel: Added to files')
        }
      })
    }

    // Extract links from message content and link previews
    const urlRegex = /(https?:\/\/[^\s]+)/g
    const matches = message.content.match(urlRegex)
    if (matches) {
      matches.forEach(url => {
        try {
          const urlObj = new URL(url)
          links.push({
            id: `${message.id}-${url}`,
            url: url,
            title: url,
            domain: urlObj.hostname,
            timestamp: message.timestamp,
            messageId: message.id
          })
        } catch (e) {
          // Invalid URL, ignore
        }
      })
    }

    // Also extract from link previews if available
    if (message.link_previews && message.link_previews.length > 0) {
      message.link_previews.forEach(preview => {
        // Check if we already added this URL from regex extraction
        const existingLink = links.find(link => link.url === preview.url)
        if (existingLink) {
          // Update existing link with richer data from preview
          existingLink.title = preview.title || preview.url
          existingLink.description = preview.description
          existingLink.image_url = preview.image_url
          existingLink.domain = preview.domain
        } else {
          // Add new link from preview
          links.push({
            id: preview.id,
            url: preview.url,
            title: preview.title || preview.url,
            description: preview.description,
            image_url: preview.image_url,
            domain: preview.domain,
            timestamp: message.timestamp,
            messageId: message.id
          })
        }
      })
    }
  })

  console.log('ChatInfoPanel: Final results - Images:', images.length, 'Files:', files.length, 'Links:', links.length)

  sharedImages.value = images.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  sharedLinks.value = links.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  sharedFiles.value = files.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  
  console.log('ChatInfoPanel: sharedImages:', sharedImages.value)
  console.log('ChatInfoPanel: sharedFiles:', sharedFiles.value)
}

// Actions
const addMemberToGroup = async (user) => {
  try {
    console.log('🔥 ChatInfoPanel: addMemberToGroup called')
    console.log('🔥 ChatInfoPanel: isGroupAdmin.value:', isGroupAdmin.value)
    console.log('🔥 ChatInfoPanel: User to add:', user)
    
    // Regular members create requests, admins add directly
    if (isGroupAdmin.value) {
      console.log('🔥 ChatInfoPanel: Admin path - adding member directly')
      // Admin: Add member directly
      const response = await api.post(`/message/group/${props.conversation.group.id}/manage/`, {
        action: 'add_member',
        user_id: user.id
      })
      
      console.log('🔥 ChatInfoPanel: Add member response:', response.data)
      
      // Check for success in response
      if (response.data && (response.data.success || response.data.message)) {
        alert(response.data.message || 'Member added successfully!')
      } else {
        alert('Member added successfully!')
      }
      
      await fetchGroupMembers()
      showAddMemberForm.value = false
      memberSearchQuery.value = ''
      availableUsers.value = []
    } else {
      console.log('🔥 ChatInfoPanel: Regular member path - creating request')
      // Regular member: Create a request
      await createMemberRequest(user.id)
    }
  } catch (error) {
    console.error('Error adding member:', error)
    alert('Failed to add member')
  }
}

const createMemberRequest = async (userId) => {
  try {
    const requestData = {
      user_id: userId,
      message: requestMessage.value.trim()
    }
    
    await api.post(`/message/group/${props.conversation.group.id}/member-requests/`, requestData)
    
    alert('Member request sent to admins for approval!')
    showAddMemberForm.value = false
    memberSearchQuery.value = ''
    requestMessage.value = ''
    availableUsers.value = []
    selectedNewMember.value = null
  } catch (error) {
    console.error('Error creating member request:', error)
    if (error.response?.data?.error) {
      alert(error.response.data.error)
    } else {
      alert('Failed to send member request')
    }
  }
}

const fetchPendingRequests = async () => {
  try {
    if (!isGroupAdmin.value) return
    
    const { data } = await api.get(`/message/group/${props.conversation.group.id}/member-requests/`)
    pendingRequests.value = data
    console.log('Pending requests fetched:', pendingRequests.value.length)
  } catch (error) {
    console.error('Error fetching pending requests:', error)
    pendingRequests.value = []
  }
}

const handleMemberRequest = async (requestId, action, adminResponse = '') => {
  try {
    const requestData = {
      action, // 'approve' or 'reject'
      admin_response: adminResponse
    }
    
    await api.post(`/message/member-request/${requestId}/manage/`, requestData)
    
    alert(`Request ${action}d successfully!`)
    await fetchPendingRequests()
    await fetchGroupMembers() // Refresh members if approved
  } catch (error) {
    console.error(`Error ${action}ing request:`, error)
    alert(`Failed to ${action} request`)
  }
}

const cancelAddMember = () => {
  showAddMemberForm.value = false
  memberSearchQuery.value = ''
  requestMessage.value = ''
  availableUsers.value = []
}

// Group photo upload functions
const triggerGroupPhotoUpload = () => {
  groupPhotoInput.value?.click()
}

const handleGroupPhotoUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('group_picture', file)
    formData.append('action', 'update_picture')

    console.log('Uploading group photo for group:', props.conversation.group.id)
    
    const response = await api.post(`/message/group/${props.conversation.group.id}/manage/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    console.log('Group photo updated successfully:', response.data)
    
    // Emit event to parent to update the conversation list and current conversation
    if (response.data.group_picture) {
      emit('group-photo-updated', {
        groupId: props.conversation.group.id,
        newPhotoUrl: response.data.group_picture
      })
      
      // Force reactivity update
      await nextTick()
    }
    
    // Reset the file input
    event.target.value = ''
    
  } catch (error) {
    console.error('Error uploading group photo:', error)
  }
}

const removeMember = async (member) => {
  if (!confirm(`Remove ${member.first_name} ${member.last_name} from the group?`)) {
    return
  }

  try {
    const response = await api.post(`/message/group/${props.conversation.group.id}/manage/`, {
      action: 'remove_member',
      user_id: member.id
    })
    
    console.log('Remove member response:', response.data)
    
    // Check for success in response
    if (response.data && (response.data.success || response.data.message)) {
      alert(response.data.message || 'Member removed successfully!')
    } else {
      alert('Member removed successfully!')
    }
    
    // Refresh members list
    await fetchGroupMembers()
    
    console.log('Member removed successfully:', member.first_name, member.last_name)
  } catch (error) {
    console.error('Error removing member:', error)
    alert('Failed to remove member')
  }
}

const leaveGroup = async () => {
  if (!confirm('Are you sure you want to leave this group? You will no longer receive messages from this group.')) {
    return
  }

  try {
    console.log('Attempting to leave group:', props.conversation.group.id)
    console.log('Group data:', props.conversation.group)
    console.log('Current user:', props.currentUser)
    
    const response = await api.post(`/message/group/${props.conversation.group.id}/manage/`, {
      action: 'leave_group'
    })
    
    console.log('Left group successfully:', response.data)
    
    // Emit event to parent to handle UI updates (close chat, remove from list)
    emit('leave-group', {
      groupId: props.conversation.group.id,
      groupName: props.conversation.group.name
    })
    
  } catch (error) {
    console.error('Error leaving group:', error)
    console.error('Error response:', error.response?.data)
    console.error('Error status:', error.response?.status)
    alert(`Failed to leave group: ${error.response?.data?.error || error.message}`)
  }
}

const toggleBlock = async () => {
  if (props.conversation.type !== 'private') return

  try {
    if (isBlocked.value) {
      // Unblock
      await messagingService.unblockUser(props.conversation.mate.id)
      isBlocked.value = false
      emit('unblock')
      console.log('User unblocked successfully')
    } else {
      // Block
      await messagingService.blockUser(props.conversation.mate.id)
      isBlocked.value = true
      emit('block')
      console.log('User blocked successfully')
    }
  } catch (error) {
    console.error('Error toggling block:', error)
    // Show user-friendly error message
    const message = error.response?.data?.error || 'Failed to update block status'
    alert(message) // You can replace this with a toast notification
  }
}

const scrollToMessage = (messageId) => {
  // Emit event to parent to scroll to message
  console.log('ChatInfoPanel: Emitting scroll-to-message for:', messageId)
  emit('scroll-to-message', messageId)
}

const openMedia = (media) => {
  // Open media in full screen or new tab
  window.open(media.url, '_blank')
}

const downloadFile = (file) => {
  // Download file
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Search messages within current conversation
async function performMessageSearch() {
  const q = messageSearchQuery.value.trim()
  if (!q) {
    messageSearchResults.value = []
    return
  }
  try {
    messageSearchLoading.value = true
    const scope = props.conversation.type === 'group' ? 'group' : 'private'
    const id = scope === 'group' ? props.conversation.group?.id : props.conversation.mate?.id
    const { data } = await api.get('/message/search/messages/', { params: { scope, id, q } })
    messageSearchResults.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.error('Message search failed', e)
    messageSearchResults.value = []
  } finally {
    messageSearchLoading.value = false
  }
}

function clearMessageSearch() {
  messageSearchQuery.value = ''
  messageSearchResults.value = []
}

function jumpToMessage(messageId) {
  emit('scroll-to-message', messageId)
  showSearchMessages.value = false
}

// Watchers
watch(() => props.conversation, (newConversation) => {
  if (newConversation) {
    // Reset inline states
    showAddMemberForm.value = false
    memberSearchQuery.value = ''
    availableUsers.value = []
    
    fetchChatInfo()
  }
}, { immediate: true })

watch(() => props.messages, () => {
  processSharedContent()
  fetchPinnedMessages()
}, { deep: true })

// Watch for member search query changes
watch(memberSearchQuery, () => {
  if (memberSearchQuery.value.length >= 2) {
    searchAvailableMembers()
  } else {
    availableUsers.value = []
  }
})

// Watch for real-time member request notifications
watch(() => props.memberRequestNotificationTrigger, (newVal, oldVal) => {
  if (newVal > oldVal && props.conversation?.type === 'group' && isGroupAdmin.value) {
    console.log('🔔 ChatInfoPanel: Real-time member request notification, refreshing pending requests')
    fetchPendingRequests()
  }
})

// Watch for real-time group member updates
watch(() => props.groupMemberUpdateTrigger, (newVal, oldVal) => {
  if (newVal > oldVal && props.conversation?.type === 'group') {
    console.log('🔔 ChatInfoPanel: Real-time group member update, refreshing members')
    fetchChatInfo()
  }
})

// Handle image loading errors for link previews
const handleImageError = (event) => {
  event.target.style.display = 'none'
}

// Lifecycle
onMounted(() => {
  fetchChatInfo()
})
</script>

<style scoped>
.line-clamp-2 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

/* Custom scrollbar styling for chat info panel */
.chat-info-scroll::-webkit-scrollbar {
  width: 8px;
}

.chat-info-scroll::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-info-scroll::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.chat-info-scroll::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* For Firefox */
.chat-info-scroll {
  scrollbar-width: thin;
  scrollbar-color: #c1c1c1 #f1f1f1;
}
</style>