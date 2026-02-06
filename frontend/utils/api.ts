/**
 * API 服务
 */
import request from './request'

// ========== 类型定义 ==========
export interface User {
  id: number
  username: string
  email?: string
  phone?: string
  nickname?: string
  avatar?: string
  bio?: string
  membership_type: string
  membership_expire_at?: string
  daily_quota: number
  used_quota: number
  status: string
  created_at: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email?: string
  phone?: string
  password: string
  confirm_password: string
  nickname?: string
}

export interface TokenResponse {
  access_token: string
  user: User
}

// ========== 知识库类型 ==========
export interface KnowledgeBase {
  id: number
  user_id: number
  name: string
  description?: string
  avatar?: string
  document_count: number
  total_chars: number
  is_public: boolean
  created_at: string
}

export interface KnowledgeDocument {
  id: number
  kb_id: number
  file_name: string
  file_url?: string
  file_size?: number
  file_type?: string
  chunk_count: number
  status: string
  created_at: string
}

// ========== 视频类型 ==========
export interface VideoTask {
  id: number
  user_id: number
  prompt: string
  video_style?: string
  video_duration: number
  aspect_ratio: string
  video_url?: string
  thumbnail_url?: string
  status: string
  progress: number
  created_at: string
}

export interface VideoTemplate {
  id: number
  name: string
  description?: string
  category: string
  tags?: string
  preview_url?: string
  thumbnail_url?: string
  usage_count: number
  rating: number
}

// ========== 认证 API ==========
export const authApi = {
  // 登录
  login(data: LoginRequest) {
    return request.post<any, TokenResponse>('/auth/login', data)
  },

  // 注册
  register(data: RegisterRequest) {
    return request.post<any, TokenResponse>('/auth/register', data)
  },

  // 获取当前用户信息
  getCurrentUser() {
    return request.get<any, User>('/auth/me')
  },

  // 登出
  logout() {
    return request.post('/auth/logout')
  }
}

// ========== 知识库 API ==========
export const knowledgeApi = {
  // 获取知识库列表
  list(params?: { page?: number; page_size?: number }) {
    return request.get<any, { items: KnowledgeBase[]; total: number }>('/knowledge-bases', { params })
  },

  // 获取知识库详情
  get(id: number) {
    return request.get<any, KnowledgeBase>(`/knowledge-bases/${id}`)
  },

  // 创建知识库
  create(data: { name: string; description?: string }) {
    return request.post<any, KnowledgeBase>('/knowledge-bases', data)
  },

  // 更新知识库
  update(id: number, data: { name?: string; description?: string }) {
    return request.put<any, KnowledgeBase>(`/knowledge-bases/${id}`, data)
  },

  // 删除知识库
  delete(id: number) {
    return request.delete(`/knowledge-bases/${id}`)
  },

  // 上传文档
  uploadDocument(kbId: number, file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<any, KnowledgeDocument>(`/knowledge-bases/${kbId}/documents`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 获取文档列表
  listDocuments(kbId: number, params?: { page?: number; page_size?: number }) {
    return request.get<any, { items: KnowledgeDocument[]; total: number }>(`/knowledge-bases/${kbId}/documents`, { params })
  },

  // 删除文档
  deleteDocument(kbId: number, docId: number) {
    return request.delete(`/knowledge-bases/${kbId}/documents/${docId}`)
  },

  // 知识库问答
  query(kbId: number, data: { query: string; top_k?: number }) {
    return request.post<any, { answer: string; sources: any[] }>(`/knowledge-bases/${kbId}/query`, data)
  }
}

// ========== 视频 API ==========
export const videoApi = {
  // 创建视频生成任务
  generate(data: { prompt: string; video_style?: string; video_duration?: number; aspect_ratio?: string }) {
    return request.post<any, VideoTask>('/video/generate', data)
  },

  // 获取任务列表
  listTasks(params?: { page?: number; page_size?: number; status?: string }) {
    return request.get<any, { items: VideoTask[]; total: number }>('/video/tasks', { params })
  },

  // 获取任务详情
  getTask(id: number) {
    return request.get<any, VideoTask>(`/video/tasks/${id}`)
  },

  // 删除任务
  deleteTask(id: number) {
    return request.delete(`/video/tasks/${id}`)
  },

  // 获取模板列表
  listTemplates(params?: { page?: number; page_size?: number; category?: string }) {
    return request.get<any, { items: VideoTemplate[]; total: number }>('/video/templates', { params })
  },

  // 生成视频脚本
  generateScript(data: { prompt: string; style?: string; duration?: number }) {
    return request.post<any, { script: string }>('/video/generate-script', null, { params: data })
  }
}

// ========== 默认导出 ==========
export default {
  auth: authApi,
  knowledge: knowledgeApi,
  video: videoApi
}
