<template>
  <div class="chat-history">
    <!-- 消息列表 -->
    <div v-if="messages && messages.length > 0" class="messages-container">
      <div v-for="(msg, index) in messages" :key="index" class="message-container">
        <!-- 消息气泡 -->
        <div class="message-bubble"
             :class="{ 'user-message': msg.role === 'user', 'ai-message': msg.role === 'assistant' }">
          <div class="message-avatar">
            <el-avatar v-if="msg.role === 'assistant'" :size="32" :src="logo" />
            <el-avatar v-else :size="32"
                       :src="user?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
          </div>
          <div class="message-content">
            <div class="message-role">
              {{ msg.role === 'assistant' ? 'AI助手' : user?.username || '游客' }}
              <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
            </div>
            <div class="message-text">{{ msg.content }}</div>
          </div>
        </div>

        <!-- 商品卡片区域 -->
        <div v-if="msg.products && msg.products.length" class="products-section">
          <div class="search-query" v-if="msg.searchQuery">
            搜索词: "{{ msg.searchQuery }}"
          </div>
          <div class="products-grid">
            <ProductCard v-for="(product, pIndex) in getVisibleProducts(msg.products, index)"
                         :key="`product-${index}-${pIndex}`" 
                         :product="product" />
          </div>
          <div class="load-more-container" v-if="hasMoreProducts(msg.products, index)">
            <el-button type="primary" 
                       size="small" 
                       @click="loadMoreProducts(index)"
                       :loading="loadingMore[index]" 
                       plain>
              加载更多 ({{ getRemainingCount(msg.products, index) }}条)
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-avatar :size="64" :src="logo" />
      <h3>我是您的AI购物助手</h3>
      <p>请问您想找什么商品？我可以帮您搜索和推荐</p>
      <div class="quick-questions">
        <el-tag v-for="(question, idx) in quickQuestions" 
                :key="idx" 
                @click="handleQuickQuestion(question)"
                class="question-tag">
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
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElAvatar, ElTag, ElIcon, ElButton } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import ProductCard from './ProductCard.vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  user: {
    type: Object,
    default: null
  },
  chatLoading: {
    type: Boolean,
    default: false
  },
  logo: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['quick-question'])

// 快速问题示例
const quickQuestions = ref([
  '最新手机推荐',
  '夏季女装优惠',
  '家用电器排行榜',
  '运动鞋哪个品牌好'
])

// 分页相关
const BATCH_SIZE = 16
const visibleCounts = ref({})
const loadingMore = ref({})

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

// 获取当前可见的商品
const getVisibleProducts = (products, msgIndex) => {
  const count = visibleCounts.value[msgIndex] || BATCH_SIZE
  return products.slice(0, count)
}

// 检查是否有更多商品
const hasMoreProducts = (products, msgIndex) => {
  const count = visibleCounts.value[msgIndex] || BATCH_SIZE
  return products.length > count
}

// 获取剩余商品数量
const getRemainingCount = (products, msgIndex) => {
  const count = visibleCounts.value[msgIndex] || BATCH_SIZE
  return products.length - count
}

// 加载更多商品
const loadMoreProducts = (msgIndex) => {
  loadingMore.value[msgIndex] = true
  setTimeout(() => {
    visibleCounts.value[msgIndex] = (visibleCounts.value[msgIndex] || BATCH_SIZE) + BATCH_SIZE
    loadingMore.value[msgIndex] = false
  }, 300)
}

// 处理快速提问
const handleQuickQuestion = (question) => {
  emit('quick-question', question)
}
</script>

<style scoped>
.chat-history {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: #f9f9f9;
}

.messages-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 20px;
}

.message-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-bubble {
  max-width: 85%;
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
  gap: 6px;
}

.user-message .message-content {
  align-items: flex-end;
}

.ai-message .message-content {
  align-items: flex-start;
}

.message-role {
  font-size: 0.85em;
  color: #666;
  display: flex;
  align-items: center;
  gap: 8px;
}

.message-time {
  font-size: 0.75em;
  color: #999;
}

.message-text {
  padding: 12px 16px;
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

/* 商品区域 */
.products-section {
  margin-top: 15px;
  padding: 0 20px;
  max-width: 1200px;
  width: 100%;
}

.search-query {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  padding-left: 8px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  padding: 5px 0;
}

.load-more-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  padding: 10px 0;
}

/* 空状态 */
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
  margin: 12px 0 6px;
  color: #333;
  font-size: 1.3em;
}

.empty-state p {
  margin-bottom: 24px;
  color: #666;
  font-size: 0.95em;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 500px;
}

.question-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.question-tag:hover {
  background: #409eff;
  color: white;
}

/* 加载状态 */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 15px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .products-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 900px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .message-bubble {
    max-width: 90%;
  }
}

@media (max-width: 768px) {
  .products-section {
    padding: 0 15px;
  }
}

@media (max-width: 600px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
  
  .chat-history {
    padding: 15px;
  }
  
  .message-text {
    max-width: 100%;
    padding: 10px 14px;
  }
}

@media (max-width: 480px) {
  .empty-state h3 {
    font-size: 1.2em;
  }
  
  .empty-state p {
    font-size: 0.9em;
  }
  
  .quick-questions {
    gap: 8px;
  }
}
</style>