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
  ElTooltip,
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
