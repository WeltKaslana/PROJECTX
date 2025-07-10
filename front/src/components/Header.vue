<template>
  <el-header class="header">
    <el-menu mode="horizontal" :ellipsis="false" :router="true" class="nav-menu">
      <!-- 应用logo -->
      <el-menu-item index="0" class="logo-item">
        <img style="width: 100px" :src="Zhigou_Logo" alt="应用Logo" />
      </el-menu-item>

      <!-- 用户状态区域 -->
      <div class="user-state">
        <!-- 未登录状态 -->
        <div v-if="!user" class="auth-buttons">
          <el-button @click="navigateTo.register" class="auth-button register" :loading="authLoading">
            注册
          </el-button>
          <el-button @click="navigateTo.login" class="auth-button login" :loading="authLoading">
            登录
          </el-button>
        </div>

        <!-- 已登录状态 -->
        <div v-else class="user-profile">
          <el-dropdown>
            <el-button class="profile-button">
              {{ user.username }}
              <i class="el-icon-arrow-down el-icon--right"></i>
            </el-button>
            <template #dropdown>
              <el-menu>
                <el-menu-item @click="navigateTo.info">
                  用户信息
                </el-menu-item>
                <el-menu-item @click="navigateTo.settings">
                  设置
                </el-menu-item>
                <el-menu-item @click="navigateTo.test">
                  开发者功能
                </el-menu-item>
                <el-menu-item @click="logout">
                  退出
                </el-menu-item>
              </el-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
    </el-menu>
  </el-header>
</template>

<script setup>
import { useAuth } from '@/api/auth'
import Zhigou_Logo from '@/assets/logo.png'
import { useRouter } from 'vue-router'

// 路由相关
const router = useRouter()

// 认证模块
const {
  user,
  authLoading,
  logout
} = useAuth()

// 导航方法
const navigateTo = {
  login: () => router.push('/login'),
  register: () => router.push('/register'),
  info: () => router.push('/info'),
  settings: () => router.push('/settings'),
  test: () => router.push('/test')
}
</script>

<style scoped>
.header {
  padding: 0;
  height: 65px;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
}

.nav-menu {
  display: flex;
  align-items: center;
  height: 100%;
  border-bottom: none;
  justify-content: space-between !important;
}

.logo-item {
  display: flex;
  align-items: center;
  padding: 0 20px !important;
}

.user-state {
  padding-right: 20px;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

.auth-button {
  &.login {
    background-color: black;
    color: white;
    border-color: black;

    &:hover {
      background-color: #666;
      border-color: #666;
    }
  }

  &.register {
    background-color: white;
    color: black;
    border-color: #dcdfe6;

    &:hover {
      background-color: #f5f7fa;
    }
  }
}

.profile-button {
  padding: 8px 15px;
}

@media (max-width: 480px) {
  .header {
    height: 60px;
  }
  
  .auth-buttons {
    gap: 5px;
  }

  .auth-button {
    padding: 8px 12px;
    font-size: 12px;
  }
}
</style>