import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router';

createApp(App).mount('#app')

App.use(router);
App.mount('#app');
// ...existing code.
