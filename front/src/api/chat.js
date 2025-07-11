import { ref } from 'vue'
import api from './api'

export const useChat = (username) => {
  const conversations = ref([])
  const currentConversation = ref(null)
  const messages = ref([])
  const loading = ref(false)
  const error = ref(null)




  const fetchCurrentConversation = async () => {
    try {
      if (!username) throw new Error('用户名不存在');

      const response = await api.getHistoryCount(username);
      console.log('getHistoryCount response:', response);

      if (response.code === 200) {
        // 修复点1：正确处理数组和对象两种响应格式
        const firstSession = Array.isArray(response.result)
          ? response.result[0]?.sessionId
          : response.result?.sessionId;

        // 修复点2：添加默认值处理
        currentConversation.value = firstSession || null;

        if (!currentConversation.value) {
          console.warn('No valid session found, will create new one');
        }
        return currentConversation.value;
      }
      throw new Error(response.reason || '获取当前对话失败');
    } catch (err) {
      console.error('fetchCurrentConversation error:', err);
      throw err;
    }
  };

  const createNewChat = async () => {
    try {
      loading.value = true;
      const response = await api.newConversation(username);
      console.log('createNewChat response:', response);

      // 修复点3：统一result处理逻辑
      currentConversation.value = response.result || null;

      if (!currentConversation.value) {
        throw new Error('创建会话失败：未返回有效sessionId');
      }

      await fetchConversations();
      return currentConversation.value;
    } catch (err) {
      console.error('createNewChat error:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await api.getHistoryCount(username);
      if (response.code === 200) {
        // 修复点4：确保总是更新currentConversation
        const sessions = Array.isArray(response.result)
          ? response.result
          : [response.result];

        if (sessions.length > 0 && !currentConversation.value) {
          currentConversation.value = sessions[0].sessionId;
        }

        conversations.value = sessions.map(s => ({
          id: s.sessionId,
          title: new Date(s.createdAt).toLocaleString(),
          createdAt: s.createdAt
        })).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
      }
    } catch (err) {
      console.error('fetchConversations error:', err);
    }
  };

  const loadHistory = async (sessionId) => {
    try {
      loading.value = true
      const response = await api.getHistory(sessionId)
      if (response.code === 200) {
        messages.value = response.result
        currentConversation.value = sessionId
        return messages.value
      }
      throw new Error(response.reason || '加载历史记录失败')
    } catch (err) {
      error.value = err.reason || '加载历史记录失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 关键词搜索
  const searchKeywords = async (sessionId, question) => {
    try {
      console.log('搜索参数:', { sessionId, question });

      if (!sessionId) throw new Error('会话ID不存在');
      if (!question) throw new Error('搜索内容不能为空');

      loading.value = true;
      const response = await api.searchKeywords(sessionId, question);
      console.log('搜索响应:', response);

      if (response.code !== 200) {
        throw new Error(response.reason || '搜索失败');
      }

      // 标准化消息格式
      const searchResult = {
        role: 'assistant',
        content: response.result.tip || '为您找到以下结果:',
        products: response.result.result || [],
        timestamp: new Date().toISOString()
      };

      messages.value.push(searchResult);
      return response;
    } catch (err) {
      error.value = err.message;
      console.error('搜索失败:', err);
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
    searchKeywords,
    fetchCurrentConversation
  }
}