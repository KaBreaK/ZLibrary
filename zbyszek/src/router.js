import { createRouter, createWebHistory } from 'vue-router';
import Ustawienia from './views/Ustawienia.vue';
import Ulubione from './views/Ulubione.vue';
import Glowna from "./views/Glowna.vue";
import Users from "./views/Users.vue";

const routes = [
  {
    path: '/', // Ścieżka główna
    name: 'glowna', // Dodanie nazwy 'glowna'
    component: Glowna
  },
  {
    path: '/ustawienia',
    name: 'ustawienia',
    component: Ustawienia
  },
  {
    path: '/ulubione',
    name: 'ulubione',
    component: Ulubione
  },
  {
    path: '/users',
    name: 'users',
    component: Users
  },
  // inne ścieżki
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
