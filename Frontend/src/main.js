import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { useAuthStore } from './stores/auth';

// Clear any dark mode settings from localStorage
localStorage.removeItem('darkMode');

// Remove dark class from document if it exists
document.documentElement.classList.remove('dark');

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

app.mount('#app');

// Initialize auth store after app is mounted
const auth = useAuthStore();
if (auth.token) {
  auth.fetchUser();
}
