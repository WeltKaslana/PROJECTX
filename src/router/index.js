import { createWebHistory, createRouter } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import HelpView from '@/views/HelpView.vue'
import ChatView from '@/views/ChatView.vue'

// 定义"路由"数组 (即路由记录数组)
const routes = [
    {
        path: '/',
        name: 'home',
        component: HomeView,
    },
    {
        path: '/help',
        name: 'help',
        component: HelpView,
    },
    {
        path: '/chat',
        name: 'chat',
        component: ChatView,
    }
]

// 创建"路由器"
const router = createRouter({
    history: createWebHistory(),
    routes,
})

// 导出"路由器" (此处使用ES6默认导出)
export default router