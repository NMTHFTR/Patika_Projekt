import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// @ts-ignore
import Leltar from '../views/Leltar.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },

    {
      path: '/inventory',
      name: 'inventory',
      component: Leltar
    }
  ]
})

export default router
