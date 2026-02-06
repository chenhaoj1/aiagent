<template>
  <div class="knowledge-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1>智能知识库</h1>
      <p>上传文档，构建专属知识库，AI 智能问答</p>
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建知识库
      </el-button>
    </div>

    <!-- 知识库列表 -->
    <div v-if="knowledgeBases.length === 0" class="empty-state">
      <el-empty description="暂无知识库，点击上方按钮创建">
        <el-button type="primary" @click="showCreateDialog = true">
          创建知识库
        </el-button>
      </el-empty>
    </div>

    <div v-else class="kb-grid">
      <el-card
        v-for="kb in knowledgeBases"
        :key="kb.id"
        class="kb-card"
        shadow="hover"
        @click="openKnowledgeBase(kb)"
      >
        <div class="kb-icon">
          <el-icon :size="32"><Folder /></el-icon>
        </div>
        <h3 class="kb-name">{{ kb.name }}</h3>
        <p class="kb-desc">{{ kb.description || '暂无描述' }}</p>
        <div class="kb-meta">
          <span><el-icon><Document /></el-icon> {{ kb.document_count }} 个文档</span>
          <span><el-icon><ChatDotRound /></el-icon> {{ kb.total_chars }} 字符</span>
        </div>
      </el-card>
    </div>

    <!-- 创建知识库对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建知识库"
      width="500px"
    >
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input
            v-model="createForm.name"
            placeholder="请输入知识库名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入知识库描述（可选）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Plus, Folder, Document, ChatDotRound } from '@element-plus/icons-vue'
import { knowledgeApi, type KnowledgeBase } from '~/utils/api'

const userStore = useUserStore()
const router = useRouter()

// 检查登录
onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
  }
})

const showCreateDialog = ref(false)
const creating = ref(false)
const knowledgeBases = ref<KnowledgeBase[]>([])

const createForm = reactive({
  name: '',
  description: ''
})

// 创建知识库
const handleCreate = async () => {
  if (!createForm.name.trim()) {
    return
  }

  creating.value = true
  try {
    await knowledgeApi.create({
      name: createForm.name,
      description: createForm.description || undefined
    })
    showCreateDialog.value = false
    createForm.name = ''
    createForm.description = ''
    await loadKnowledgeBases()
  } catch (error: any) {
    console.error('创建失败:', error)
  } finally {
    creating.value = false
  }
}

// 打开知识库详情
const openKnowledgeBase = (kb: KnowledgeBase) => {
  // 这里可以跳转到知识库详情页，暂时使用 console
  console.log('打开知识库:', kb)
  // TODO: 创建知识库详情页
  alert(`知识库详情功能开发中\n知识库: ${kb.name}`)
}

// 加载知识库列表
const loadKnowledgeBases = async () => {
  try {
    const result = await knowledgeApi.list()
    knowledgeBases.value = result.items
  } catch (error) {
    console.error('加载知识库失败:', error)
  }
}

// 初始加载
onMounted(() => {
  loadKnowledgeBases()
})
</script>

<style scoped lang="scss">
.knowledge-page {
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

.action-bar {
  margin-bottom: 24px;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.kb-card {
  cursor: pointer;
  transition: all 0.3s;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  }
}

.kb-icon {
  width: 60px;
  height: 60px;
  margin: 0 auto 16px;
  background: var(--el-color-primary-light-9);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-color-primary);
  font-size: 28px;
}

.kb-name {
  font-size: 18px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-desc {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  text-align: center;
  margin-bottom: 16px;
  min-height: 40px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.kb-meta {
  display: flex;
  justify-content: space-around;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 13px;
  color: var(--el-text-color-secondary);

  span {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}

.empty-state {
  padding: 80px 0;
}
</style>
