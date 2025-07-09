<script setup>
// ======================
// 导入模块
// ======================
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ElButton,
  ElDropdown,
  ElMenu,
  ElMenuItem,
  ElMessage,
  ElTag,
  ElTooltip
} from 'element-plus'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
  Upload,
  Promotion,
  Delete
} from '@element-plus/icons-vue'
import { Shop, Picture, Loading } from '@element-plus/icons-vue'
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
  '/register',
  '/test',
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
  searchKeywords,
  fetchConversations
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
  about: () => router.push('/about'),
  test: () => router.push('/test')
}

// ======================
// 聊天相关方法
// ======================
onMounted(async () => {
  if (user.value) {
    await fetchConversations();
  }
})

/**
 * 创建新聊天
 */
const handleCreateNewChat = async () => {
  try {
    if (!user.value) {
      await visitorLogin();
    }
    await createNewChat();
    ElMessage.success('新对话已创建');
  } catch (err) {
    ElMessage.error(err.reason || err.message || '创建对话失败');
  }
}

/**
 * 提交消息
 */
const handleSubmitMessage = async () => {
  if (!message.value.trim()) return

  try {
    if (!user.value) {
      await visitorLogin()
      await handleCreateNewChat()
    }

    // 模拟搜索结果
    const searchResults = {
      text: `这是关于"${message.value}"的搜索结果：`,
      products: generateSampleProducts(message.value)
    }

    // 添加到消息列表
    messages.value.push({
      role: 'assistant',
      content: searchResults.text,
      products: searchResults.products,
      timestamp: new Date().toISOString()
    })

    message.value = ''
  } catch (error) {
    showError('发送消息失败', error)
  }
}

/**
 * 处理换行
 */
const handleNewLine = () => {
  message.value += '\n'
}

// ======================
// 商品相关方法
// ======================
/**
 * 生成示例商品数据
 */
const generateSampleProducts = (keyword) => {
  const brands = ['Apple', '华为', '小米', 'OPPO', 'vivo', '三星']
  const shops = ['官方旗舰店', '品牌专卖店', '授权经销商', '优选店铺']
  const categories = {
    '手机': ['Pro', 'Max', 'Plus', 'Lite', 'SE'],
    '电脑': ['Air', 'Pro', '游戏本', '轻薄本'],
    '衣服': ['T恤', '衬衫', '卫衣', '外套']
  }

  // 根据关键词确定类别
  let category = '其他'
  Object.keys(categories).forEach(cat => {
    if (keyword.includes(cat)) category = cat
  })

  return Array.from({ length: 8 }, (_, i) => ({
    id: i + 1,
    name: `${brands[i % brands.length]} ${keyword} ${categories[category] ? categories[category][i % categories[category].length] : ''}`.trim(),
    price: (Math.random() * 5000 + 1000).toFixed(2),
    originalPrice: (Math.random() * 6000 + 1500).toFixed(2),
    image: `https://picsum.photos/300/300?random=${i}`,
    shop: `${brands[i % brands.length]}${shops[i % shops.length]}`,
    sales: Math.floor(Math.random() * 10000),
    link: `https://example.com/product/${i + 1}`
  }))
}

// ======================
// 组件定义
// ======================
/**
 * 商品卡片组件
 */
const ProductCard = {
  props: {
    product: {
      type: Object,
      required: true,
      validator: (value) => {
        return value.id && value.name && value.price
      }
    }
  },
  methods: {
    openProductLink() {
      window.open(this.product.link, '_blank')
    }
  },
  template: `
    <el-card class="product-card" :body-style="{ padding: '0px' }" shadow="hover" @click="openProductLink">
      <div class="image-container">
        <el-image :src="product.image" fit="cover" class="product-image" :alt="product.name">
          <template #error>
            <div class="image-error">
              <el-icon><Picture /></el-icon>
              <span>图片加载失败</span>
            </div>
          </template>
          <template #placeholder>
            <div class="image-loading">
              <el-icon><Loading /></el-icon>
            </div>
          </template>
        </el-image>
      </div>
      <div class="product-info">
        <div class="product-name" :title="product.name">{{ product.name }}</div>
        <div class="product-shop">
          <el-icon><Shop /></el-icon>
          <span>{{ product.shop }}</span>
        </div>
        <div class="product-price">
          <span class="current-price">¥{{ product.price }}</span>
          <span v-if="product.originalPrice" class="original-price">¥{{ product.originalPrice }}</span>
          <span v-if="product.sales" class="sales">月销{{ product.sales }}笔</span>
        </div>
      </div>
    </el-card>
  `
}

// ======================
// 辅助方法
// ======================
/**
 * 显示错误消息
 */
const showError = (message, error) => {
  const reason = error.reason || error.message || '未知错误'
  ElMessage.error(`${message}: ${reason}`)
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
                    <el-menu-item @click="navigateTo.test">
                      开发者功能
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
            <!-- 修改侧边栏菜单项 -->
            <el-menu-item index="/chat" @click="handleCreateNewChat" :disabled="chatLoading">
              <el-icon><icon-menu /></el-icon>
              <span>创建新聊天</span>
            </el-menu-item>

            <!-- 添加历史对话下拉菜单 -->
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
              <div v-for="(msg, index) in messages" :key="index" class="message-container">
                <!-- 消息气泡部分 -->
                <div class="message-bubble"
                  :class="{ 'user-message': msg.role === 'user', 'ai-message': msg.role === 'assistant' }">
                  <div class="message-avatar">
                    <el-avatar v-if="msg.role === 'assistant'" :size="32" :src="Zhigou_Logo" />
                    <el-avatar v-else :size="32"
                      :src="user?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
                  </div>
                  <div class="message-content">
                    <div class="message-role">
                      {{ msg.role === 'assistant' ? 'AI助手' : user?.username || '游客' }}
                      <span class="message-time">{{ new Date().toLocaleTimeString() }}</span>
                    </div>
                    <div class="message-text">{{ msg.content }}</div>
                  </div>
                </div>

                <!-- 商品卡片展示区域 -->
                <div v-if="msg.products && msg.products.length" class="products-container">
                  <div class="products-grid">
                    <component :is="ProductCard" v-for="(product, pIndex) in msg.products" :key="`product-${pIndex}`"
                      :product="product" />
                  </div>
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
              <el-icon class="is-loading">
                <Loading />
              </el-icon>
              <span>AI正在思考中...</span>
            </div>
          </div>

          <!-- 改进后的输入区域 -->
          <div class="input-area">
            <div class="user-status-bar">
              <div class="user-info">
                <el-avatar :size="24"
                  :src="user?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
                <span class="username">{{ user?.username || '游客' }}</span>
                <el-tag v-if="!user || user.isVisitor" type="info" size="small">
                  {{ user?.isVisitor ? '游客' : '游客模式' }}
                </el-tag>
              </div>
              <div class="input-hints">
                <small>按Enter发送，Shift+Enter换行</small>
              </div>
            </div>

            <div class="input-container">
              <el-input v-model="message" placeholder="请输入您想找的商品或问题..." type="textarea" :rows="2" resize="none"
                @keyup.enter.exact="handleSubmitMessage" @keydown.shift.enter="handleNewLine" class="message-input"
                :disabled="chatLoading" />
              <div class="action-buttons">
                <el-tooltip content="清空输入" placement="top">
                  <el-button circle :disabled="!message.trim()" @click="message = ''" class="clear-button">
                    <el-icon>
                      <Delete />
                    </el-icon>
                  </el-button>
                </el-tooltip>
                <el-button type="primary" @click="handleSubmitMessage" :disabled="!message.trim() || chatLoading"
                  :loading="chatLoading" class="send-button">
                  发送
                  <el-icon class="el-icon--right">
                    <Promotion />
                  </el-icon>
                </el-button>
              </div>
            </div>

            <div class="input-footer">
              <small>AI助手可能会出错，请核对重要信息</small>
              <small v-if="chatLoading">AI正在思考中，请稍候...</small>
            </div>
          </div>
        </div>
      </el-container>
    </el-container>
  </div>
</template>

<style scoped>
/* ======================
   全局布局样式 
   ====================== */
.common-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* ======================
   顶部导航栏样式 
   ====================== */
.header {
  padding: 0;
  height: 65px;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.nav-menu {
  display: flex;
  align-items: center;
  height: 100%;
  border-bottom: none;
}

.user-state {
  margin-left: auto;
  padding-right: 20px;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

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

/* ======================
   侧边栏样式 
   ====================== */
.sidebar {
  height: calc(100vh - 65px);
  background-color: white;
  box-shadow: 1px 0 4px rgba(0, 0, 0, 0.08);
  transition: width 0.3s;
  z-index: 5;
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

/* ======================
   主内容区样式 
   ====================== */
.main-content {
  padding: 0;
  overflow-y: auto;
  height: calc(100vh - 65px);
  background-color: #f9f9f9;
}

/* ======================
   AI助手容器样式 
   ====================== */
.ai-assistant-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 65px);
  width: calc(100% - 230px);
  background: white;
  overflow: hidden;
}

/* ======================
   聊天历史区域样式 
   ====================== */
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
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 20px;
}

.message-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-bubble {
  max-width: 80%;
  display: flex;
  gap: 12px;
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
  max-width: 800px;
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

/* ======================
   商品卡片区域样式 
   ====================== */
.products-container {
  margin-top: 10px;
  padding: 0 60px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  padding: 10px 0;
}

.product-card {
  width: 100%;
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.image-container {
  width: 100%;
  height: 240px;
  overflow: hidden;
}

.product-image {
  width: 100%;
  height: 100%;
  transition: transform 0.5s;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.image-error,
.image-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  background-color: #f5f5f5;
}

.product-info {
  padding: 12px;
}

.product-name {
  font-size: 14px;
  color: #333;
  line-height: 1.5;
  height: 42px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-shop {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
}

.product-shop .el-icon {
  margin-right: 4px;
}

.product-price {
  margin-top: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.current-price {
  color: #ff5000;
  font-size: 18px;
  font-weight: bold;
  margin-right: 8px;
}

.original-price {
  color: #999;
  font-size: 12px;
  text-decoration: line-through;
  margin-right: 8px;
}

.sales {
  color: #999;
  font-size: 12px;
}

/* ======================
   空状态样式 
   ====================== */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  text-align: center;
}

.empty-state h3 {
  margin: 10px 0 5px;
  color: #333;
  font-size: 1.2em;
}

.empty-state p {
  margin-bottom: 20px;
  color: #666;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 500px;
}

.quick-questions .el-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.quick-questions .el-tag:hover {
  background: #409eff;
  color: white;
}

/* ======================
   加载状态样式 
   ====================== */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  color: #666;
  font-size: 0.9em;
}

/* ======================
   输入区域样式 
   ====================== */
.input-area {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #f0f0f0;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.user-status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.username {
  font-size: 0.9em;
  font-weight: 500;
}

.input-hints small {
  color: #999;
  font-size: 0.75em;
}

.input-container {
  position: relative;
  display: flex;
  gap: 8px;
}

.message-input {
  flex: 1;
  font-size: 15px;
}

.message-input :deep(.el-textarea__inner) {
  padding-right: 100px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #e5e5e5;
  transition: all 0.2s;
}

.message-input :deep(.el-textarea__inner):focus {
  box-shadow: 0 0 0 1px var(--el-color-primary);
}

.action-buttons {
  position: absolute;
  right: 8px;
  bottom: 8px;
  display: flex;
  gap: 6px;
  align-items: center;
}

.clear-button {
  width: 32px;
  height: 32px;
  padding: 0;
}

.send-button {
  padding: 8px 16px;
  border-radius: 8px;
}

.input-footer {
  display: flex;
  justify-content: space-between;
  padding: 0 4px;
}

.input-footer small {
  color: #999;
  font-size: 0.75em;
}

/* ======================
   响应式设计 
   ====================== */
@media (max-width: 1200px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .sidebar {
    width: 200px;
  }

  .ai-assistant-container {
    width: calc(100% - 200px);
  }

  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 180px;
  }

  .ai-assistant-container {
    width: calc(100% - 180px);
  }

  .message-bubble {
    max-width: 90%;
  }

  .products-container {
    padding: 0 20px;
  }
}

@media (max-width: 600px) {
  .sidebar {
    width: 160px;
  }

  .ai-assistant-container {
    width: calc(100% - 160px);
  }

  .products-grid {
    grid-template-columns: 1fr;
  }

  .message-text {
    max-width: 100%;
  }
}

@media (max-width: 480px) {
  .header {
    height: 60px;
  }

  .sidebar {
    width: 0;
    position: absolute;
    left: 0;
    z-index: 10;
    height: calc(100vh - 60px);
  }

  .ai-assistant-container {
    width: 100%;
    height: calc(100vh - 60px);
  }

  .auth-buttons {
    gap: 5px;
  }

  .auth-button {
    padding: 8px 12px;
    font-size: 12px;
  }

  .message-input {
    font-size: 14px;
  }
}
</style>