import { createRouter, createWebHistory } from 'vue-router'
import CalculatorView from '../views/CalculatorView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'calculator',
      component: CalculatorView,
    },
    // Single-page app: send any unknown path back to the calculator
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
