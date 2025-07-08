<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElButton,
  ElDropdown,
  ElMenu,
  ElMenuItem,
  ElMessage
} from 'element-plus'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'
import elementPlusLogo from '@/assets/logo.png'
import { useAuth } from '@/api/auth'
import { useChat } from '@/api/chat'

const route = useRoute()
const router = useRouter()

// 使用 auth 模块
const {
  user,
  error: authError,
  loading: authLoading,
  register,
  login,
  visitorLogin,
  logout
} = useAuth()

// 使用chat模块
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

// 路由相关计算属性
const currentRoute = computed(() => route.path)
const excludePaths = computed(() => [
  '/help',
  '/settings',
  '/about',
  '/login',
  '/register',
])

// 消息输入
const message = ref('')

// 处理消息提交
const handleSubmitMessage = async () => {
  if (!message.value.trim()) return;

  try {
    // 使用正确的函数名 visitorLogin
    if (!user.value) {
      await visitorLogin();
    }
    await searchKeywords(currentConversation.value, message.value);
    message.value = '';
  } catch (error) {
    ElMessage.error('发送消息失败: ' + (error.reason || error.message));
  }
};

// 导航到登录页面
const navigateToLogin = () => {
  router.push('/login')
}

// 导航到注册页面
const navigateToRegister = () => {
  router.push('/register')
}
const navigateToInfo = () => {
  router.push('/info')
}
// 方法：查看历史聊天
const viewHistory = () => {
  console.log('查看历史聊天')
  // 逻辑代码可以在这里添加
}

// 方法：筛选商品
const filterProducts = () => {
  console.log('筛选商品')
  // 逻辑代码可以在这里添加
}

// 方法：设置价格提醒
const setPriceAlert = () => {
  console.log('设置价格提醒')
  // 逻辑代码可以在这里添加
}

// 方法：打开用户设置
const openSettings = () => {
  console.log('打开设置')
  // 逻辑代码可以在这里添加
}

// 方法：打开帮助
const openHelp = () => {
  console.log('打开帮助')
  // 逻辑代码可以在这里添加
}
</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <el-menu mode="horizontal" :ellipsis="false" :router="true" class="nav-menu">
          <el-menu-item index="0">
            <img style="width: 100px" :src="elementPlusLogo" alt="Element logo" />
          </el-menu-item>

          <!-- 右上角的注册/登录按钮 -->
          <div v-if="!user" class="login-btn">
            <el-button @click="navigateToRegister" class="register-button" :loading="authLoading">
              注册
            </el-button>

            <el-button @click="navigateToLogin" class="login-button" :loading="authLoading">
              登录
            </el-button>


          </div>
          <!-- 如果已登录，则显示用户信息和设置 -->
          <div v-else class="user-dropdown">
            <el-dropdown>
              <el-button>
                {{ user.username }} <i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <template #dropdown>
                <el-menu>
                  <el-menu-item @click="navigateToInfo">用户信息</el-menu-item>
                  <el-menu-item @click="router.push('/settings')">设置</el-menu-item>
                  <el-menu-item @click="logout">退出</el-menu-item>
                </el-menu>
              </template>
            </el-dropdown>
          </div>
        </el-menu>
      </el-header>

      <el-container>
        <el-aside width="230px" class="aside">
          <el-menu default-active="2" class="el-menu-vertical-demo" :router="true" mode="vertical">
            <!--创建新聊天-->
            <el-menu-item index="/chat" @click="createNewChat" :disabled="!user || chatLoading">
              <el-icon><icon-menu /></el-icon>
              <span>创建新聊天</span>
            </el-menu-item>

            <!--商品筛选-->
            <el-menu-item index="/shopping" @click="filterProducts" :disabled="chatLoading">
              <el-icon><icon-menu /></el-icon>
              <span>商品筛选</span>
            </el-menu-item>

            <!-- 历史聊天 -->
            <el-menu-item index="3" @click="loadHistory(currentConversation)"
              :disabled="!user || !currentConversation || chatLoading">
              <el-icon><icon-menu /></el-icon>
              <span>历史聊天</span>
            </el-menu-item>

            <!-- 固定底部 -->
            <div class="bottom-buttons">
              <!-- 用户设置 -->
              <el-menu-item index="/settings">
                <el-icon>
                  <Setting />
                </el-icon>
                <span>用户设置</span>
              </el-menu-item>

              <!-- 帮助 -->
              <el-menu-item index="/help">
                <el-icon>
                  <Location />
                </el-icon>
                <span>帮助页面</span>
              </el-menu-item>
            </div>
          </el-menu>
        </el-aside>

        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- 聊天输入框 -->
    <div v-if="!excludePaths.includes(currentRoute)" class="chat-box">
      <div class="input-wrapper">
        <div v-if="user" class="user-info">
          当前用户: {{ user.username }}
          <el-tag v-if="user.isVisitor" type="info" size="small">游客</el-tag>
        </div>
        <div v-else class="user-info">
          <el-tag type="info">游客模式</el-tag>
        </div>

        <el-input v-model="message" placeholder="请输入您的问题..." class="message-input"></el-input>
        <el-button type="primary" class="submit-btn" @click="handleSubmitMessage" :loading="chatLoading">
          ↑
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-info {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 右上角的登录按钮样式 */
.login-btn {
  float: right;
  display: flex;
  justify-content: center;
  /* 水平居中 */
  align-items: center;
  /* 垂直居中 */
  margin-top: 5px;
  /* 调整按钮与顶部的距离 */
  margin-right: 5px;
  /* 确保按钮靠右 */
}

/* 修改登录按钮样式：黑色背景，白色字体 */
.login-button {
  background-color: black;
  color: white;
  border-color: black;
}

.login-button:hover {
  background-color: #666;
  color: white;
  border-color: #666;
}

.aside {
  height: 90vh;
  margin-top: 20px;
  display: flex;
  flex-direction: column;
}

.el-menu-vertical-demo {
  flex-grow: 1;
  overflow-y: auto;
}

.bottom-buttons {
  margin-top: 300px;
  /* 固定底部 */
  padding: 1px;
}

.el-menu-item {
  display: flex;
  align-items: center;
  padding-left: 20px;
  font-size: 16px;
  color: #333;
}

.el-menu-item:hover {
  background-color: #ddd;
}

.el-menu--horizontal {
  --el-menu-horizontal-height: 65px;
}

.el-menu--horizontal>.el-menu-item:nth-child(1) {
  margin-right: auto;
}

.input-label {
  font-size: 30px;
  color: black;
  margin-bottom: 30px;
  text-align: center;
  font-weight: bold;
}

.chat-box {
  position: absolute;
  top: 75%;
  /* 垂直居中 */
  left: 50%;
  /* 水平居中 */
  transform: translate(-40%, -50%);
  width: 900px;
}

.input-wrapper {
  text-align: center;
}

.message-input {
  vertical-align: top;
  width: 100%;
  height: 200px;
  margin-bottom: 10px;
  font-size: 20px;
}

.submit-btn {
  width: 40px;
  height: 40px;
  border-radius: 100%;
  /* 使按钮变圆 */
  position: absolute;
  bottom: 20px;
  /* 按钮位置靠近文本框右下角 */
  right: 15px;
  /* 放置到右下角 */
  padding: 0;
  font-size: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: black;
  color: white;
  border-color: black;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
</style>