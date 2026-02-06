<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>{{ isLogin ? '登录' : '注册' }}</h1>
        <p>AI智能体平台</p>
      </div>

      <!-- 错误提示 -->
      <el-alert
        v-if="errorMessage"
        :title="errorMessage"
        type="error"
        :closable="true"
        @close="errorMessage = ''"
        style="margin-bottom: 20px"
      />

      <el-tabs v-model="activeTab" class="login-tabs">
        <!-- 登录表单 -->
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名/邮箱/手机号"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="submit-btn"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>

            <div class="form-footer">
              <span>还没有账号？</span>
              <el-link type="primary" @click="activeTab = 'register'">
                立即注册
              </el-link>
            </div>
          </el-form>
        </el-tab-pane>

        <!-- 注册表单 -->
        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
            @submit.prevent="handleRegister"
          >
            <el-form-item prop="username">
              <el-input
                v-model="registerForm.username"
                placeholder="用户名（3-50字符）"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="email">
              <el-input
                v-model="registerForm.email"
                placeholder="邮箱（可选）"
                size="large"
                clearable
              >
                <template #prefix>
                  <el-icon><Message /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="密码（至少6位）"
                size="large"
                show-password
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item prop="confirm_password">
              <el-input
                v-model="registerForm.confirm_password"
                type="password"
                placeholder="确认密码"
                size="large"
                show-password
                @keyup.enter="handleRegister"
              >
                <template #prefix>
                  <el-icon><Lock /></el-icon>
                </template>
              </el-input>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="submit-btn"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>

            <div class="form-footer">
              <span>已有账号？</span>
              <el-link type="primary" @click="activeTab = 'login'">
                立即登录
              </el-link>
            </div>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { User, Lock, Message } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useUserStore } from '~/stores/user'

definePageMeta({
  layout: false
})

const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const errorMessage = ref('')

// 登录表单
const loginFormRef = ref<FormInstance>()
const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

// 注册表单
const registerFormRef = ref<FormInstance>()
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirm_password: ''
})

const registerRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为 3-50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== registerForm.password) {
          callback(new Error('两次密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 是否登录 tab
const isLogin = computed(() => activeTab.value === 'login')

// 处理登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  errorMessage.value = ''
  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.login(loginForm.username, loginForm.password)
      // 登录成功，跳转首页
      window.location.href = '/'
    } catch (error: any) {
      console.error('登录失败:', error)
      errorMessage.value = error.response?.data?.detail || error.message || '登录失败，请检查用户名和密码'
    } finally {
      loading.value = false
    }
  })
}

// 处理注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  errorMessage.value = ''
  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await userStore.register({
        username: registerForm.username,
        email: registerForm.email || undefined,
        password: registerForm.password,
        confirm_password: registerForm.confirm_password
      })
      // 注册成功，跳转首页
      window.location.href = '/'
    } catch (error: any) {
      console.error('注册失败:', error)
      errorMessage.value = error.response?.data?.detail || error.message || '注册失败，请重试'
    } finally {
      loading.value = false
    }
  })
}

// 如果已登录，跳转到首页
onMounted(() => {
  if (userStore.isLoggedIn) {
    window.location.href = '/'
  }
})
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;

  h1 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  p {
    color: var(--el-text-color-secondary);
  }
}

.login-tabs {
  :deep(.el-tabs__header) {
    margin-bottom: 24px;
  }

  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }

  :deep(.el-tabs__item) {
    font-size: 16px;
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 20px;
  }

  .submit-btn {
    width: 100%;
  }
}

.form-footer {
  text-align: center;
  margin-top: 20px;
  color: var(--el-text-color-secondary);
}
</style>
