import { createRouter, createWebHistory } from 'vue-router'
import Ustawienia from '@/views/Ustawienia.vue' // Upewnij się, że ścieżka jest poprawna

const routes = [
  {
    path: '/ustawienia',
    name: 'Ustawienia',
    component: Ustawienia
  }
  // Inne trasy...
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
