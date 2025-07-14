import { createRouter, createWebHistory } from 'vue-router';

import ConnectMuse from "../views/ConnectMuse.vue"

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/ConnectMuse.vue'), // Replace with your actual Home component if needed
  },
  // Add more routes here as needed
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

export default router;
