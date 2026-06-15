import { createRouter, createWebHashHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/predict', name: 'predict', component: () => import('../views/PredictorView.vue') },
    { path: '/groups', name: 'groups', component: () => import('../views/GroupsView.vue') },
    { path: '/bracket', name: 'bracket', component: () => import('../views/BracketView.vue') },
    { path: '/teams', name: 'teams', component: () => import('../views/TeamsView.vue') },
    { path: '/live', name: 'live', component: () => import('../views/LiveView.vue') },
    { path: '/accuracy', name: 'accuracy', component: () => import('../views/AccuracyView.vue') },
  ],
})

export default router
