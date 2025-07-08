import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080', // 后端API地址
  timeout: 5000
});

// 统一处理响应
api.interceptors.response.use(
  response => {
    if (response.data && response.data.code === 200) {
      return response.data;
    }
    return Promise.reject(response.data);
  },
  error => {
    return Promise.reject(error);
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