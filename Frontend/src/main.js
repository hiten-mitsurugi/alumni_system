import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { useAuthStore } from './stores/auth';
import { useThemeStore } from './stores/theme';
import { useUiStore } from './stores/ui';

// Clear any old dark mode settings from localStorage ONLY if they're the old format
const oldDarkMode = localStorage.getItem('darkMode');
if (oldDarkMode) {
  localStorage.removeItem('darkMode');
}

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

app.mount('#app');

// Initialize stores after app is mounted
const auth = useAuthStore();
const theme = useThemeStore();

// Initialize theme store - sync reactive state with DOM
console.log('🚀 Initializing theme store after Vue mount')
theme.initializeTheme();
theme.initializeAdminTheme();

// Initialize auth store
if (auth.token) {
  const ui = useUiStore();
  ui.start('Loading user...');
  auth.fetchUser().catch(() => {}).finally(() => ui.stop());
}
