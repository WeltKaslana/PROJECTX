// chat.js
import { ref } from 'vue';
import api from './api';

export const useChat = (username) => {
  const conversations = ref([]);
  const currentConversation = ref(null);
  const messages = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const createNewChat = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.newConversation(username);
      currentConversation.value = `${username}_${response.result}`;
      return response;
    } catch (err) {
      error.value = err.reason || '创建对话失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const getHistoryCount = async () => {
    loading.value = true;
    try {
      return await api.getHistoryCount(username);
    } finally {
      loading.value = false;
    }
  };

  const loadHistory = async (sessionId) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.getHistory(sessionId);
      messages.value = response.result;
      return response;
    } catch (err) {
      error.value = err.reason || '加载历史记录失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const searchKeywords = async (question) => {
    if (!currentConversation.value) return;
    
    loading.value = true;
    error.value = null;
    try {
      const response = await api.searchKeywords(
        currentConversation.value, 
        question
      );
      messages.value.push({
        question,
        answer: response.result
      });
      return response;
    } catch (err) {
      error.value = err.reason || '搜索失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    conversations,
    currentConversation,
    messages,
    loading,
    error,
    createNewChat,
    getHistoryCount,
    loadHistory,
    searchKeywords
  };
};