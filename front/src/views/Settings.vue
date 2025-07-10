<template>
  <div class="settings-page">
    <h1 class="page-title">个人设置</h1>
    
    <div class="settings-container">
      <!-- 侧边栏导航 -->
      <div class="settings-sidebar">
        <h3 class="sidebar-title">设置选项</h3>
        <div class="tab-menu">
          <div 
            v-for="tab in tabs" 
            :key="tab.id"
            class="tab-item"
            :class="{ 'active-tab': activeTab === tab.id }"
            @click="setActiveTab(tab.id)"
          >
            {{ tab.label }}
          </div>
        </div>
      </div>
      
      <!-- 主内容区 -->
      <div class="settings-content">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-overlay">
          <div class="loader"></div>
        </div>
        
        <!-- 个人信息表单 -->
        <div v-show="activeTab === 'profile'" class="tab-panel">
          <h2 class="panel-title">个人信息</h2>
          <div class="form-container">
            <div class="form-group">
              <label>用户名</label>
              <input 
                type="text" 
                v-model="localUserInfo.username" 
                maxlength="20"
                class="form-input"
                placeholder="请输入用户名">
            </div>
            
            <div class="form-group">
              <label>头像</label>
              <div class="avatar-upload">
                <img :src="localUserInfo.avatarUrl" alt="用户头像" class="user-avatar" />
                <div class="upload-controls">
                  <button class="btn btn-primary" @click="triggerAvatarUpload">
                    更换头像
                  </button>
                  <input 
                    type="file" 
                    ref="avatarInput"
                    accept="image/*" 
                    class="file-input"
                    @change="handleAvatarUpload">
                  <p class="upload-hint">支持 JPG、PNG 格式，大小不超过 2MB</p>
                </div>
              </div>
            </div>
            
            <div class="form-group">
              <label>手机号</label>
              <input 
                type="tel" 
                v-model="localUserInfo.phone" 
                class="form-input"
                placeholder="请输入手机号">
            </div>
            
            <div class="form-group">
              <label>邮箱</label>
              <input 
                type="email" 
                v-model="localUserInfo.email" 
                class="form-input"
                placeholder="请输入邮箱">
            </div>
            
            <div class="form-actions">
              <button class="btn btn-primary" @click="saveProfile">
                保存修改
              </button>
            </div>
          </div>
        </div>
        
        <!-- 账号安全表单 -->
        <div v-show="activeTab === 'security'" class="tab-panel">
          <h2 class="panel-title">账号安全</h2>
          <div class="form-container">
            <div class="form-group">
              <label>当前密码</label>
              <input 
                type="password" 
                v-model="securityInfo.oldPassword" 
                class="form-input"
                placeholder="请输入当前密码">
            </div>
            
            <div class="form-group">
              <label>新密码</label>
              <input 
                type="password" 
                v-model="securityInfo.newPassword" 
                class="form-input"
                placeholder="请输入新密码">
            </div>
            
            <div class="form-group">
              <label>确认新密码</label>
              <input 
                type="password" 
                v-model="securityInfo.confirmPassword" 
                class="form-input"
                placeholder="请再次输入新密码">
            </div>
            
            <div class="password-strength">
              <div class="strength-bar" :class="passwordStrengthClass"></div>
              <div class="strength-text">{{ passwordStrengthText }}</div>
            </div>
            
            <div class="form-actions">
              <button class="btn btn-primary" @click="changePassword">
                修改密码
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus';

export default {
  name: 'SettingsView',
  data() {
    return {
      activeTab: 'profile',
      tabs: [
        { id: 'profile', label: '个人信息' },
        { id: 'security', label: '账号安全' }
      ],
      isLoading: false,
      localUserInfo: {
        username: 'User123',
        avatarUrl: 'https://via.placeholder.com/80',
        phone: '13800000000',
        email: 'user@example.com'
      },
      securityInfo: {
        oldPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    };
  },
  computed: {
    passwordStrength() {
      const pwd = this.securityInfo.newPassword || '';
      let score = 0;
      if (pwd.length >= 8) score += 1;
      if (pwd.length >= 12) score += 1;
      if (/[A-Z]/.test(pwd)) score += 2;
      if (/[a-z]/.test(pwd)) score += 1;
      if (/\d/.test(pwd)) score += 2;
      if (/[^A-Za-z0-9]/.test(pwd)) score += 2;
      return score;
    },
    passwordStrengthText() {
      const s = this.passwordStrength;
      if (!this.securityInfo.newPassword) return '';
      return s <= 3 ? '弱' : s <= 5 ? '中' : '强';
    },
    passwordStrengthClass() {
      const s = this.passwordStrength;
      return s <= 3 ? 'strength-weak' : s <= 5 ? 'strength-medium' : 'strength-strong';
    }
  },
  methods: {
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    triggerAvatarUpload() {
      this.$refs.avatarInput.click();
    },
    handleAvatarUpload(e) {
      const file = e.target.files[0];
      if (!file || !file.type.match('image.*')) {
        ElMessage.error('请选择图片文件');
        return;
      }
      if (file.size > 2 * 1024 * 1024) {
        ElMessage.error('图片大小不能超过2MB');
        return;
      }
      const reader = new FileReader();
      reader.onload = evt => {
        this.localUserInfo.avatarUrl = evt.target.result;
      };
      reader.readAsDataURL(file);
      e.target.value = '';
    },
    saveProfile() {
      if (!this.localUserInfo.username) {
        ElMessage.error('用户名不能为空');
        return;
      }
      ElMessage.success('个人信息修改成功');
    },
    changePassword() {
      if (this.securityInfo.newPassword !== this.securityInfo.confirmPassword) {
        ElMessage.error('两次输入的密码不一致');
        return;
      }
      if (this.securityInfo.newPassword.length < 6) {
        ElMessage.error('密码长度不能少于6位');
        return;
      }
      this.isLoading = true;
      setTimeout(() => {
        this.isLoading = false;
        ElMessage.success('密码修改成功');
        this.securityInfo.oldPassword = '';
        this.securityInfo.newPassword = '';
        this.securityInfo.confirmPassword = '';
      }, 1000);
    }
  }
};
</script>

<style scoped>
/* 页面整体样式 */
.settings-page {
  max-width: 1200px;
  margin: 10px auto;
  padding: 10px 16px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px solid #eee;
}

.settings-container {
  display: flex;
  gap: 16px;
  justify-content: flex-start;
}

@media (max-width: 767px) {
  .settings-container {
    flex-direction: column;
  }
}

/* 侧边栏 */
.settings-sidebar {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 12px;
  width: 220px;
  flex-shrink: 0;
}


.sidebar-title {
  font-size: 20px;
  font-weight: 600;
  color: #666;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f0f0f0;
}

.tab-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tab-item {
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  color: #555;
}

.tab-item.active-tab,
.tab-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 主内容区 */
.settings-content {
  flex: none;
  width: 580px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  padding: 20px;
  position: relative;
}

.tab-panel {
  margin-top: 0;
}

/* 表单容器 */
.form-container {
  width: 100%;
  box-sizing: border-box;
}

.form-group {
  margin-bottom: 10px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #555;
  font-size: 13px;
}

.form-input {
  width: 100%;
  max-width: 440px;
  height: 32px;
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #409eff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 强度条 & 按钮 */
.password-strength {
  margin-top: 10px;
}

.strength-bar {
  height: 6px;
  border-radius: 3px;
  margin-bottom: 6px;
}

.strength-weak { width: 30%; background-color: #f56c6c; }
.strength-medium { width: 60%; background-color: #e6a23c; }
.strength-strong { width: 100%; background-color: #67c23a; }

.strength-text {
  font-size: 12px;
  color: #666;
}

.form-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.btn {
  display: inline-block;
  padding: 6px 12px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
  transition: background-color .2s, border-color .2s;
  appearance: none;
  border: 1px solid transparent;
  background: transparent;
  color: #409eff;
}
.btn-primary {
  background-color: #409eff;
  border-color: #409eff;
  color: #fff;
}
.btn-primary:hover {
  background-color: #66b1ff;
  border-color: #66b1ff;
}
.btn:focus { outline: none; }


/* 头像上传 */
.avatar-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #f0f0f0;
}

.upload-controls {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-input { display: none; }
.upload-hint {
  font-size: 11px;
  color: #999;
}

/* 加载状态 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  z-index: 10;
}

.loader {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409eff;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
