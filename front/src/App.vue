<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Header from '@/components/Header.vue'
import Sidebar from '@/components/Sidebar.vue'
import ChatAssistant from '@/components/ChatAssistant.vue'
import { useAuth } from '@/api/auth'
import { useChat } from '@/api/chat'


// 路由相关
const route = useRoute()
const currentRoute = computed(() => route.path)

// 排除聊天框的路径
const excludedPaths = [
  '/help',
  '/settings',
  '/about',
  '/login',
  '/register',
  '/test',
]
const showChatBox = computed(() => !excludedPaths.includes(currentRoute.value))

// 认证模块
const { user, visitorLogin } = useAuth()

// 聊天模块
const { fetchConversations } = useChat(user.value?.username)

onMounted(async () => {
  if (user.value) {
    await fetchConversations()
  }
})
</script>

<template>
  <div class="common-layout">
    <el-container direction="vertical">
      <!-- 顶部导航栏 -->
      <Header class="header" />
      
      <!-- 主体内容区域 -->
      <el-container class="content-container">
        <!-- 侧边栏导航 -->
        <Sidebar class="sidebar" />
        
        <!-- 主内容区 -->
        <main class="main-area">
          <router-view v-if="!showChatBox" class="router-content" />
          <ChatAssistant v-else class="chat-content" />
        </main>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.common-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  overflow-y: auto;
}

.header {
  flex: 0 0 auto;
  height: 60px; /* 固定高度 */
}

.content-container {
  flex: 1;
  min-height: 0; /* 修复Flexbox计算问题 */
}

.sidebar {
  width: 200px;
  height: 100%;
  overflow-y: auto;
  transition: width 0.3s;
}

.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 修复Flexbox溢出问题 */
}

.router-content,
.chat-content {
  flex: 1;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .sidebar {
    width: 180px;
  }
}

@media (max-width: 600px) {
  .sidebar {
    width: 160px;
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 0;
    position: absolute;
    z-index: 100;
  }
  
  .main-area {
    height: calc(100vh - 50px);
  }
}
</style>