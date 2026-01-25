import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../utils/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('mobile_token') || '')
  const userInfo = ref(null)
  const employeeInfo = ref(null)
  const userNotFound = ref(false)  // 用户不存在标识

  const isLoggedIn = computed(() => !!token.value)
  const onboardStatus = computed(() => employeeInfo.value?.onboard_status || 'pending')

  // 检查登录状态
  async function checkAuth() {
    if (!token.value) return false
    
    try {
      const res = await api.get('/api/auth/me/')
      if (res.data.authenticated) {
        userInfo.value = res.data.user
        // 获取完整的员工信息
        const profileResult = await fetchProfile()
        if (!profileResult) {
          // 用户不存在
          return false
        }
        return true
      }
    } catch (e) {
      logout()
    }
    return false
  }

  // 登录
  async function login(credentials) {
    const res = await api.post('/api/auth/token/', credentials)
    token.value = res.data.access
    localStorage.setItem('mobile_token', res.data.access)
    localStorage.setItem('mobile_refresh_token', res.data.refresh)
    await checkAuth()
    return res.data
  }

  // 注册
  async function register(data) {
    const res = await api.post('/api/onboarding/register/', data)
    if (res.data.success) {
      token.value = res.data.data.access
      localStorage.setItem('mobile_token', res.data.data.access)
      localStorage.setItem('mobile_refresh_token', res.data.data.refresh)
      employeeInfo.value = {
        employee_id: res.data.data.employee_id,
        name: res.data.data.name,
        onboard_status: res.data.data.onboard_status,
      }
    }
    return res.data
  }

  // 获取入职状态
  async function fetchOnboardStatus() {
    try {
      const res = await api.get('/api/onboarding/status/')
      if (res.data.success) {
        userNotFound.value = false
        const data = res.data.data
        employeeInfo.value = {
          ...employeeInfo.value,
          ...data,
          // 将 API 返回的 status 映射到 onboard_status
          onboard_status: data.status || data.onboard_status || 'pending',
        }
      } else if (res.data.error?.code === 'not_found') {
        userNotFound.value = true
        employeeInfo.value = null
      }
    } catch (e) {
      if (e.response?.status === 404 || e.response?.data?.error?.code === 'not_found') {
        userNotFound.value = true
        employeeInfo.value = null
      } else {
        console.error('获取入职状态失败', e)
      }
    }
  }

  // 获取个人资料
  async function fetchProfile() {
    try {
      const res = await api.get('/api/onboarding/profile/')
      if (res.data.success) {
        userNotFound.value = false
        const data = res.data.data
        employeeInfo.value = {
          ...data,
          // 将 onboard_reject_reason 映射为 reject_reason 供前端使用
          reject_reason: data.onboard_reject_reason || '',
        }
        return res.data
      } else if (res.data.error?.code === 'not_found') {
        userNotFound.value = true
        employeeInfo.value = null
        return null
      }
    } catch (e) {
      if (e.response?.status === 404 || e.response?.data?.error?.code === 'not_found') {
        userNotFound.value = true
        employeeInfo.value = null
        return null
      }
      console.error('获取个人资料失败', e)
    }
    return null
  }

  // 更新个人资料
  async function updateProfile(data) {
    const res = await api.post('/api/onboarding/profile/', data)
    if (res.data.success) {
      await fetchProfile()
    }
    return res.data
  }

  // 退出登录
  function logout() {
    token.value = ''
    userInfo.value = null
    employeeInfo.value = null
    userNotFound.value = false
    localStorage.removeItem('mobile_token')
    localStorage.removeItem('mobile_refresh_token')
  }

  return {
    token,
    userInfo,
    employeeInfo,
    userNotFound,
    isLoggedIn,
    onboardStatus,
    checkAuth,
    login,
    register,
    fetchOnboardStatus,
    fetchProfile,
    updateProfile,
    logout,
  }
})
