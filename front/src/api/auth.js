// auth.js
import { ref } from 'vue';
import api from './api';

const user = ref(null);
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

    // 处理API响应错误
    const handleApiError = (err) => {
        // 现在err已经是后端返回的完整响应数据
        const errorMessage = err.reason || err.message || '操作失败';
        error.value = errorMessage;
        throw err; // 抛出完整错误对象，以便调用处可以访问所有字段
    };

    const register = async (username, password) => {
        loading.value = true;
        error.value = null;
        try {
            validateCredentials(username, password);

            const response = await api.register(username, password);
            if (response.code === 200) {
                user.value = { username };
                return response;
            } else {
                handleApiError(response);
            }
        } catch (err) {
            handleApiError(err);
        } finally {
            loading.value = false;
        }
    };

    const login = async (username, password) => {
        loading.value = true;
        error.value = null;
        try {
            validateCredentials(username, password);

            const response = await api.login(username, password);
            // 现在response已经是后端返回的数据对象
            if (response.code === 200) {
                user.value = { username };
                return response;
            } else {
                // 登录失败，抛出错误信息
                throw {
                    message: response.message,
                    reason: response.reason
                };
            }
        } catch (err) {
            handleApiError(err);
        } finally {
            loading.value = false;
        }
    };

    const visitorLogin = async () => {
        loading.value = true;
        error.value = null;
        try {
            const response = await api.visitorLogin();
            if (response.code === 200) {
                user.value = { username: `visitor${response.result}` };
                return response;
            } else {
                handleApiError(response);
            }
        } catch (err) {
            handleApiError(err);
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
        register
    };
};