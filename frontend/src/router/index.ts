import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ResultView from '../views/ResultView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/result',
      name: 'result',
      component: ResultView,
      props: () => ({ tripPlan: JSON.parse(sessionStorage.getItem('tripPlan') || '{}') })
    }
  ]
})

export default router
