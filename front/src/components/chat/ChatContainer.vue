<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ChatHistory from './ChatHistory.vue'
import ChatInput from './ChatInput.vue'
import ChatSidebar from './ChatSidebar.vue'

const route = useRoute()
const excludedPaths = ['/help', '/settings', '/about', '/login', '/register', '/test']
const showChatBox = computed(() => !excludedPaths.includes(route.path))
</script>

<template>
  <div v-if="showChatBox" class="chat-container">
    <ChatSidebar />
    <div class="chat-content">
      <ChatHistory />
      <ChatInput />
    </div>
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/chat/_container.scss';
</style>