// src/api/agent.js
import { ref } from 'vue'
import axios from 'axios'

export function useAgent() {
  const loading = ref(false)
  const error = ref(null)
  
  const sendMessageToAgent = async (data) => {
    try {
      loading.value = true
      error.value = null
      
      // 模拟实际API调用，实际项目中替换为真实API地址
      // const response = await axios.post('/api/agent/chat', data)
      
      // 模拟响应 - 实际开发中删除此部分
      await new Promise(resolve => setTimeout(resolve, 1000));
      const mockResponse = {
        data: {
          text: `这是关于"${data.message}"的搜索结果：`,
          // 实际API应返回结构化数据
        }
      };
      
      return mockResponse.data;
    } catch (err) {
      error.value = err.response?.data?.message || 
                   err.message || 
                   '助手服务请求失败'
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    loading,
    error,
    sendMessageToAgent
  }
}