import { ref } from 'vue';
import api from './api';
const user = ref(null);  // 这行是修复关键

const error = ref(null);
const loading = ref(false);
export const useAuth = () => {
 
    // 验证用户名和密码不能是纯数字
    const validateCredentials = (username, password) => {
        const isAllNumbers = (str) => /^\d+$/.test(str);

        if (isAllNumbers(username)) {
            throw new Error('用户名不能是纯数字');
        }

        if (isAllNumbers(password)) {
            throw new Error('密码不能是纯数字');
        }

        // 可以添加更多验证规则
        if (username.length < 3) {
            throw new Error('用户名至少需要3个字符');
        }

        if (password.length < 6) {
            throw new Error('密码至少需要6个字符');
        }
    };

    const logout = () => {
        user.value = null;
    };

    const register = async (username, password) => {
        loading.value = true;
        error.value = null;
        try {
            // 先验证输入
            validateCredentials(username, password);

            const response = await api.register(username, password);
            user.value = { username };
            return response;
        } catch (err) {
            error.value = err.message || err.reason || '注册失败';
            throw err;
        } finally {
            loading.value = false;
        }
    };

    const login = async (username, password) => {
        loading.value = true;
        error.value = null;
        try {
            // 登录时也验证输入
            validateCredentials(username, password);

            const response = await api.login(username, password);
            user.value = { username };
            return response;
        } catch (err) {
            error.value = err.message || err.reason || '登录失败';
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
        visitorLogin,
        logout,
    };
};