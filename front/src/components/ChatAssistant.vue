<template>
  <div class="ai-assistant-container">
    <MessageList 
      :messages="messages" 
      :chat-loading="chatLoading" 
      :user="user" 
      :logo="Zhigou_Logo"
      @quick-question="handleQuickQuestion"
    />
    
    <MessageInput 
      :modelValue="message" 
      :chat-loading="chatLoading" 
      :agent-error="agentError?.value || ''"
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
import { useAgent } from '@/api/agent'
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import Zhigou_Logo from '@/assets/logo.png'
import { ElMessage } from 'element-plus'

const { user, visitorLogin } = useAuth()
// const {
//   messages,
//   chatLoading,
//   fetchConversations
// } = useChat(user.value?.username)
const chat = useChat(user.value?.username)
const messages = chat.messages
const chatLoading = chat.chatLoading
const { fetchConversations } = chat


// Agent模块 - 安全解构
const agent = useAgent()
const agentLoading = agent.loading
const agentError = agent.error
const { sendMessageToAgent } = agent

const message = ref('')

// 合并加载状态 - 安全访问
const isLoading = computed(() => {
  // 安全访问 ref 对象的 value 属性
  const chatVal = chatLoading?.value ?? false
  const agentVal = agentLoading?.value ?? false
  return chatVal || agentVal
})

const handleSubmitMessage = async () => {
  if (!message.value.trim()) return

  try {
    if (!user.value) {
      await visitorLogin()
    }

    chatLoading.value = true
    
    // 添加用户消息到列表
    const userMsg = {
      role: 'user',
      content: message.value,
      timestamp: new Date().toISOString()
    }
    messages.value.push(userMsg)
    
    // 清空输入框
    const userMessage = message.value
    message.value = ''

    // 调用agent接口
    const agentResponse = await sendMessageToAgent({
      message: userMessage,
      conversationId: null // 实际使用中应传入当前对话ID
    })

    // 调用后端API获取搜索结果
    const response = await fetch(
      `/keywords/${user.value.username}_${user.value.currentSession}/${encodeURIComponent(message.value)}`
    )
    
    if (!response.ok) {
      throw new Error(`请求失败: ${response.status}`)
    }

    const data = await response.json()
    
    if (data.code !== 200) {
      throw new Error(data.reason || '获取搜索结果失败')
    }

    // 解析商品数据
    const searchResults = {
      text: `为您找到以下关于"${message.value}"的商品：`,
      products: parseProductData(data.result),
      searchQuery: message.value
    }

    messages.value.push({
      role: 'assistant',
      content: searchResults.text,
      products: searchResults.products,
      timestamp: new Date().toISOString(),
      searchQuery: searchResults.searchQuery
    })

    message.value = ''
  } catch (error) {
    ElMessage.error(`搜索失败: ${error.message}`)
    let reason = error.reason || error.message || '未知错误'
    
    // 添加agent错误消息
    messages.value.push({
      role: 'assistant',
      content: `处理您的请求时出错: ${reason}`,
      timestamp: new Date().toISOString()
    })
    
    // 更新错误状态
    if (agentError) {
      agentError.value = reason
    }
    
    ElMessage.error(`发送消息失败: ${reason}`)
  } finally {
    chatLoading.value = false
  }
}

// 解析后端商品数据
const parseProductData = (apiData) => {
  if (!apiData || !Array.isArray(apiData)) return []
  
  return apiData.map((item, index) => ({
    id: `${item.Page || 0}_${item.Num || index}`,
    name: item.title || '未知商品',
    price: formatPrice(item.Price),
    originalPrice: null,
    image: validateImageUrl(item.Img_URL),
    shop: item.Shop || '未知店铺',
    sales: formatSales(item.Deal),
    link: validateUrl(item.Title_URL),
    shopLink: validateUrl(item.Shop_URL),
    location: item.Location || '',
    isPostFree: item.IsPostFree === '是',
    page: item.Page || 1,
    position: item.Num || index + 1
  }))
}

// 辅助函数：格式化价格
const formatPrice = (price) => {
  if (!price) return '0.00'
  // 如果已经是数字格式，直接返回
  if (!isNaN(price)) return Number(price).toFixed(2)
  // 去除可能的货币符号
  return price.replace(/[^\d.]/g, '')
}

// 辅助函数：格式化销量
const formatSales = (deal) => {
  if (!deal) return 0
  const num = parseInt(deal.replace(/[^\d]/g, ''))
  return isNaN(num) ? 0 : num
}

// 辅助函数：验证图片URL
const validateImageUrl = (url) => {
  if (!url) return 'https://via.placeholder.com/300'
  return url.startsWith('http') ? url : 'https://via.placeholder.com/300'
}

// 辅助函数：验证普通URL
const validateUrl = (url) => {
  if (!url) return '#'
  return url.startsWith('http') ? url : '#'
}

const handleNewLine = () => {
  message.value += '\n'
}

const handleQuickQuestion = (question) => {
  message.value = question
  handleSubmitMessage()
}

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

:root {
  --sidebar-width: 200px;
}

@media (max-width: 900px) {
  :root { --sidebar-width: 190px; }
}
@media (max-width: 768px) {
  :root { --sidebar-width: 180px; }
}
@media (max-width: 600px) {
  :root { --sidebar-width: 160px; }
}
@media (max-width: 480px) {
  :root { --sidebar-width: 0; }
}
</style>