<template>
  <div class="register-page">
    <el-card class="register-card">
      <h2 class="register-title">用户注册</h2>
      <el-form ref="registerFormRef" :model="form" :rules="rules" label-width="100px" label-position="top"
        @submit.prevent="handleSubmit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="3-20位字符，不能是纯数字" clearable />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" placeholder="至少6位字符，不能是纯数字" type="password" show-password clearable />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" placeholder="请再次输入密码" type="password" show-password clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="register-button">
            注册
          </el-button>
          <el-button @click="navigateToLogin" class="login-link-button">
            已有账号？登录
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
const { register, loading } = useAuth();
const registerFormRef = ref(null);

const form = ref({
  username: '',
  password: '',
  confirmPassword: ''
});

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度在3到20个字符', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
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
      validator: (rule, value, callback) => {
        if (/^\d+$/.test(value)) {
          callback(new Error('密码不能是纯数字'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== form.value.password) {
          callback(new Error('两次输入的密码不一致'));
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
    // 验证表单
    await registerFormRef.value.validate();
    loading.value = true;

    // 调用注册接口
    const result = await register(form.value.username, form.value.password);

    // 注册成功处理
    if (result.code === 200) {
      ElMessage.success(result.message || '注册成功');
      router.push('/login'); // 注册成功后跳转到登录页
    }
  } catch (err) {
    // 错误处理 - 优先显示后端返回的reason或message
    const errorMsg = err.reason || err.message || '注册失败';
    ElMessage.error(errorMsg);
    console.error('注册错误详情:', {
      message: err.message,
      reason: err.reason,
      fullError: err
    });
  } finally {
    loading.value = false;
  }
};

const navigateToLogin = () => {
  router.push('/login');
};
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
}

.register-card {
  width: 100%;
  max-width: 500px;
  padding: 24px;
}

.register-title {
  text-align: center;
  margin-bottom: 24px;
  color: #333;
}

.register-button {
  width: 100%;
  margin-bottom: 12px;
}

.login-link-button {
  width: 100%;
}
</style>