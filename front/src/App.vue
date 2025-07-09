<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElButton,
  ElDropdown,
  ElMenu,
  ElMenuItem,
  ElMessage,
  ElTag
} from 'element-plus'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
  Upload
} from '@element-plus/icons-vue'
import Zhigou_Logo from '@/assets/logo.png'
import { useAuth } from '@/api/auth'
import { useChat } from '@/api/chat'

// ======================
// 路由相关
// ======================
const route = useRoute()
const router = useRouter()

// 排除聊天框的路径
const excludedPaths = [
  '/help',
  '/settings',
  '/about',
  '/login',
  '/register'
]
const currentRoute = computed(() => route.path)
const showChatBox = computed(() => !excludedPaths.includes(currentRoute.value))

// ======================
// 认证模块
// ======================
const {
  user,
  error: authError,
  loading: authLoading,
  login,
  logout,
  register,
  visitorLogin
} = useAuth()

// ======================
// 聊天模块
// ======================
const {
  conversations,
  currentConversation,
  messages,
  loading: chatLoading,
  error: chatError,
  createNewChat,
  getHistoryCount,
  loadHistory,
  searchKeywords
} = useChat(user.value?.username)

// ======================
// 数据状态
// ======================
const message = ref('')

// ======================
// 导航方法
// ======================
const navigateTo = {
  login: () => router.push('/login'),
  register: () => router.push('/register'),
  info: () => router.push('/info'),
  settings: () => router.push('/settings'),
  shopping: () => router.push('/shopping'),
  help: () => router.push('/help'),
  about: () => router.push('/about')

}

// ======================
// 聊天相关方法
// ======================
const handleSubmitMessage = async () => {
  if (!message.value.trim()) return
  navigateTo.shopping()
  try {
    // 导航到商品页面
    
    // 未登录用户自动游客登录
    if (!user.value) {
      await visitorLogin()
      // 游客登录后创建新会话
      await createNewChat()
    }
    // 打印

    await searchKeywords(currentConversation.value, message.value)
    message.value = ''
  } catch (error) {
    showError('发送消息失败', error)
  }
}

// ======================
// 辅助方法
// ======================
const showError = (message, error) => {
  const reason = error.reason || error.message || '未知错误'
  ElMessage.error(`${message}: ${reason}`)
}

// 占位方法（待实现功能）
const placeholderMethod = (name) => {
  console.log(`${name}功能待实现`)
}
</script>

<template>
  <div class="common-layout">
    <!-- 顶部导航栏 -->
    <el-container>
      <el-header class="header">
        <el-menu mode="horizontal" :ellipsis="false" :router="true" class="nav-menu">
          <!-- 应用logo -->
          <el-menu-item index="0">
            <img style="width: 100px" :src="Zhigou_Logo" alt="应用Logo" />
          </el-menu-item>

          <!-- 用户状态区域 -->
          <div class="user-state">
            <!-- 未登录状态 -->
            <div v-if="!user" class="auth-buttons">
              <el-button @click="navigateTo.register" class="auth-button register" :loading="authLoading">
                注册
              </el-button>
              <el-button @click="navigateTo.login" class="auth-button login" :loading="authLoading">
                登录
              </el-button>
            </div>

            <!-- 已登录状态 -->
            <div v-else class="user-profile">
              <el-dropdown>
                <el-button class="profile-button">
                  {{ user.username }}
                  <i class="el-icon-arrow-down el-icon--right"></i>
                </el-button>
                <template #dropdown>
                  <el-menu>
                    <el-menu-item @click="navigateTo.info">
                      用户信息
                    </el-menu-item>
                    <el-menu-item @click="navigateTo.settings">
                      设置
                    </el-menu-item>
                    <el-menu-item @click="logout">
                      退出
                    </el-menu-item>
                  </el-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-menu>
      </el-header>

      <!-- 主体内容区域 -->
      <el-container>
        <!-- 侧边栏导航 -->
        <el-aside width="230px" class="sidebar">
          <el-menu default-active="2" class="vertical-menu" :router="true" mode="vertical">
            <!-- 聊天功能 -->
            <el-menu-item index="/chat" @click="createNewChat" :disabled="chatLoading">
              <el-icon><icon-menu /></el-icon>
              <span>创建新聊天</span>
            </el-menu-item>

            <!-- 历史记录 -->
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

        <!-- 主内容区 - 现在包含AI助手界面 -->
        <el-main class="main-content" v-if="!showChatBox">
          <router-view />
        </el-main>

        <!-- AI助手界面（当showChatBox为true时显示） -->
        <div v-else class="ai-assistant-container">
          <!-- 聊天历史区域 -->
          <div class="chat-history">
            <div v-if="messages.length > 0" class="messages-container">
              <div v-for="(msg, index) in messages" :key="index" class="message-bubble" 
                   :class="{'user-message': msg.role === 'user', 'ai-message': msg.role === 'assistant'}">
                <div class="message-avatar">
                  <el-avatar v-if="msg.role === 'assistant'" :size="32" :src="Zhigou_Logo" />
                  <el-avatar v-else :size="32" :src="user?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
                </div>
                <div class="message-content">
                  <div class="message-role">
                    {{ msg.role === 'assistant' ? 'AI助手' : user?.username || '游客' }}
                    <span class="message-time">{{ new Date().toLocaleTimeString() }}</span>
                  </div>
                  <div class="message-text">{{ msg.content }}</div>
                </div>
              </div>
            </div>
            
            <!-- 空状态 -->
            <div v-else class="empty-state">
              <el-avatar :size="64" :src="Zhigou_Logo" />
              <h3>我是您的AI购物助手</h3>
              <p>请问您想找什么商品？我可以帮您搜索和推荐</p>
              <div class="quick-questions">
                <el-tag v-for="(question, idx) in [
                  '最新手机推荐', 
                  '夏季女装优惠', 
                  '家用电器排行榜',
                  '运动鞋哪个品牌好'
                ]" :key="idx" @click="message = question; handleSubmitMessage()">
                  {{ question }}
                </el-tag>
              </div>
            </div>
            
            <!-- 加载状态 -->
            <div v-if="chatLoading" class="loading-indicator">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>AI正在思考中...</span>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="input-area">
            <div class="user-status">
              <template v-if="user">
                当前用户: {{ user.username }}
                <el-tag v-if="user.isVisitor" type="info" size="small">
                  游客
                </el-tag>
              </template>
              <el-tag v-else type="info">
                游客模式 (消息将自动以游客身份发送)
              </el-tag>
            </div>
            
            <div class="input-wrapper">
              <el-input
                v-model="message"
                placeholder="请输入您想找的商品或问题..."
                type="textarea"
                :rows="2"
                resize="none"
                @keyup.enter.native="handleSubmitMessage"
                class="message-input"
              />
              <div class="input-actions">


                <el-button
                  type="primary"
                  @click="handleSubmitMessage"
                  :disabled="!message.trim() || chatLoading"
                  :loading="chatLoading"
                  class="send-button"
                >
                  发送
                  <el-icon class="el-icon--right"><Upload /></el-icon>
                </el-button>
              </div>
            </div>
            <div class="input-footer">
              <small>AI助手可能会出错，请核对重要信息</small>
            </div>
          </div>
        </div>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
/* 布局样式 */
.common-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  padding: 0;
  height: 65px;
}

.sidebar {
  height: calc(100vh - 65px);
  margin-top: 20px;
}

/* 主内容区调整 */
.main-content {
  padding: 0;
  overflow-y: auto;
  height: calc(100vh - 65px); /* 减去header高度 */
}

/* 导航菜单样式 */
.nav-menu {
  display: flex;
  align-items: center;
  height: 100%;
}

.user-state {
  margin-left: auto;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

/* 按钮样式 */
.auth-button {
  &.login {
    background-color: black;
    color: white;
    border-color: black;

    &:hover {
      background-color: #666;
      border-color: #666;
    }
  }

  &.register {
    background-color: white;
    color: black;
    border-color: #dcdfe6;

    &:hover {
      background-color: #f5f7fa;
    }
  }
}

.profile-button {
  padding: 8px 15px;
}

/* 侧边栏样式 */
.vertical-menu {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.menu-footer {
  margin-top: auto;
  padding-bottom: 20px;
}

/* 聊天框样式 */
.chat-box {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  max-width: 900px;
  padding: 20px;
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
}

.input-container {
  position: relative;
}

.user-status {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-input {
  font-size: 16px;
}

.send-button {
  position: absolute;
  right: 10px;
  bottom: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
}
/* 扩展的AI助手样式 */
/* AI助手容器样式调整 */
.ai-assistant-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 65px); /* 减去header高度 */
  width: calc(100% - 230px); /* 减去侧边栏宽度 */
  background: white;
  overflow: hidden;
}

/* 聊天历史区域调整 */
.chat-history {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f9f9f9;
}
.messages-container {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* 消息气泡最大宽度调整 */
.message-bubble {
  max-width: 80%;
}

.user-message {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.ai-message {
  align-self: flex-start;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.user-message .message-content {
  align-items: flex-end;
}

.ai-message .message-content {
  align-items: flex-start;
}

.message-role {
  font-size: 0.8em;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-time {
  font-size: 0.7em;
  color: #999;
}

.message-text {
  padding: 10px 15px;
  border-radius: 18px;
  line-height: 1.5;
  word-break: break-word;
}

.user-message .message-text {
  background: #409eff;
  color: white;
  border-top-right-radius: 4px;
}

.ai-message .message-text {
  background: #f1f1f1;
  color: #333;
  border-top-left-radius: 4px;
}

/* 空状态调整 */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.empty-state h3 {
  margin: 10px 0 5px;
  color: #333;
}

.empty-state p {
  margin-bottom: 20px;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.quick-questions .el-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.quick-questions .el-tag:hover {
  background: #409eff;
  color: white;
}

.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  color: #666;
  font-size: 0.9em;
}

/* 输入区域调整 */
.input-area {
  padding: 15px;
  background: white;
  border-top: 1px solid #eee;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

/* 输入框区域调整 */
.input-wrapper {
  position: relative;
  margin-top: 10px;
}

.message-input {
  padding-right: 100px;
  width: 100%;
}

.input-actions {
  position: absolute;
  right: 5px;
  bottom: 5px;
  display: flex;
  gap: 5px;
}

.send-button {
  padding: 7px 15px;
}

.input-footer {
  margin-top: 8px;
  text-align: center;
  color: #999;
  font-size: 0.8em;
}

/* 其他样式微调 */
.user-status {
  margin-bottom: 10px;
  padding: 0 5px;
}
</style>
