import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { useAuthStore } from './stores/auth';
import { useThemeStore } from './stores/theme';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

app.mount('#app');

// Initialize stores after app is mounted
const auth = useAuthStore();
const theme = useThemeStore();

// Initialize theme
theme.initializeTheme();

// Initialize auth store if token exists
if (auth.token) {
  auth.fetchUser();
}
