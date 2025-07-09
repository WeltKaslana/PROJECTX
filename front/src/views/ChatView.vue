<template>
  <div class="chat-container">
    <!-- 聊天头部 -->
    <div class="chat-header">
      <h3>智能助手</h3>
      <div class="chat-info">
        <span v-if="user">当前用户: {{ user.username }}</span>
        <el-tag v-if="user && user.isVisitor" type="info" size="small">游客</el-tag>
      </div>
    </div>

    <!-- 消息列表区域 -->
    <div class="message-list" ref="messageListRef">
      <!-- 加载历史消息提示 -->
      <div v-if="loadingHistory" class="loading-history">
        <el-loading-spinner size="small"></el-loading-spinner>
        <span>加载历史消息...</span>
      </div>

      <!-- 消息气泡 -->
      <div 
        v-for="(msg, index) in displayedMessages" 
        :key="index" 
        :class="['message-item', msg.isUser ? 'user-message' : 'ai-message']"
      >
        <div class="message-content">
          <div class="message-bubble" v-html="parseMessageContent(msg.content)"></div>
          <div class="message-time">{{ formatMessageTime(msg.timestamp) }}</div>
        </div>
      </div>

      <!-- 底部空白区域，用于滚动定位 -->
      <div class="scroll-anchor" ref="scrollAnchorRef"></div>
    </div>

    <!-- 输入区域 -->
    <div class="input-area">
      <el-input
        v-model="message"
        placeholder="请输入您的问题..."
        class="message-input"
        type="textarea"
        :rows="1"
        @keydown.enter.exact="handleSubmitMessage"
        @input="adjustTextareaHeight"
      ></el-input>
      <el-button 
        type="primary" 
        class="send-button" 
        @click="handleSubmitMessage"
        :disabled="!message.trim() || chatLoading"
        :loading="chatLoading"
      >
        发送
      </el-button>
    </div>
  </div>
</template>

<script setup>
// 保持原有代码不变
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
}

.chat-header {
  padding: 15px 20px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-info {
  font-size: 13px;
  color: #606266;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
}

.message-item {
  display: flex;
  margin-bottom: 20px;
  max-width: 90%;
}

.user-message {
  align-self: flex-end;
  justify-content: flex-end;
}

.ai-message {
  align-self: flex-start;
}

.message-content {
  max-width: 100%;
}

.message-bubble {
  padding: 10px 15px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.6;
  display: inline-block;
  max-width: 100%;
}

.user-message .message-bubble {
  background-color: #409eff;
  color: white;
}

.ai-message .message-bubble {
  background-color: #f0f2f5;
  color: #303133;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  text-align: right;
}

.user-message .message-time {
  text-align: right;
}

.ai-message .message-time {
  text-align: left;
}

.loading-history {
  text-align: center;
  padding: 10px;
  color: #909399;
  font-size: 13px;
}

.input-area {
  padding: 15px 20px;
  background-color: #f5f7fa;
  border-top: 1px solid #ebeef5;
  position: relative;
}

.message-input {
  padding-right: 60px !important;
  resize: none;
  max-height: 100px;
}

.send-button {
  position: absolute;
  right: 25px;
  bottom: 20px;
  height: 32px;
  border-radius: 4px;
}

.scroll-anchor {
  margin-bottom: 10px;
}
</style>