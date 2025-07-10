<template>
  <div class="ai-assistant-container">
    <!-- 聊天历史区域 -->
    <MessageList 
      :messages="messages" 
      :chat-loading="chatLoading" 
      :user="user" 
      :logo="Zhigou_Logo"
      @quick-question="handleQuickQuestion"
    />
    
    <!-- 消息输入区域 -->
    <MessageInput 
      :modelValue="message" 
      :chat-loading="chatLoading" 
      @submit-message="handleSubmitMessage"
      @new-line="handleNewLine"
      :user="user"
      @update:modelValue="message = $event"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '@/api/auth'
import { useChat } from '@/api/chat'
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import Zhigou_Logo from '@/assets/logo.png'
import { ElMessage } from 'element-plus'

// 认证模块
const { user, visitorLogin } = useAuth()

// 聊天模块
const {
  messages,
  chatLoading,
  fetchConversations
} = useChat(user.value?.username)

// 消息内容
const message = ref('')

// 提交消息
const handleSubmitMessage = async () => {
  if (!message.value.trim()) return

  try {
    if (!user.value) {
      await visitorLogin()
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
    const reason = error.reason || error.message || '未知错误'
    ElMessage.error(`发送消息失败: ${reason}`)
  }
}

// 处理换行
const handleNewLine = () => {
  message.value += '\n'
}

// 快速提问
const handleQuickQuestion = (question) => {
  message.value = question
  handleSubmitMessage()
}

// 生成示例商品数据
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

// 组件挂载时获取对话列表
onMounted(async () => {
  if (user.value) {
    await fetchConversations()
  }
})
</script>

<style scoped>
.ai-assistant-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 65px);
  width: calc(100% - var(--sidebar-width));
  background: white;
  overflow: hidden;
}

/* 动态设置CSS变量 */
@media (max-width: 480px) { --sidebar-width: 0; }
@media (max-width: 600px) { --sidebar-width: 160px; }
@media (max-width: 768px) { --sidebar-width: 180px; }
@media (max-width: 900px) { --sidebar-width: 190px; }
@media (min-width: 900px) { --sidebar-width: 200px; }

.chat-history {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
</style>