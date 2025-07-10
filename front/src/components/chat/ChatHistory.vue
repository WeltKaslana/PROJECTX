<script setup>
import { useChat } from '@/composables/useChat'
import ChatMessage from './ChatMessage.vue'
import ChatProductCard from './ChatProductCard.vue'

const { messages, chatLoading } = useChat()
</script>

<template>
  <div class="chat-history">
    <div v-if="messages.length > 0" class="messages-container">
      <ChatMessage 
        v-for="(msg, index) in messages" 
        :key="index" 
        :message="msg" 
      />
    </div>
    
    <div v-else class="empty-state">
      <!-- 空状态内容 -->
    </div>
    
    <div v-if="chatLoading" class="loading-indicator">
      <!-- 加载指示器 -->
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/chat/_history.scss';
</style>