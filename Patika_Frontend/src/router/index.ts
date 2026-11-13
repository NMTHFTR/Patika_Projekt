import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
// @ts-ignore
import Leltar from '../views/Leltar.vue'
// @ts-ignore
import ProjectDetailsView from '../views/ProjectDetailsView.vue'
import NewProductTypeView from '../views/NewProductTypeView.vue'


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
    },

    {
      path: '/add-product-type',
      name: 'add-product-type',
      component: NewProductTypeView
    }


  ]
})

export default router
