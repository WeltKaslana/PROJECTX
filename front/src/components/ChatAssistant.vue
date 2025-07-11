<template>
  <div class="ai-assistant-container">
    <MessageList 
      :messages="messages" 
      :chat-loading="loading" 
      :user="user" 
      :logo="Zhigou_Logo"
      @quick-question="handleQuickQuestion"
    />
    
    <MessageInput 
      :modelValue="message" 
      :chat-loading="loading" 
      @submit-message="handleSubmitMessage"
      @new-line="handleNewLine"
      :user="user"
      @update:modelValue="message = $event"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/api/auth'
import { useChat } from '@/api/chat'
import MessageList from './MessageList.vue'
import MessageInput from './MessageInput.vue'
import Zhigou_Logo from '@/assets/logo.png'
import { ElMessage } from 'element-plus'

const { user, visitorLogin } = useAuth()
const {
  messages,
  loading,
  error,
  fetchConversations,
  currentConversation,
  searchKeywords,
  createNewChat,
  fetchCurrentConversation
} = useChat(user.value?.username)

const message = ref('')

const ensureConversation = async () => {
  if (!currentConversation.value) {
    await fetchCurrentConversation()
    if (!currentConversation.value) {
      await createNewChat()
      ElMessage.success('已创建新会话')
    }
  }
}

const handleSubmitMessage = async () => {
  if (!message.value.trim()) {
    ElMessage.warning('请输入搜索内容');
    return;
  }

  try {
    // 1. 确保用户已登录和会话有效
    if (!user.value) await visitorLogin();
    if (!currentConversation.value) await ensureConversation();

    // 2. 添加用户消息
    messages.value.push({
      role: 'user',
      content: message.value,
      timestamp: new Date().toISOString()
    });

    // 3. 清空输入框
    const question = message.value;
    message.value = '';

    // 4. 执行搜索（会分两步响应）
    await searchKeywords(currentConversation.value, question);
    
  } catch (error) {
    ElMessage.error(`处理失败: ${error.message}`);
    // 移除加载中的消息（如果有）
    messages.value = messages.value.filter(m => !m.isLoading);
  }
};

const parseProductData = (apiData) => {
  if (!apiData || !Array.isArray(apiData)) return []
  
  return apiData.map((item, index) => ({
    id: `${item.page || 0}_${item.position || index}`,
    name: item.name || item.title || '未知商品',
    price: formatPrice(item.price || item.Price),
    originalPrice: null,
    image: validateImageUrl(item.img_url || item.Img_URL),
    shop: item.shop || item.Shop || '未知店铺',
    sales: formatSales(item.deals || item.Deal),
    link: validateUrl(item.goods_url || item.Title_URL),
    shopLink: validateUrl(item.shop_url || item.Shop_URL),
    location: item.location || item.Location || '',
    isPostFree: item.isPostFree === true || item.IsPostFree === '是',
    page: item.page || 1,
    position: item.position || index + 1
  }))
}

const formatPrice = (price) => {
  if (!price) return '0.00'
  if (!isNaN(price)) return Number(price).toFixed(2)
  return price.replace(/[^\d.]/g, '')
}

const formatSales = (deal) => {
  if (!deal) return 0
  const num = parseInt(deal.replace(/[^\d]/g, ''))
  return isNaN(num) ? 0 : num
}

const validateImageUrl = (url) => {
  if (!url) return 'https://via.placeholder.com/300'
  
  // 处理淘宝图片
  if (url.includes('alicdn.com')) {
    return `https:${url.replace(/^\/\//, '')}`.replace(/\.webp$/, '.jpg')
  }
  
  return url.startsWith('http') ? url : `https://${url}`
}

const validateUrl = (url) => {
  if (!url) return '#'
  
  // 处理淘宝链接
  if (url.includes('tmall.com') || url.includes('taobao.com')) {
    return `https:${url.replace(/^\/\//, '')}`
  }
  
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
    try {
      await fetchConversations()
      await ensureConversation()
    } catch (err) {
      ElMessage.error(`初始化失败: ${err.message}`)
    }
  }
})
</script>

<style scoped>
/* 原有样式保持不变 */
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