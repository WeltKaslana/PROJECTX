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
import elementPlusLogo from '@/assets/logo.png'
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
            <img style="width: 100px" :src="elementPlusLogo" alt="应用Logo" />
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

        <!-- 主内容区 -->
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- 聊天输入框 -->
    <div v-if="showChatBox" class="chat-box">
      <div class="input-container">
        <!-- 用户状态显示 -->
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

        <!-- 消息输入区域 -->
        <el-input v-model="message" placeholder="请输入您的问题..." class="message-input" type="textarea" :rows="4" />
        <el-button type="primary" class="send-button" @click="handleSubmitMessage"
          :disabled="!message.trim() || chatLoading" :loading="chatLoading">
          <el-icon>
            <Upload />
          </el-icon>
        </el-button>
      </div>
    </div>
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

.main-content {
  padding: 20px;
  overflow-y: auto;
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
</style>