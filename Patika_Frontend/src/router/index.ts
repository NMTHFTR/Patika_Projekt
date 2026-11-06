import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// @ts-ignore
import Leltar from '../views/Leltar.vue'
import ProjectDetailsView from '../views/ProjectDetailsView.vue'


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
    },

    {
      path: '/inventory/:id',
      name: 'project-details',
      component: ProjectDetailsView
    }


  ]
})

export default router
