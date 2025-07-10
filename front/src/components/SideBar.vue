<template>
  <el-aside :width="sidebarWidth" class="sidebar">
    <el-menu default-active="2" class="vertical-menu" :router="true" mode="vertical">
      <!-- 创建新聊天 -->
      <el-menu-item index="/chat" @click="handleCreateNewChat" :disabled="chatLoading">
        <el-icon><icon-menu /></el-icon>
        <span>创建新聊天</span>
      </el-menu-item>

      <!-- 历史对话下拉菜单 -->
      <el-submenu index="history" v-if="conversations.length > 0">
        <template #title>
          <el-icon>
            <document />
          </el-icon>
          <span>历史对话</span>
        </template>
        <el-menu-item v-for="conv in conversations" :key="conv.id" @click="loadHistory(conv.id)">
          {{ conv.title }}
        </el-menu-item>
      </el-submenu>
      <el-menu-item v-else index="no-history" disabled>
        <el-icon>
          <document />
        </el-icon>
        <span>暂无历史对话</span>
      </el-menu-item>

      <!-- 历史聊天 -->
      <el-menu-item index="3" @click="loadHistory(currentConversation)"
        :disabled="!currentConversation || chatLoading">
        <el-icon><icon-menu /></el-icon>
        <span>历史聊天</span>
      </el-menu-item>

      <!-- 底部固定菜单 -->
      <div class="menu-footer">
        <el-menu-item index="/settings">
          <el-icon>
            <Setting />
          </el-icon>
          <span>用户设置</span>
        </el-menu-item>
        <el-menu-item index="/help">
          <el-icon>
            <Location />
          </el-icon>
          <span>帮助页面</span>
        </el-menu-item>
      </div>
    </el-menu>
  </el-aside>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuth } from '@/api/auth'
import { useChat } from '@/api/chat'
import { Document, Menu as IconMenu, Setting, Location } from '@element-plus/icons-vue'
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

watch(() => window.innerWidth, () => {
  sidebarWidth.value = calculateWidth()
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

.vertical-menu {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: none;
}

.menu-footer {
  margin-top: auto;
  padding-bottom: 20px;
}

/* 移动端隐藏时的动画 */
@media (max-width: 480px) {
  .sidebar {
    transform: translateX(-230px);
  }
}
</style>