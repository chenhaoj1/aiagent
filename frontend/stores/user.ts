/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import type { User } from '~/utils/api'

interface UserState {
  user: User | null
  token: string | null
  isLoggedIn: boolean
}

// 客户端存储辅助函数
const getToken = (): string | null => {
  if (process.client) {
    return localStorage.getItem('access_token')
  }
  return null
}

const setToken = (token: string) => {
  if (process.client) {
    localStorage.setItem('access_token', token)
  }
}

const removeToken = () => {
  if (process.client) {
    localStorage.removeItem('access_token')
  }
}

const getUser = (): User | null => {
  if (process.client) {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        return JSON.parse(userStr)
      } catch {
        return null
      }
    }
  }
  return null
}

const setUser = (user: User) => {
  if (process.client) {
    localStorage.setItem('user', JSON.stringify(user))
  }
}

const removeUser = () => {
  if (process.client) {
    localStorage.removeItem('user')
  }
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    user: null,
    token: getToken(),
    isLoggedIn: !!getToken()
  }),

  getters: {
    // 当前用户
    currentUser: (state) => state.user,

    // 是否是付费会员
    isPremium: (state) => state.user?.membership_type !== 'free',

    // 会员类型
    membershipType: (state) => state.user?.membership_type || 'free',

    // 配额信息
    quotaInfo: (state) => ({
      daily: state.user?.daily_quota || 0,
      used: state.user?.used_quota || 0,
      remaining: Math.max(0, (state.user?.daily_quota || 0) - (state.user?.used_quota || 0))
    })
  },

  actions: {
    // 设置 token
    setToken(token: string) {
      this.token = token
      this.isLoggedIn = true
      setToken(token)
    },

    // 设置用户信息
    setUser(user: User) {
      this.user = user
      setUser(user)
    },

    // 登录
    async login(username: string, password: string) {
      const { authApi } = await import('~/utils/api')
      const response = await authApi.login({ username, password })
      this.setToken(response.access_token)
      this.setUser(response.user)
      return response
    },

    // 注册
    async register(data: any) {
      const { authApi } = await import('~/utils/api')
      const response = await authApi.register(data)
      this.setToken(response.access_token)
      this.setUser(response.user)
      return response
    },

    // 获取用户信息
    async fetchUser() {
      const { authApi } = await import('~/utils/api')
      const user = await authApi.getCurrentUser()
      this.setUser(user)
      return user
    },

    // 登出
    logout() {
      this.user = null
      this.token = null
      this.isLoggedIn = false
      removeToken()
      removeUser()
      navigateTo('/login')
    },

    // 检查登录状态
    async checkAuth() {
      if (!this.token) {
        return false
      }
      try {
        await this.fetchUser()
        return true
      } catch {
        this.logout()
        return false
      }
    }
  }
})
