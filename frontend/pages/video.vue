<template>
  <div class="video-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>AI 短视频生成</h1>
      <p>输入文案，AI 自动生成专业短视频</p>
    </div>

    <!-- 视频生成区域 -->
    <el-card class="generator-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>创建视频任务</span>
        </div>
      </template>

      <el-form :model="videoForm" label-width="100px">
        <el-form-item label="视频文案">
          <el-input
            v-model="videoForm.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入视频文案，AI 将根据文案生成视频内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="视频风格">
          <el-select v-model="videoForm.video_style" placeholder="选择视频风格">
            <el-option label="默认风格" value="" />
            <el-option label="商务风格" value="business" />
            <el-option label="时尚风格" value="fashion" />
            <el-option label="科技风格" value="tech" />
            <el-option label="教育风格" value="education" />
          </el-select>
        </el-form-item>

        <el-form-item label="视频时长">
          <el-slider v-model="videoForm.video_duration" :min="10" :max="60" :step="5" show-input />
          <span class="hint">建议时长：15-30秒</span>
        </el-form-item>

        <el-form-item label="视频比例">
          <el-radio-group v-model="videoForm.aspect_ratio">
            <el-radio label="16:9">16:9 (横屏)</el-radio>
            <el-radio label="9:16">9:16 (竖屏)</el-radio>
            <el-radio label="1:1">1:1 (方形)</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="generating"
            @click="handleGenerate"
          >
            <template v-if="!generating">
              <el-icon><VideoCamera /></el-icon>
              生成视频
            </template>
            <template v-else>
              生成中...
            </template>
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 生成历史 -->
    <el-card class="history-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <span>生成历史</span>
          <el-button text @click="loadTasks">刷新</el-button>
        </div>
      </template>

      <div v-if="tasks.length === 0" class="empty-state">
        <el-empty description="暂无生成记录" />
      </div>

      <div v-else class="tasks-grid">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="task-item"
          @click="selectTask(task)"
        >
          <div class="task-status" :class="task.status">
            <el-icon v-if="task.status === 'completed'"><CircleCheck /></el-icon>
            <el-icon v-else-if="task.status === 'processing'"><Loading /></el-icon>
            <el-icon v-else-if="task.status === 'failed'"><CircleClose /></el-icon>
          </div>
          <div class="task-info">
            <p class="task-prompt">{{ task.prompt }}</p>
            <div class="task-meta">
              <span>{{ formatDate(task.created_at) }}</span>
              <el-tag :type="getStatusType(task.status)" size="small">
                {{ getStatusText(task.status) }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 视频播放弹窗 -->
      <el-dialog
        v-model="showVideoDialog"
        title="视频预览"
        width="800px"
        @close="selectedTask = null"
      >
        <div v-if="selectedTask" class="video-dialog-content">
          <div class="video-info">
            <p><strong>提示词：</strong>{{ selectedTask.prompt }}</p>
            <p><strong>状态：</strong>{{ getStatusText(selectedTask.status) }}</p>
            <p v-if="selectedTask.video_url"><strong>视频链接：</strong>
              <el-link :href="selectedTask.video_url" target="_blank" type="primary">在新窗口打开</el-link>
            </p>
          </div>
          <div v-if="selectedTask.video_url" class="video-player">
            <video :src="selectedTask.video_url" controls style="width: 100%; max-height: 500px;"></video>
          </div>
          <div v-else class="no-video">
            <el-empty description="视频尚未生成完成" />
          </div>
        </div>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { VideoCamera, CircleCheck, Loading, CircleClose } from '@element-plus/icons-vue'
import { videoApi, type VideoTask } from '~/utils/api'

const userStore = useUserStore()
const router = useRouter()

// 检查登录
onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
  }
})

// 视频生成表单
const videoForm = reactive({
  prompt: '',
  video_style: '',
  video_duration: 15,
  aspect_ratio: '16:9'
})

const generating = ref(false)
const tasks = ref<VideoTask[]>([])
const showVideoDialog = ref(false)
const selectedTask = ref<VideoTask | null>(null)

// 选择任务查看视频
const selectTask = (task: VideoTask) => {
  selectedTask.value = task
  showVideoDialog.value = true
}

// 生成视频
const handleGenerate = async () => {
  if (!videoForm.prompt.trim()) {
    return
  }

  generating.value = true
  try {
    const result = await videoApi.generate({
      prompt: videoForm.prompt,
      video_style: videoForm.video_style || undefined,
      video_duration: videoForm.video_duration,
      aspect_ratio: videoForm.aspect_ratio
    })
    // 模拟成功（实际需要后端支持）
    console.log('生成任务创建成功:', result)
    await loadTasks()
    videoForm.prompt = ''
  } catch (error: any) {
    console.error('生成失败:', error)
  } finally {
    generating.value = false
  }
}

// 加载任务列表
const loadTasks = async () => {
  try {
    const result = await videoApi.listTasks()
    tasks.value = result.items
  } catch (error) {
    console.error('加载任务失败:', error)
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 获取状态类型
const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    completed: 'success',
    processing: 'warning',
    failed: 'danger',
    pending: 'info'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    completed: '已完成',
    processing: '处理中',
    failed: '失败',
    pending: '等待中'
  }
  return texts[status] || status
}

// 初始加载
onMounted(() => {
  loadTasks()
})
</script>

<style scoped lang="scss">
.video-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;

  h1 {
    font-size: 28px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  p {
    color: var(--el-text-color-secondary);
  }
}

.generator-card {
  margin-bottom: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.hint {
  margin-left: 12px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.task-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;

  &:hover {
    border-color: var(--el-color-primary);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  }
}

.task-status {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;

  &.completed {
    background: var(--el-color-success-light-9);
    color: var(--el-color-success);
  }

  &.processing {
    background: var(--el-color-warning-light-9);
    color: var(--el-color-warning);
  }

  &.failed {
    background: var(--el-color-danger-light-9);
    color: var(--el-color-danger);
  }

  &.pending {
    background: var(--el-color-info-light-9);
    color: var(--el-color-info);
  }
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-prompt {
  font-size: 14px;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.task-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.empty-state {
  padding: 40px 0;
}
</style>
