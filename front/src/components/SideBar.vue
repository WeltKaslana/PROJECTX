<template>
  <el-aside :width="sidebarWidth" class="sidebar">
    <div class="sidebar-content">
      <!-- 创建新聊天按钮 -->
      <div class="new-chat-btn" @click="handleCreateNewChat">
        <el-icon><Plus /></el-icon>
        <span>新建聊天</span>
      </div>

      <!-- 历史对话列表 -->
      <div class="history-section">
        <div class="section-header">
          <el-icon><Clock /></el-icon>
          <span>历史对话</span>
        </div>
        
        <div class="conversation-list" :class="{ 'has-scroll': conversations.length > 10 }">
          <div 
            v-for="conv in conversations" 
            :key="conv.id" 
            class="conversation-item"
            :class="{ 'active': conv.id === currentConversation }"
            @click="loadHistory(conv.id)"
          >
            <el-icon><ChatDotRound /></el-icon>
            <span class="conversation-title">{{ formatConversationTitle(conv.title) }}</span>
            <span class="conversation-time">{{ formatTime(conv.createdAt) }}</span>
          </div>
          
          <div v-if="conversations.length === 0" class="empty-tip">
            <el-icon><FolderOpened /></el-icon>
            <span>暂无历史对话</span>
          </div>
        </div>
      </div>
    </div>
  </el-aside>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '@/api/auth'
import { useChat } from '@/api/chat'
import { Plus, Clock, ChatDotRound, FolderOpened } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 响应式计算侧边栏宽度
const sidebarWidth = ref('200px')

const calculateWidth = () => {
  if (window.innerWidth < 480) return '0'
  if (window.innerWidth < 600) return '160px'
  if (window.innerWidth < 768) return '180px'
  if (window.innerWidth < 900) return '190px'
  return '200px'
}

onMounted(() => {
  sidebarWidth.value = calculateWidth()
  window.addEventListener('resize', () => {
    sidebarWidth.value = calculateWidth()
  })
})

// 认证模块
const { user, visitorLogin } = useAuth()

// 聊天模块
const {
  conversations,
  currentConversation,
  chatLoading,
  createNewChat,
  loadHistory
} = useChat(user.value?.username)

// 格式化对话标题
const formatConversationTitle = (title) => {
  return title.length > 15 ? title.substring(0, 15) + '...' : title
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return `${date.getMonth()+1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`
}

// 创建新聊天
const handleCreateNewChat = async () => {
  try {
    if (!user.value) {
      await visitorLogin()
    }
    await createNewChat()
    ElMessage.success('新对话已创建')
  } catch (err) {
    ElMessage.error(err.reason || err.message || '创建对话失败')
  }
}
</script>

<style scoped>
.sidebar {
  height: calc(100vh - 65px);
  background-color: white;
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.08);
  transition: all 0.3s;
  z-index: 5;
  overflow: hidden;
}

.sidebar-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 10px;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  margin-bottom: 15px;
  border-radius: 8px;
  background-color: var(--el-color-primary);
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background-color: var(--el-color-primary-light-3);
}

.new-chat-btn .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.history-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 5px 10px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.section-header .el-icon {
  margin-right: 8px;
  font-size: 16px;
}

.conversation-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 5px;
}

.conversation-list.has-scroll {
  max-height: calc(100vh - 180px);
}

.conversation-item {
  display: flex;
  flex-direction: column;
  padding: 10px 12px;
  margin-bottom: 5px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.conversation-item:hover {
  background-color: var(--el-color-primary-light-9);
}

.conversation-item.active {
  background-color: var(--el-color-primary-light-8);
}

.conversation-item .el-icon {
  position: absolute;
  left: 12px;
  top: 12px;
  font-size: 16px;
  color: var(--el-text-color-secondary);
}

.conversation-title {
  padding-left: 25px;
  margin-bottom: 3px;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-time {
  padding-left: 25px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.empty-tip {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100px;
  color: var(--el-text-color-secondary);
}

.empty-tip .el-icon {
  font-size: 24px;
  margin-bottom: 10px;
}

/* 滚动条样式 */
.conversation-list::-webkit-scrollbar {
  width: 6px;
}

.conversation-list::-webkit-scrollbar-thumb {
  background-color: var(--el-color-primary-light-5);
  border-radius: 3px;
}

.conversation-list::-webkit-scrollbar-track {
  background-color: var(--el-color-primary-light-9);
}

/* 移动端隐藏时的动画 */
@media (max-width: 480px) {
  .sidebar {
    transform: translateX(-230px);
  }
}
</style>