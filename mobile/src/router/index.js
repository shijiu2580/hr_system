import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    redirect: '/welcome'
  },
  {
    path: '/welcome',
    name: 'Welcome',
    component: () => import('../views/Welcome.vue'),
    meta: { title: 'HR员工自助入职' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue'),
    meta: { title: '注册' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { title: '完善资料', requiresAuth: true }
  },
  {
    path: '/status',
    name: 'Status',
    component: () => import('../views/Status.vue'),
    meta: { title: '入职进度', requiresAuth: true }
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页', requiresAuth: true, requiresOnboarded: true }
  },
  {
    path: '/checkin',
    name: 'Checkin',
    component: () => import('../views/Checkin.vue'),
    meta: { title: '签到打卡', requiresAuth: true, requiresOnboarded: true }
  },
  {
    path: '/attendance',
    name: 'Attendance',
    component: () => import('../views/Attendance.vue'),
    meta: { title: '考勤记录', requiresAuth: true, requiresOnboarded: true }
  },
  {
    path: '/leave',
    name: 'Leave',
    component: () => import('../views/Leave.vue'),
    meta: { title: '请假申请', requiresAuth: true, requiresOnboarded: true }
  },
  {
    path: '/me',
    name: 'Me',
    component: () => import('../views/Me.vue'),
    meta: { title: '我的', requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 是否已初始化
let isInitialized = false

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'HR员工自助'
  
  const userStore = useUserStore()
  
  // 首次加载时，先恢复用户状态
  if (!isInitialized && userStore.token) {
    isInitialized = true
    await userStore.checkAuth()
  }
  
  // 需要登录的页面
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 需要已入职状态的页面
  if (to.meta.requiresOnboarded && userStore.onboardStatus !== 'onboarded') {
    next({ name: 'Status' })
    return
  }
  
  // 已入职员工访问入职进度页时，直接跳转首页
  if (to.name === 'Status' && userStore.onboardStatus === 'onboarded') {
    next({ name: 'Home' })
    return
  }
  
  next()
})

export default router
