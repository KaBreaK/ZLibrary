import { createRouter, createWebHistory } from 'vue-router';
import Ustawienia from './views/Ustawienia.vue';
import Ulubione from './views/Ulubione.vue'; // Zakładam, że masz ten widok\
import Glowna from "@/views/Glowna.vue";

const routes = [
  {
    path: '/glowna',
    redirect: 'glowna', // Przekierowanie na domyślną stronę
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
  // inne ścieżki
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
