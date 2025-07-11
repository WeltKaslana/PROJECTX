import { ref } from 'vue';
import api from './api';

export const useChat = (username) => {
  const state = ref({
    conversations: [],
    currentConversation: null,
    messages: [],
    loading: false,
    error: null
  });

  // 创建新会话
  const createNewChat = async () => {
    try {
      state.value.loading = true;
      const res = await api.createConversation(username);
      
      if (res.code === 200) {
        state.value.currentConversation = res.result.session_id;
        await fetchConversations();
        return res.result;
      }
      throw new Error(res.reason || '创建失败');
    } finally {
      state.value.loading = false;
    }
  };

  // 获取会话列表
  const fetchConversations = async () => {
    try {
      const res = await api.getConversations(username);
      if (res.code === 200) {
        state.value.conversations = res.result.map(conv => ({
          id: conv.session_id,
          title: conv.title || `对话 ${new Date(conv.created_at).toLocaleDateString()}`,
          createdAt: conv.created_at
        }));
        
        // 如果没有当前会话，设置第一个为当前
        if (!state.value.currentConversation && res.result.length > 0) {
          state.value.currentConversation = res.result[0].session_id;
        }
      }
    } catch (err) {
      state.value.error = err;
    }
  };

  // 分步搜索流程
  const searchKeywords = async (sessionId, question) => {
    try {
      state.value.loading = true;
      
      // 步骤1：快速文本回复
      const quickRes = await api.sendQuickReply(sessionId, question);
      if (quickRes.code !== 200) throw new Error(quickRes.reason);

      // 添加临时消息
      const tempMsg = {
        role: 'assistant',
        content: quickRes.result.message,
        timestamp: new Date().toISOString(),
        isLoading: true,
        tempId: Date.now() // 用于后续定位
      };
      state.value.messages.push(tempMsg);

      // 步骤2：异步获取商品数据
      const fetchProducts = async () => {
        try {
          const productRes = await api.fetchProducts(sessionId);
          if (productRes.code === 200) {
            // 替换临时消息
            const index = state.value.messages.findIndex(m => m.tempId === tempMsg.tempId);
            if (index !== -1) {
              state.value.messages[index] = {
                role: 'assistant',
                content: quickRes.result.message,
                products: parseProductData(productRes.result),
                timestamp: new Date().toISOString()
              };
            }
          }
        } catch (err) {
          console.error('商品加载失败:', err);
        }
      };

      // 延迟1秒获取商品（模拟后台处理）
      setTimeout(fetchProducts, 1000);

      return quickRes;
    } catch (err) {
      state.value.error = err;
      throw err;
    } finally {
      state.value.loading = false;
    }
  };

  // 商品数据解析
  const parseProductData = (items) => {
    return items?.map(item => ({
      id: item.id || `${item.page}_${item.position}`,
      name: item.name || item.title,
      price: item.price || 0,
      image: formatImageUrl(item.img_url || item.image),
      shop: item.shop || '官方旗舰店',
      sales: formatSales(item.deals || item.sales),
      link: formatProductLink(item.goods_url || item.link),
      isPostFree: !!item.free_shipping
    })) || [];
  };

  // 辅助方法
  const formatImageUrl = (url) => {
    if (!url) return '';
    return url.startsWith('http') ? url : `https:${url}`;
  };

  const formatSales = (sales) => {
    const num = parseInt(sales) || 0;
    return num > 10000 ? `${(num/10000).toFixed(1)}万` : num;
  };

  const formatProductLink = (link) => {
    return link?.startsWith('http') ? link : `https:${link}`;
  };

  return {
    ...state.value,
    createNewChat,
    fetchConversations,
    searchKeywords
  };
};