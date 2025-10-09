<script setup>
import { computed } from 'vue'
import { 
  User as UserIcon,
  Shield as ShieldIcon,
  Palette as PaletteIcon,
  Lock as LockIcon,
  Bell as BellIcon,
  ChevronLeft as ChevronLeftIcon
} from 'lucide-vue-next'

// Props
const props = defineProps({
  activeSection: {
    type: String,
    required: true
  },
  sidebarExpanded: {
    type: Boolean,
    default: false
  },
  hoverDisabled: {
    type: Boolean,
    default: false
  },
  themeStore: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['section-change', 'sidebar-toggle', 'sidebar-expand'])

// Settings sections configuration
const sections = [
  { 
    id: 'profile', 
    label: 'Profile Settings', 
    icon: UserIcon,
    description: 'Personal information and profile picture'
  },
  { 
    id: 'account', 
    label: 'Account & Security', 
    icon: ShieldIcon,
    description: 'Password, 2FA, and security settings'
  },
  { 
    id: 'appearance', 
    label: 'Appearance', 
    icon: PaletteIcon,
    description: 'Theme, colors, and visual preferences'
  },
  { 
    id: 'privacy', 
    label: 'Privacy Settings', 
    icon: LockIcon,
    description: 'Control your privacy and visibility'
  },
  { 
    id: 'notifications', 
    label: 'Notifications', 
    icon: BellIcon,
    description: 'Email and push notification preferences'
  }
]

// Computed
const currentSection = computed(() => 
  sections.find(section => section.id === props.activeSection)
)

// Methods
const onSectionChange = (sectionId) => {
  emit('section-change', sectionId)
}

const onToggleSidebar = () => {
  emit('sidebar-toggle')
}

const onExpandSidebar = () => {
  if (!props.hoverDisabled) {
    emit('sidebar-expand')
  }
}
</script>

<template>
  <div
    :class="sidebarExpanded ? 'w-64' : 'w-16'"
    class="flex-shrink-0 transition-all duration-500 ease-out group"
    @mouseenter="onExpandSidebar">
    
    <div class="sticky top-6 py-2">
      <nav class="space-y-2">
        <!-- Navigation Items -->
        <button
          v-for="section in sections"
          :key="section.id"
          @click="onSectionChange(section.id)"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition-all duration-300 ease-out hover:scale-[1.02] active:scale-98 relative overflow-hidden hover:shadow-md group/item"
          :class="activeSection === section.id
            ? (themeStore.isDarkMode ? 'bg-blue-600 text-white shadow-lg' : 'bg-blue-600 text-white shadow-lg')
            : (themeStore.isDarkMode ? 'text-gray-300 hover:bg-gray-800/50' : 'text-gray-700 hover:bg-gray-100/80')
          ">
          
          <!-- Icon - always visible -->
          <component 
            :is="section.icon" 
            class="w-5 h-5 flex-shrink-0 transition-transform duration-300 ease-out"
            :class="sidebarExpanded ? 'group-hover/item:scale-110' : ''" />
          
          <!-- Label - visible when expanded -->
          <div v-if="sidebarExpanded" class="flex-1 min-w-0">
            <span class="font-medium whitespace-nowrap transition-all duration-400 ease-out block">
              {{ section.label }}
            </span>
            <!-- Description - only shown on hover or when active -->
            <span 
              v-if="activeSection === section.id || sidebarExpanded"
              class="text-xs opacity-75 whitespace-nowrap block transition-all duration-300"
              :class="activeSection === section.id ? 'text-blue-100' : (themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500')">
              {{ section.description }}
            </span>
          </div>

          <!-- Active indicator -->
          <div 
            v-if="activeSection === section.id"
            class="absolute left-0 top-0 bottom-0 w-1 bg-white rounded-r-full"></div>
        </button>
      </nav>

      <!-- Collapse Button - Only visible when expanded -->
      <div v-if="sidebarExpanded" class="flex justify-start mt-6">
        <button
          @click.stop="onToggleSidebar"
          class="flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 hover:scale-105 relative z-10 cursor-pointer select-none"
          :class="themeStore.isDarkMode ? 'text-gray-400 hover:text-white hover:bg-gray-700' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'"
          type="button"
          style="pointer-events: auto;">
          <ChevronLeftIcon class="w-4 h-4 transform transition-transform duration-200 pointer-events-none" />
          <span class="text-sm font-medium pointer-events-none">Collapse</span>
        </button>
      </div>

      <!-- Breadcrumb when collapsed -->
      <div v-if="!sidebarExpanded && currentSection" class="mt-6 px-2">
        <div class="text-center">
          <p class="text-xs font-medium transform -rotate-90 whitespace-nowrap"
             :class="themeStore.isDarkMode ? 'text-gray-400' : 'text-gray-500'">
            {{ currentSection.label }}
          </p>
        </div>
      </div>
    </div>

    <!-- Tooltip for collapsed state -->
    <div v-if="!sidebarExpanded" class="absolute left-full ml-2 top-0 w-64 pointer-events-none">
      <!-- Tooltips would be rendered here when hovering over icons -->
    </div>
  </div>
</template>

<style scoped>
/* Custom styles for smooth transitions */
.group:hover .group-hover\:scale-110 {
  transform: scale(1.1);
}

/* Smooth width transitions */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
}

/* Custom easing for sidebar */
.ease-out {
  transition-timing-function: cubic-bezier(0, 0, 0.2, 1);
}

/* Prevent text selection on interactive elements */
.select-none {
  user-select: none;
}

/* Ensure pointer events work properly */
button {
  pointer-events: auto;
}
</style>