import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { useAuthStore } from './stores/auth';
import { useDarkModeStore } from './stores/darkMode';

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);

// Initialize dark mode
const darkModeStore = useDarkModeStore();
darkModeStore.initializeDarkMode();

const auth = useAuthStore();
if (auth.token) {
  auth.fetchUser();
}

app.mount('#app');
