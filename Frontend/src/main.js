import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { useAuthStore } from './stores/auth';
import { useThemeStore } from './stores/theme';
import { useUiStore } from './stores/ui';

// Clear any old dark mode settings from localStorage
localStorage.removeItem('darkMode');

// Remove dark class from document if it exists
document.documentElement.classList.remove('dark');

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

app.mount('#app');

// Initialize stores after app is mounted
const auth = useAuthStore();
const theme = useThemeStore();

// Initialize theme store
theme.initializeTheme();
theme.initializeAdminTheme();

// Initialize auth store
if (auth.token) {
  const ui = useUiStore();
  ui.start('Loading user...');
  auth.fetchUser().catch(() => {}).finally(() => ui.stop());
}
