<script setup>
import { computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import ChatProductCard from './ChatProductCard.vue'

const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const { user } = useAuth()
const isAssistant = computed(() => props.message.role === 'assistant')
</script>

<template>
  <div class="message-container">
    <div class="message-bubble" :class="{ 'user-message': !isAssistant, 'ai-message': isAssistant }">
      <!-- 消息内容 -->
    </div>
    
    <div v-if="message.products?.length" class="products-container">
      <div class="products-grid">
        <ChatProductCard 
          v-for="(product, pIndex) in message.products" 
          :key="`product-${pIndex}`" 
          :product="product" 
        />
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/chat/_message.scss';
</style>