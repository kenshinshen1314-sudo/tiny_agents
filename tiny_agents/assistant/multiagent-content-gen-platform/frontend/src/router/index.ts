import { createRouter, createWebHistory } from 'vue-router';
import Home from '../views/Home.vue';
import ResearchProcess from '../views/ResearchProcess.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home,
  },
  {
    path: '/research',
    name: 'research',
    component: ResearchProcess,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;