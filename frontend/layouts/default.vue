<script setup lang="ts">
import {
  DataLine,
  User as UserIcon,
  Star,
  SwitchButton
} from '@element-plus/icons-vue'

const userStore = useUserStore()
const route = useRoute()

// 将图标注册到组件中，供模板使用
const icons = {
  DataLine,
  UserIcon,
  Star,
  SwitchButton
}

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 页面加载时检查登录状态
onMounted(async () => {
  if (userStore.token && !userStore.user) {
    await userStore.checkAuth()
  }
})
</script>

<template>
  <div class="layout">
    <!-- 顶部导航栏 -->
    <el-header class="header">
      <div class="header-inner">
        <!-- Logo -->
        <div class="logo" @click="navigateTo('/')">
          <h1>AI智能体平台</h1>
        </div>

        <!-- 导航菜单 -->
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          class="nav-menu"
        >
          <el-menu-item index="/" @click="navigateTo('/')">
            首页
          </el-menu-item>
          <el-menu-item index="/video" @click="navigateTo('/video')">
            AI视频
          </el-menu-item>
          <el-menu-item index="/knowledge" @click="navigateTo('/knowledge')">
            知识库
          </el-menu-item>
        </el-menu>

        <!-- 用户区域 -->
        <div class="user-area">
          <template v-if="userStore.isLoggedIn">
            <!-- 配额显示 -->
            <el-tooltip content="今日配额">
              <div class="quota-info">
                <el-icon :size="18"><component :is="icons.DataLine" /></el-icon>
                <span>{{ userStore.quotaInfo.used }}/{{ userStore.quotaInfo.daily === -1 ? '无限' : userStore.quotaInfo.daily }}</span>
              </div>
            </el-tooltip>

            <!-- 用户下拉菜单 -->
            <el-dropdown>
              <div class="user-dropdown">
                <el-avatar :size="32" :src="userStore.user?.avatar">
                  {{ userStore.user?.username?.charAt(0).toUpperCase() }}
                </el-avatar>
                <span class="username">{{ userStore.user?.username }}</span>
                <el-tag v-if="userStore.isPremium" type="warning" size="small">VIP</el-tag>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="navigateTo('/profile')">
                    <el-icon><component :is="icons.UserIcon" /></el-icon>
                    个人中心
                  </el-dropdown-item>
                  <el-dropdown-item @click="navigateTo('/membership')">
                    <el-icon><component :is="icons.Star" /></el-icon>
                    会员中心
                  </el-dropdown-item>
                  <el-dropdown-item divided @click="userStore.logout()">
                    <el-icon><component :is="icons.SwitchButton" /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="navigateTo('/login')">
              登录 / 注册
            </el-button>
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主要内容区域 -->
    <el-main class="main-content">
      <slot />
    </el-main>

    <!-- 页脚 -->
    <el-footer class="footer">
      <div class="footer-inner">
        <p>&copy; 2026 AI智能体平台. All rights reserved.</p>
      </div>
    </el-footer>
  </div>
</template>

<style scoped lang="scss">
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 0;
  height: 60px;
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  gap: 40px;
}

.logo {
  cursor: pointer;
  flex-shrink: 0;

  h1 {
    font-size: 20px;
    font-weight: 600;
    color: var(--el-color-primary);
    margin: 0;
  }
}

.nav-menu {
  flex: 1;
  border: none;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

.quota-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
  cursor: help;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;

  .username {
    font-size: 14px;
    max-width: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.main-content {
  flex: 1;
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.footer {
  background: var(--el-bg-color-page);
  border-top: 1px solid var(--el-border-color-lighter);
  height: auto;
  padding: 20px 0;
}

.footer-inner {
  text-align: center;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}
</style>
