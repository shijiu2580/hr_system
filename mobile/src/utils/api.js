import axios from 'axios'
import { showToast } from 'vant'

const api = axios.create({
  baseURL: '',
  timeout: 15000,
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('mobile_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const { response } = error
    
    if (response) {
      switch (response.status) {
        case 401:
          // Token 过期，尝试刷新
          const refreshToken = localStorage.getItem('mobile_refresh_token')
          if (refreshToken) {
            try {
              const res = await axios.post('/api/auth/token/refresh/', {
                refresh: refreshToken
              })
              localStorage.setItem('mobile_token', res.data.access)
              // 重试原请求
              error.config.headers.Authorization = `Bearer ${res.data.access}`
              return api(error.config)
            } catch (e) {
              // 刷新失败，清除登录状态
              localStorage.removeItem('mobile_token')
              localStorage.removeItem('mobile_refresh_token')
              window.location.href = '/login'
            }
          } else {
            window.location.href = '/login'
          }
          break
        case 403:
          showToast('没有权限')
          break
        case 404:
          showToast('请求的资源不存在')
          break
        case 500:
          showToast('服务器错误')
          break
        default:
          showToast(response.data?.error?.message || response.data?.detail || '请求失败')
      }
    } else {
      showToast('网络连接失败')
    }
    
    return Promise.reject(error)
  }
)

export default api
