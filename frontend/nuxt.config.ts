// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },

  // 应用配置
  app: {
    head: {
      title: 'AI智能体平台',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'AI智能体平台 - 提供AI短视频生成、知识库管理、智能客服等服务' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  // 开发服务器
  devServer: {
    port: 5173,
    host: '127.0.0.1'
  },

  // 模块
  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@element-plus/nuxt',
    '@vueuse/nuxt'
  ],

  // 自动导入
  imports: {
    dirs: ['composables', 'stores']
  },

  // CSS
  css: [
    '~/assets/css/main.scss'
  ],

  // 运行时配置
  runtimeConfig: {
    // 服务端私有配置
    apiBase: process.env.API_BASE_URL || 'http://localhost:8000',

    // 客户端公开配置
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000'
    }
  },

  // Nitro 服务器配置
  nitro: {
    experimental: {
      wasm: true
    }
  },

  // 构建配置
  build: {
    transpile: ['element-plus']
  },

  // Vite 配置
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `
            @use "@/assets/css/variables.scss" as *;
          `
        }
      }
    }
  }
})
