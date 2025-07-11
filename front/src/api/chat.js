import { ref } from 'vue';
import api from './api';

export const useChat = (username) => {
  const conversations = ref([]);
  const currentConversation = ref(null);
  const messages = ref([]);
  const loading = ref(false);
  const error = ref(null);

  // 获取当前会话
  const fetchCurrentConversation = async () => {
    try {
      if (!username) throw new Error('用户名不存在');
      
      const response = await api.getHistoryCount(username);
      console.log('获取历史会话响应:', response);

      if (response.code === 200) {
        // 处理数组或对象格式的响应
        currentConversation.value = Array.isArray(response.result) 
          ? response.result[0]?.sessionId 
          : response.result?.sessionId;
        
        if (!currentConversation.value) {
          console.warn('未获取到有效会话ID');
        }
        return currentConversation.value;
      }
      throw new Error(response.reason || '获取会话失败');
    } catch (err) {
      error.value = err.message;
      console.error('获取当前会话失败:', err);
      throw err;
    }
  };

  // 创建新会话
  const createNewChat = async () => {
    try {
      loading.value = true;
      const response = await api.newConversation(username);
      console.log('创建会话响应:', response);

      if (response.code === 200) {
        currentConversation.value = response.result;
        if (!currentConversation.value) {
          throw new Error('未返回有效会话ID');
        }
        await fetchConversations();
        return currentConversation.value;
      }
      throw new Error(response.reason || '创建会话失败');
    } catch (err) {
      error.value = err.message;
      console.error('创建会话失败:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };

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

  // 其他方法保持不变...
  return {
    conversations,
    currentConversation,
    messages,
    loading,
    error,
    fetchCurrentConversation,
    createNewChat,
    searchKeywords,
    // ...其他方法
  };
};