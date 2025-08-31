import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import { useAuthStore } from './stores/auth';

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

app.use(pinia);
app.use(router);

const auth = useAuthStore();
// Only fetch user if token exists and no user is loaded
if (auth.token && !auth.user) {
  auth.fetchUser().catch(() => {
    // If fetching user fails, logout to clear invalid token
    auth.logout();
  });
}

app.mount('#app');
