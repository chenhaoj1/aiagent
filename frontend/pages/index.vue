<template>
  <div class="home-page">
    <!-- Hero 区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          AI智能体平台
        </h1>
        <p class="hero-subtitle">
          一站式AI内容创作平台，让创意触手可及
        </p>
        <div class="hero-actions">
          <el-button
            v-if="!userStore.isLoggedIn"
            type="primary"
            size="large"
            @click="navigateTo('/login')"
          >
            立即开始
          </el-button>
          <el-button
            v-else
            type="primary"
            size="large"
            @click="navigateTo('/video')"
          >
            开始创作
          </el-button>
          <el-button
            size="large"
            @click="navigateTo('/knowledge')"
          >
            探索知识库
          </el-button>
        </div>
      </div>
    </section>

    <!-- 功能介绍 -->
    <section class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <el-card
          v-for="feature in features"
          :key="feature.title"
          class="feature-card"
          shadow="hover"
        >
          <div class="feature-icon">
            <component :is="feature.icon" />
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-desc">{{ feature.description }}</p>
        </el-card>
      </div>
    </section>

    <!-- 优势介绍 -->
    <section class="advantages-section">
      <h2 class="section-title">平台优势</h2>
      <div class="advantages-list">
        <div
          v-for="(advantage, index) in advantages"
          :key="index"
          class="advantage-item"
        >
          <div class="advantage-number">{{ String(index + 1).padStart(2, '0') }}</div>
          <div class="advantage-content">
            <h3 class="advantage-title">{{ advantage.title }}</h3>
            <p class="advantage-desc">{{ advantage.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA 区域 -->
    <section class="cta-section">
      <div class="cta-content">
        <h2>准备好开始创作了吗？</h2>
        <p>加入我们的平台，体验 AI 带来的无限可能</p>
        <el-button
          type="primary"
          size="large"
          @click="navigateTo(userStore.isLoggedIn ? '/video' : '/login')"
        >
          {{ userStore.isLoggedIn ? '立即创作' : '免费注册' }}
        </el-button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '~/stores/user'
import {
  VideoCamera,
  Document,
  ChatDotRound,
  Picture
} from '@element-plus/icons-vue'

const userStore = useUserStore()

// 功能列表
const features = [
  {
    icon: VideoCamera,
    title: 'AI 短视频生成',
    description: '输入文案，AI 自动生成专业短视频，支持多种风格和模板'
  },
  {
    icon: Document,
    title: '智能知识库',
    description: '上传文档，构建专属知识库，AI 智能问答，让知识触手可及'
  },
  {
    icon: ChatDotRound,
    title: 'AI 智能助手',
    description: '7x24小时在线，智能对话，高效解答各类问题'
  },
  {
    icon: Picture,
    title: 'AI 图片生成',
    description: '文字描述即可生成精美图片，激发创意灵感'
  }
]

// 平台优势
const advantages = [
  {
    title: '简单易用',
    description: '无需专业技能，一句话即可生成专业内容'
  },
  {
    title: '高效快捷',
    description: 'AI 自动化处理，大幅提升创作效率，节省 70% 以上时间'
  },
  {
    title: '质量保证',
    description: '采用业界领先 AI 模型，输出质量有保障'
  },
  {
    title: '持续更新',
    description: '每周更新功能，紧跟 AI 技术发展'
  }
]
</script>

<style scoped lang="scss">
.home-page {
  min-height: calc(100vh - 140px);
}

.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 100px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
}

.hero-subtitle {
  font-size: 20px;
  opacity: 0.9;
  margin-bottom: 40px;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.features-section,
.advantages-section {
  padding: 80px 20px;
}

.section-title {
  text-align: center;
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 50px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  text-align: center;
  padding: 30px;
}

.feature-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 20px;
  background: var(--el-color-primary-light-9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
  font-size: 28px;
}

.feature-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
}

.feature-desc {
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

.advantages-list {
  max-width: 800px;
  margin: 0 auto;
}

.advantage-item {
  display: flex;
  gap: 24px;
  margin-bottom: 40px;
}

.advantage-number {
  flex-shrink: 0;
  width: 60px;
  height: 60px;
  background: var(--el-color-primary);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
}

.advantage-title {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 8px;
}

.advantage-desc {
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

.cta-section {
  background: var(--el-bg-color-page);
  padding: 80px 20px;
  text-align: center;
}

.cta-content h2 {
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 16px;
}

.cta-content p {
  font-size: 18px;
  color: var(--el-text-color-secondary);
  margin-bottom: 32px;
}
</style>
