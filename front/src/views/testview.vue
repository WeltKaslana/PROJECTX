<template>
  <div class="chat-container">
    <!-- 消息列表 -->
    <div class="messages">
      <div v-for="(msg, index) in messages" :key="index" class="message">
        <div class="message-content" :class="msg.role">
          {{ msg.content }}
        </div>
        
        <!-- 商品卡片区域 -->
        <div v-if="msg.products" class="products-wrapper">
          <div class="products-grid">
            <div v-for="(product, pIndex) in msg.products" :key="pIndex" class="product-card">
              <img :src="product.image" class="product-image" />
              <div class="product-name">{{ product.name }}</div>
              <div class="product-price">¥{{ product.price }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 输入区域 -->
    <div class="input-area">
      <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="输入消息..." />
      <button @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const newMessage = ref('');
const messages = ref([
  {
    role: 'assistant',
    content: '您好！我是购物助手，请问您想找什么商品？',
    products: [
      {
        id: 1,
        name: '示例商品1',
        price: '299.00',
        image: 'https://picsum.photos/200/200?random=1'
      },
      {
        id: 2,
        name: '示例商品2',
        price: '399.00',
        image: 'https://picsum.photos/200/200?random=2'
      },
      {
        id: 3,
        name: '示例商品3',
        price: '499.00',
        image: 'https://picsum.photos/200/200?random=3'
      },
      {
        id: 4,
        name: '示例商品4',
        price: '599.00',
        image: 'https://picsum.photos/200/200?random=4'
      }
    ]
  }
]);

const sendMessage = () => {
  if (!newMessage.value.trim()) return;
  
  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: newMessage.value
  });
  
  // 模拟AI回复
  setTimeout(() => {
    messages.value.push({
      role: 'assistant',
      content: `这是关于"${newMessage.value}"的搜索结果：`,
      products: generateProducts(newMessage.value)
    });
  }, 500);
  
  newMessage.value = '';
};

const generateProducts = (keyword) => {
  return Array.from({length: 4}, (_, i) => ({
    id: i + 1,
    name: `${keyword} 商品 ${i + 1}`,
    price: (Math.random() * 500 + 100).toFixed(2),
    image: `https://picsum.photos/200/200?random=${i}`
  }));
};
</script>

<style>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

.messages {
  margin-bottom: 20px;
}

.message {
  margin-bottom: 20px;
}

.message-content {
  padding: 10px 15px;
  border-radius: 18px;
  margin-bottom: 10px;
  max-width: 70%;
}

.message-content.user {
  background: #409eff;
  color: white;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}

.message-content.assistant {
  background: #f1f1f1;
  margin-right: auto;
  border-bottom-left-radius: 4px;
}

.products-wrapper {
  margin-top: 10px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
}

.product-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.product-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.product-name {
  padding: 8px;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-price {
  padding: 0 8px 8px;
  color: #ff5000;
  font-weight: bold;
}

.input-area {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.input-area input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.input-area button {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>