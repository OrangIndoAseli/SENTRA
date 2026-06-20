import { createRouter, createWebHistory } from 'vue-router'

import Dashboard from '../pages/Dashboard.vue'
import Monitoring from '../pages/Monitoring.vue'
import Violations from '../pages/Violations.vue'
import DangerZone from '../pages/DangerZone.vue'
import Logs from '../pages/Logs.vue'

const routes = [
  {
    path: '/',
    component: Dashboard
  },
  {
    path: '/monitoring',
    component: Monitoring
  },
  {
    path: '/violations',
    component: Violations
  },
  {
    path: '/danger-zone',
    component: DangerZone
  },
  {
    path: '/logs',
    component: Logs
  }
]

export default createRouter({
  history: createWebHistory(),
  routes
})