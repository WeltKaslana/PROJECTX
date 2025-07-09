import axios from 'axios';

const api = axios.create({
  baseURL: 'http://172.20.10.8:8080', // 后端API地址
  timeout: 5000
});

// 优化后的响应拦截器
api.interceptors.response.use(
  response => {
    // 直接返回response.data，保持与后端一致的结构
    return response.data;
  },
  error => {
    // 如果有响应数据，则返回它
    if (error.response && error.response.data) {
      return Promise.reject(error.response.data);
    }
    // 如果是网络错误等没有response的情况
    return Promise.reject({
      code: error.code || 500,
      message: error.message || '网络错误',
      reason: '请求失败，请检查网络连接'
    });
  }
);

// API方法
export default {
  // 游客登录
  visitorLogin() {
    return api.get('/visitor');
  },
  
  // 用户注册
  register(username, password) {
    return api.get(`/register/${username}/${password}`);
  },
  
  // 用户登录
  login(username, password) {
    return api.get(`/login/${username}/${password}`);
  },
  
  // 创建新对话
  newConversation(username) {
    return api.get(`/new/${username}`);
  },
  
  // 获取历史记录数
  getHistoryCount(username) {
    return api.get(`/historycount/${username}`);
  },
  
  // 获取历史记录
  getHistory(sessionId) {
    return api.get(`/history/${sessionId}`);
  },
  
  // 关键词查询
  searchKeywords(sessionId, question) {
    return api.get(`/keywords/${sessionId}/${encodeURIComponent(question)}`);
  }
}