// auth.js
import { ref } from 'vue';
import api from './api';

export const useAuth = () => {
  // 修改为默认已登录状态
  //测试状态 未启用后端
  const user = ref({
    username: '测试用户',
    isAdmin: false
  })
  
  const error = ref(null)
  const loading = ref(false)

  // 保持其他方法不变

  const logout = () => {
    user.value = null
  }

  const register = async (username, password) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.register(username, password);
      user.value = { username };
      return response;
    } catch (err) {
      error.value = err.reason || '注册失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const login = async (username, password) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await api.login(username, password);
      user.value = { username };
      return response;
    } catch (err) {
      error.value = err.reason || '登录失败';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const visitorLogin = async () => {
    loading.value = true;
    try {
      const response = await api.visitorLogin();
      user.value = { username: `visitor${response.result[0]}` };
      return response;
    } finally {
      loading.value = false;
    }
  };

  return {
    user,
    error,
    loading,
    register,
    login,
    visitorLogin
  };
};