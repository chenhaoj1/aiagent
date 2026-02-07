/**
 * API 请求工具
 */
import axios from 'axios'

// 创建 axios 实例
// 使用运行时配置获取 API 地址
const getBaseURL = () => {
  // @ts-ignore
  if (import.meta.client) {
    // @ts-ignore
    return useRuntimeConfig().public.apiBase || 'http://localhost:8000/api/v1'
  }
  // @ts-ignore
  return process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
}

const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 只在客户端添加 token
    // @ts-ignore
    if (import.meta.client) {
      // @ts-ignore
      const token = localStorage.getItem('access_token')
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 401 未授权，只在客户端跳转登录
    // @ts-ignore
    if (error.response?.status === 401 && import.meta.client) {
      // @ts-ignore
      localStorage.removeItem('access_token')
      // @ts-ignore
      localStorage.removeItem('user')
      // @ts-ignore
      window.location.href = '/login'
    }

    return Promise.reject(error)
  }
)

export default apiClient
