import axios from 'axios';

const api = axios.create({
  baseURL: 'http://172.20.10.8:8080',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器
api.interceptors.request.use(config => {
  console.log('请求参数:', config);
  return config;
}, error => {
  return Promise.reject(error);
});

// 响应拦截器
api.interceptors.response.use(
  response => {
    const res = response.data;
    // 标准化响应格式
    return {
      code: res.code || 200,
      message: res.message || 'success',
      result: res.result ?? res.data,
      timestamp: Date.now()
    };
  },
  error => {
    console.error('API错误:', error);
    return Promise.reject({
      code: error.response?.status || 500,
      message: error.response?.data?.message || '网络错误',
      reason: error.response?.data?.reason || error.message
    });
  }
);

export default {
  // 用户认证
  visitorLogin() {
    return api.post('/visitor/login');
  },
  
  // 会话管理
  createConversation(username) {
    return api.post('/conversations', { username });
  },
  
  getConversations(username) {
    return api.get(`/conversations?username=${username}`);
  },

  // 消息交互
  sendQuickReply(sessionId, question) {
    return api.get(`/quick-reply/${sessionId}/${encodeURIComponent(question)}`);
  },

  fetchProducts(sessionId) {
    return api.get(`/products/${sessionId}`);
  },

  // 搜索功能
  searchKeywords(sessionId, question) {
    return api.post('/search', {
      session_id: sessionId,
      question: question
    });
  }
};