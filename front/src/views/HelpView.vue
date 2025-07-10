<template>
    <div class="help-page">
        <!-- 帮助中心头部 -->
        <div class="header-section">
            <h1 class="help-title">帮助中心</h1>
            <p class="welcome-text">欢迎使用智购助手帮助中心，这里为您提供关于系统功能和使用方法的详细说明。</p>
        </div>

        <!-- 关于智购助手 -->
        <section class="info-section">
            <h2 class="section-title">关于智购助手</h2>
            <p class="section-content">
                智购助手是由西安交通大学的九位开发者研发的一款AI助手，旨在为用户提供智能购物服务。我们致力于通过先进的人工智能技术，为用户提供个性化的推荐和高效的服务体验。
            </p>
        </section>

        <!-- 常见问题 -->
        <section class="faq-section">
            <h2 class="section-title">常见问题</h2>
            
            <div class="faq-container">
                <div 
                    v-for="(faq, index) in faqList" 
                    :key="index"
                    class="faq-item"
                    :class="{ 'is-active': activeIndexes.includes(index) }"
                    @click="toggleFaq(index)"
                >
                    <div class="faq-question">
                        <span>{{ faq.title }}</span>
                        <span class="toggle-icon">{{ activeIndexes.includes(index) ? '−' : '+' }}</span>
                    </div>
                    
                    <div v-show="activeIndexes.includes(index)" class="faq-answer">
                        <div v-for="(item, itemIndex) in faq.content" :key="itemIndex">
                            <p v-if="item.type === 'paragraph'">{{ item.text }}</p>
                            <ul v-if="item.type === 'list'" class="faq-list">
                                <li v-for="(listItem, listIndex) in item.items" :key="listIndex">{{ listItem }}</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref } from 'vue';

// 管理展开的面板
const activeIndexes = ref([]);

// 所有FAQ数据集中管理
const faqList = ref([
    {
        title: "如何注册账号？",
        content: [
            { type: "paragraph", text: "在首页点击'注册'按钮，进入注册页面。" },
            { type: "paragraph", text: "注册要求：" },
            { 
                type: "list", 
                items: [
                    "用户名：3-20位字符，不能是纯数字",
                    "密码：至少6位字符，不能是纯数字"
                ]
            },
            { type: "paragraph", text: "填写完成后点击'注册'按钮即可完成注册。" }
        ]
    },
    {
        title: "如何进行商品搜索？",
        content: [
            { type: "paragraph", text: "登录账号后，进入购物页面。" },
            { type: "paragraph", text: "在搜索框中输入您想要搜索的商品关键词，点击搜索按钮，系统会为您展示相关的商品信息。" },
            { type: "paragraph", text: "您还可以使用筛选功能，进一步缩小搜索范围。" }
        ]
    },
    {
        title: "忘记密码怎么办？",
        content: [
            { type: "paragraph", text: "目前暂不支持找回密码功能，请联系管理员进行处理。" },
            { type: "paragraph", text: "管理员邮箱：admin@qq.com" }
        ]
    }
]);

// 切换FAQ的展开状态
const toggleFaq = (index) => {
    const currentIndex = activeIndexes.value.indexOf(index);
    
    if (currentIndex > -1) {
        activeIndexes.value.splice(currentIndex, 1);
    } else {
        activeIndexes.value.push(index);
    }
};
</script>

<style scoped>
/* 基础样式 */
.help-page {
    max-width: 1200px;
    margin: 0 auto; 
    padding: 30px; 
    box-sizing: border-box; 
    animation: fadeIn 0.5s ease-in-out;
}

/* 头部区域 */
.header-section {
    margin-bottom: 30px;
}

.help-title {
    font-size: 24px;
    font-weight: 700;
    color: #333;
    margin-bottom: 15px;
}

.welcome-text {
    font-size: 16px;
    color: #666;
    max-width: 800px;
    line-height: 1.6;
}

/* 通用部分样式 */
.section-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    margin-bottom: 15px;
}

.section-content {
    font-size: 16px;
    color: #666;
    line-height: 1.6;
}

/* 信息板块 */
.info-section,
.faq-section {
    background-color: #fff;
    border-radius: 12px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    padding: 25px;
    margin-bottom: 30px;
}

/* FAQ区域 */
.faq-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.faq-item {
    border: 1px solid #eaeaea;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.faq-item.is-active {
    border-color: #409eff;
    box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.faq-question {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px;
    background-color: #f9f9f9;
    cursor: pointer;
    font-size: 16px;
    font-weight: 500;
    color: #333;
    transition: background-color 0.2s;
}

.faq-question:hover {
    background-color: #f1f1f1;
}

.toggle-icon {
    font-size: 20px;
    font-weight: bold;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.faq-answer {
    padding: 20px;
    background-color: #fff;
    border-top: 1px solid #f0f0f0;
    font-size: 15px;
    color: #555;
    line-height: 1.7;
}

.faq-list {
    padding-left: 20px;
    margin: 10px 0;
}

.faq-list li {
    margin-bottom: 8px;
    line-height: 1.5;
}

/* 动画效果 */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
    .help-page {
        padding: 20px 15px;
    }
    
    .info-section,
    .faq-section {
        padding: 20px;
    }
}
</style>