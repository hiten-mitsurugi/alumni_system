import { defineStore } from 'pinia';

export const useUiStore = defineStore('ui', {
  state: () => ({
    isLoading: false,
    message: 'Loading...',
  }),
  actions: {
    start(message = 'Loading...') {
      this.message = message;
      this.isLoading = true;
    },
    stop() {
      this.isLoading = false;
      this.message = 'Loading...';
    }
  }
});

export default useUiStore;
