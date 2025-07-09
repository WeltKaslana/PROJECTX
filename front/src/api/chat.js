// chat.js
import { ref } from 'vue';
import api from './api';

export const useChat = (username) => {
  const conversations = ref([]);
  const currentConversation = ref(null);
  const messages = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // 获取所有对话列表
  const fetchConversations = async () => {
    try {
      const response = await api.getHistoryCount(username);
      if (response.code === 200) {
        conversations.value = response.result.map(conv => ({
          id: conv.sessionId,
          title: new Date(conv.createdAt).toLocaleString(),
          createdAt: conv.createdAt
        })).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      }
    } catch (err) {
      error.value = err.reason || '获取对话列表失败';
    }
  };

  // 创建新对话
  const createNewChat = async () => {
    loading.value = true;
    error.value = null;
    try {
      // 清空当前消息
      messages.value = [];

      const response = await api.newConversation(username);
      if (response.code === 200) {
        currentConversation.value = `${username}_${response.result}`;
        // 创建成功后刷新对话列表
        await fetchConversations();
        return response;
      } else {
        throw { message: response.message, reason: response.reason };
      }
    } catch (err) {
      error.value = err.reason || '创建对话失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // 加载历史对话
  const loadHistory = async (sessionId) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.getHistory(sessionId);
      if (response.code === 200) {
        messages.value = response.result;
        currentConversation.value = sessionId;
        return response;
      } else {
        throw { message: response.message, reason: response.reason };
      }
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
    fetchConversations,
    loadHistory,
    searchKeywords
  };
};