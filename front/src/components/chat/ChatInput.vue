<script setup>
import { ref } from 'vue'
import { useChat } from '@/composables/useChat'
import { useAuth } from '@/composables/useAuth'

const message = ref('')
const { chatLoading, handleSubmitMessage } = useChat()
const { user } = useAuth()

const handleNewLine = () => {
  message.value += '\n'
}
</script>

<template>
  <div class="input-area">
    <!-- 输入区域结构 -->
  </div>
</template>

<style scoped lang="scss">
@import '@/styles/chat/_input.scss';
</style>