<script setup>
import { ref } from 'vue'
import { ElButton, ElDropdown, ElMenu, ElMenuItem } from 'element-plus'
import elementPlusLogo from '@/assets/logo.png'

import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'

const isLoggedIn = ref(false)
const username = ref('用户名')
const message = ref('')

// 模拟登录
const login = () => {
  isLoggedIn.value = true;
  username.value = '张三'; // 登录后显示用户名
}

// 模拟登出
const logout = () => {
  isLoggedIn.value = false;
  username.value = '';
}

// 方法：创建新聊天
const createNewChat = () => {
  console.log('创建新聊天')
  router.push('/new-chat');
}

// 方法：查看历史聊天
const viewHistory = () => {
  console.log('查看历史聊天')
  // 逻辑代码可以在这里添加
}

// 方法：筛选商品
const filterProducts = () => {
  console.log('筛选商品')
  // 逻辑代码可以在这里添加
}

// 方法：设置价格提醒
const setPriceAlert = () => {
  console.log('设置价格提醒')
  // 逻辑代码可以在这里添加
}

// 方法：打开用户设置
const openSettings = () => {
  console.log('打开设置')
  // 逻辑代码可以在这里添加
}

// 方法：打开帮助
const openHelp = () => {
  console.log('打开帮助')
  // 逻辑代码可以在这里添加
}

const submitMessage = () => {
  console.log('提交消息:', message.value);  // 这里可以替换为提交消息的实际逻辑
  message.value = '';  // 清空输入框
}
</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header class="header">
        <!-- 水平导航菜单， 当 router 取值为 true 时表示启用对 VueRouter 的导航支持 -->
        <el-menu mode="horizontal" :ellipsis="false" :router="true" class="nav-menu">
          <!-- 菜单项 -->
          <el-menu-item index="0">
            <img style="width: 100px" :src="elementPlusLogo" alt="Element logo" />
          </el-menu-item>
          <!-- 右上角的注册/登录按钮 -->
          <div v-if="!isLoggedIn" class="login-btn">
            <el-button @click="login" class="login-button">登录</el-button>
          </div>

          <!-- 如果已登录，则显示用户信息和设置 -->
          <div v-else class="user-dropdown">
            <el-dropdown>
              <el-button>
                {{ username }} <i class="el-icon-arrow-down el-icon--right"></i>
              </el-button>
              <template #dropdown>
                <el-menu>
                  <el-menu-item>用户信息</el-menu-item>
                  <el-menu-item>设置</el-menu-item>
                  <el-menu-item @click="logout">退出</el-menu-item>
                </el-menu>
              </template>
            </el-dropdown> 
          </div> 
        </el-menu>
      </el-header>
      
      <el-container>
        <el-aside width="230px" class="aside">
          <el-menu default-active="2" class="el-menu-vertical-demo">
            <!--创建新聊天-->
            <el-menu-item index="1" @click="createNewChat">
              <el-icon><icon-menu /></el-icon>
              <span>创建新聊天</span>
            </el-menu-item>

            <!--商品筛选-->
            <el-menu-item index="2" @click="filterProducts">
              <el-icon><icon-menu /></el-icon>
              <span>商品筛选</span>
            </el-menu-item>  

            <!-- 历史聊天 -->
            <el-menu-item index="3" @click="viewHistory">
              <el-icon><icon-menu /></el-icon>
              <span>历史聊天</span>
            </el-menu-item>

            <!-- 固定底部 -->
            <div class="bottom-buttons">
              <!-- 用户设置 -->
              <el-menu-item index="4" @click="openSettings">
                <el-icon><Setting /></el-icon>
                <span>用户设置</span>
              </el-menu-item>

              <!-- 帮助 -->
              <el-menu-item index="5" :to="{ path: '/help' }"> 
                <el-icon><Location /></el-icon>
                <span>帮助</span>
              </el-menu-item>
            </div>
          </el-menu>
          <div>
            <router-link to="/help">帮助</router-link>
          </div>
        </el-aside>
        <el-main class="main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

     <!-- 中间的输入框和提交按钮 -->
    <div class="chat-box">
      <div class="input-wrapper">
      <img style="width: 100px" src="@/assets/logo.png" alt="logo" class="chat-logo" />
      <div class="input-label">你好，我是智能购物机</div>
      <el-input v-model="message" placeholder="请输入消息..." class="message-input"></el-input>
      <el-button type="primary" class="submit-btn" @click="submitMessage">↑</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
:global(body) {
  margin: 0;
}

/* 右上角的登录按钮样式 */
.login-btn {
  float: right;
  display: flex;
  justify-content: center; /* 水平居中 */
  align-items: center;     /* 垂直居中 */
  margin-top: 5px; /* 调整按钮与顶部的距离 */
  margin-right: 5px; /* 确保按钮靠右 */
}

/* 修改登录按钮样式：黑色背景，白色字体 */
.login-button {
  background-color: black;
  color: white;
  border-color: black;
}

.login-button:hover {
  background-color: #666;
  color: white;
  border-color: #666;
}

.aside {
  height: 90vh;
  margin-top: 20px;
  display: flex;
  flex-direction: column;
}

.el-menu-vertical-demo {
  flex-grow: 1;
  overflow-y: auto;
}

.bottom-buttons {
  margin-top: 300px; /* 固定底部 */
  padding: 1px;
}

.el-menu-item {
  display: flex;
  align-items: center;
  padding-left: 20px;
  font-size: 16px;
  color: #333;
}

.el-menu-item:hover {
  background-color: #ddd;
}

.el-menu--horizontal {
  --el-menu-horizontal-height: 65px;
}

.el-menu--horizontal>.el-menu-item:nth-child(1) {
  margin-right: auto;
}

.input-label {
  font-size: 30px; 
  color: black;     
  margin-bottom: 30px; 
  text-align: center;
  font-weight: bold; 
}

.chat-box {
  position: absolute;
  top: 50%;  /* 垂直居中 */
  left: 50%; /* 水平居中 */
  transform: translate(-40%, -50%);
  width: 700px;
}

.input-wrapper {
  text-align:center;
}

.message-input {
  width: 100%;
  height: 200px;
  margin-bottom: 10px;
  font-size: 20px;
}

.submit-btn {
  width: 40px;
  height: 40px;
  border-radius: 100%; /* 使按钮变圆 */
  position: absolute;
  bottom: 20px; /* 按钮位置靠近文本框右下角 */
  right: 15px; /* 放置到右下角 */
  padding: 0;
  font-size: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: black; 
  color:white;
  border-color: black;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
}
</style>
