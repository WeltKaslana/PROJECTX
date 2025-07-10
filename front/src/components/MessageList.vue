<template>
  <div class="chat-history">
    <div v-if="messages.length > 0" class="messages-container">
      <div v-for="(msg, index) in messages" :key="index" class="message-container">
        <!-- 消息气泡部分 -->
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
              <span class="message-time">{{ new Date().toLocaleTimeString() }}</span>
            </div>
            <div class="message-text">{{ msg.content }}</div>
          </div>
        </div>

        <!-- 商品卡片展示区域 -->
        <div v-if="msg.products && msg.products.length" class="products-container">
          <div class="products-grid">
            <ProductCard v-for="(product, pIndex) in msg.products" :key="`product-${pIndex}`" :product="product" />
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
        <el-tag v-for="(question, idx) in [
          '最新手机推荐',
          '夏季女装优惠',
          '家用电器排行榜',
          '运动鞋哪个品牌好'
        ]" :key="idx" @click="$emit('quick-question', question)">
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
import { Loading } from '@element-plus/icons-vue'
import ProductCard from './ProductCard.vue'

const props = defineProps({
  messages: {
    type: Array,
    required: true,
    default: () => []
  },
  chatLoading: {
    type: Boolean,
    default: false
  },
  user: {
    type: Object,
    default: null
  },
  logo: {
    type: String,
    required: true
  }
})

defineEmits(['quick-question'])
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

/* 商品展示区域 */
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

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
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

.empty-state > * {
  margin: 12px 0;
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

/* 加载状态样式 */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  color: #666;
  font-size: 0.9em;
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
  }
}

@media (max-width: 768px) {
  .message-bubble {
    max-width: 90%;
  }

  .products-container {
    padding: 0 20px;
  }
}

@media (max-width: 600px) {
  .products-grid {
    grid-template-columns: 1fr;
  }

  .message-text {
    max-width: 100%;
  }
}
</style>