<template>
    <div class="input-area">
        <div class="user-status-bar">
            <div class="user-info">
                <el-avatar :size="24"
                    :src="user?.avatar || 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'" />
                <span class="username">{{ user?.username || '游客' }}</span>
                <el-tag v-if="!user || user.isVisitor" type="info" size="small">
                    {{ user?.isVisitor ? '游客' : '游客模式' }}
                </el-tag>
            </div>
            <div class="input-hints">
                <small>按Enter发送，Shift+Enter换行</small>
            </div>
        </div>

        <div class="input-container">
            <el-input ref="inputRef" v-model="inputValue" placeholder="请输入您想找的商品或问题..." type="textarea" :rows="2"
                resize="none" @keydown="handleKeydown" class="message-input" :disabled="chatLoading"
                @focus="handleFocus" @blur="handleBlur" />
            <div class="action-buttons">
                <el-tooltip content="清空输入" placement="top">
                    <el-button circle :disabled="!inputValue.trim() || chatLoading" @click="clearMessage"
                        class="clear-button">
                        <el-icon>
                            <Delete />
                        </el-icon>
                    </el-button>
                </el-tooltip>
                <el-button type="primary" @click="emit('submit-message')" 
                    :disabled="!inputValue.trim() || chatLoading || agentLoading"
                    :loading="chatLoading" class="send-button">
                    发送
                    <el-icon class="el-icon--right">
                        <Promotion />
                    </el-icon>
                </el-button>
            </div>
        </div>

        <div class="input-footer">
            <small>AI助手可能会出错，请核对重要信息</small>
            <small v-if="chatLoading">AI正在思考中，请稍候...</small>
            <!-- 新增agent错误提示 -->
            <small v-if="agentError" class="agent-error">
                助手服务异常: {{ agentError }}
            </small>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Delete, Promotion } from '@element-plus/icons-vue'

const props = defineProps({
    modelValue: {
        type: String,
        required: true,
        default: ''
    },
    chatLoading: {
        type: Boolean,
        default: false
    },
    agentLoading: {  // 新增agent加载状态
        type: Boolean,
        default: false
    },
    agentError: {    // 新增agent错误信息
        type: String,
        default: ''
    },
    user: {
        type: Object,
        default: null
    },
    resetInput: {  // 新增prop，用于父组件触发清空
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['update:modelValue', 'submit-message', 'new-line'])

const inputRef = ref(null)
const inputValue = ref(props.modelValue)
const isFocused = ref(false)

// 同步父组件的值变化
watch(() => props.modelValue, (newVal) => {
    inputValue.value = newVal
})

// 监听agent错误变化
watch(() => props.agentError, (newError) => {
    if (newError) {
        // 当有错误时自动滚动到底部以便用户看到
        nextTick(() => {
            const container = document.querySelector('.chat-history')
            if (container) {
                container.scrollTop = container.scrollHeight
            }
        })
    }
})

// 更新父组件的值
watch(inputValue, (newVal) => {
    emit('update:modelValue', newVal)
})

// 清空输入
const clearMessage = () => {
    inputValue.value = ''
    focusInput()
}

// 处理键盘事件
// const handleKeydown = (e) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//         e.preventDefault()
//         emit('submit-message')
//     }
// }
const handleKeydown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        emit('submit-message')
    } else if (e.key === 'Enter' && e.shiftKey) {
        e.preventDefault()
        emit('new-line')
    }
}

// 处理获取焦点
const handleFocus = () => {
    isFocused.value = true
    // 确保文本可见
    nextTick(() => {
        const textarea = inputRef.value?.textarea
        if (textarea) {
            textarea.style.opacity = '1'
            textarea.style.transform = 'none'
        }
    })
}

// 处理失去焦点
const handleBlur = () => {
    isFocused.value = false
}

// 聚焦输入框
const focusInput = () => {
    nextTick(() => {
        inputRef.value?.focus()
    })
}
</script>

<style scoped>
.input-area {
    padding: 12px 16px;
    background: white;
    border-top: 1px solid #f0f0f0;
    box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.05);
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.user-status-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 4px;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 8px;
}

.username {
    font-size: 0.9em;
    font-weight: 500;
}

.input-hints small {
    color: #999;
    font-size: 0.75em;
}

.input-container {
    position: relative;
    display: flex;
    gap: 8px;
}

.message-input {
    flex: 1;
    font-size: 15px;
}

/* 关键修复样式 */
.message-input :deep(.el-textarea__inner) {
    padding-right: 100px;
    border-radius: 12px;
    box-shadow: 0 0 0 1px #e5e5e5;
    transition: all 0.2s;
    opacity: 1 !important;
    /* 确保始终可见 */
    transform: none !important;
    /* 防止任何变换影响显示 */
}

.message-input :deep(.el-textarea__inner):focus {
    box-shadow: 0 0 0 1px var(--el-color-primary);
    opacity: 1 !important;
}

.action-buttons {
    position: absolute;
    right: 8px;
    bottom: 8px;
    display: flex;
    gap: 6px;
    align-items: center;
}

.clear-button {
    width: 32px;
    height: 32px;
    padding: 0;
}

.send-button {
    padding: 8px 16px;
    border-radius: 8px;
}

.input-footer {
    display: flex;
    justify-content: space-between;
    padding: 0 4px;
}

.input-footer small {
    color: #999;
    font-size: 0.75em;
}

/* 新增agent错误提示样式 */
.agent-error {
    color: #ff4d4f;
    font-weight: 500;
    margin-top: 4px; /* 与上方内容保持距离 */
}

@media (max-width: 480px) {
    .message-input {
        font-size: 14px;
    }

    .input-footer {
        flex-direction: column;
        align-items: flex-start;
    }
}
</style>