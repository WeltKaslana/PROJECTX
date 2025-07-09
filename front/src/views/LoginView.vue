<template>
  <!-- 模板部分保持不变 -->
  <div class="login-page">
    <el-card class="login-card">
      <h2 class="login-title">用户登录</h2>
      <el-form ref="loginFormRef" :model="form" :rules="rules" label-width="100px" label-position="top"
        @submit.prevent="handleSubmit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" placeholder="请输入密码" type="password" show-password clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="login-button">
            登录
          </el-button>
          <el-button @click="navigateToRegister" class="register-link-button">
            没有账号？立即注册
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { useAuth } from '@/api/auth';

const router = useRouter();
const { login, loading, error } = useAuth();
const loginFormRef = ref(null);

const form = ref({
  username: '',
  password: ''
});

// 验证规则保持不变
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (/^\d+$/.test(value)) {
          callback(new Error('用户名不能是纯数字'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '至少6个字符', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (/^\d+$/.test(value)) {
          callback(new Error('密码不能是纯数字'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ]
};

const handleSubmit = async () => {
  try {
    await loginFormRef.value.validate();
    loading.value = true;

    const result = await login(form.value.username, form.value.password);

    // 登录成功处理
    if (result.code === 200) {
      ElMessage.success(result.message || '登录成功');
      router.push('/');
    }
  } catch (err) {
    // 错误处理
    const errorMsg = err.reason || err.message || '登录失败';
    ElMessage.error(errorMsg);
    console.error('登录错误详情:', {
      message: err.message,
      reason: err.reason,
      fullError: err
    });
  } finally {
    loading.value = false;
  }
};
const navigateToRegister = () => {
  router.push('/register');
};
</script>

<style scoped>
/* 样式部分保持不变 */
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.login-card {
  width: 100%;
  max-width: 500px;
  padding: 24px;
}

.login-title {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.login-button {
  width: 100%;
  margin-bottom: 12px;
}

.register-link-button {
  width: 100%;
}
</style>