import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: () => import('../pages/HomePage.vue') },
  { path: '/login', name: 'Login', component: () => import('../pages/LoginPage.vue') },
  { path: '/home', name: 'UserHome', component: () => import('../pages/HomePage.vue'), meta: { requiresAuth: true, role: 'user' } },
  { path: '/app', name: 'Workspace', component: () => import('../pages/Workspace.vue'), meta: { requiresAuth: true, role: 'user' } },
  { path: '/profile', name: 'Profile', component: () => import('../pages/ProfilePage.vue'), meta: { requiresAuth: true, role: 'user' } },
  { path: '/admin', name: 'Admin', component: () => import('../pages/AdminDashboard.vue'), meta: { requiresAuth: true, role: 'admin' } },
]

const router = createRouter({ history: createWebHistory(), routes })

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const info = sessionStorage.getItem('loginInfo')
    if (!info) return next('/login')
    const loginInfo = JSON.parse(info)
    if (to.meta.role && to.meta.role !== loginInfo.role) return next('/login')
  }
  next()
})

export default router