import { createWebHistory, createRouter } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import HelpView from '@/views/HelpView.vue'
import ChatView from '@/views/ChatView.vue'
import ShoppingView from '@/views/ShoppingView.vue'
import Settings from '../views/Settings.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'
import Testview from '../views/testview.vue'

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
    },
    {
        path: '/shopping',
        name: 'shopping',
        component: ShoppingView,
    },
    {
        path: '/settings',
        name: 'settings',
        component: Settings,
    },
    {
        path: '/login',
        name: 'login',
        component: LoginView,
    },
    {
        path: '/register',
        name: 'register',
        component: RegisterView
    },
    {
        path: '/test',
        name: 'test',
        component: Testview,
    },
    {
        path: '/chat',
        name: 'chat',
        component: () => import('@/views/ChatView.vue'),
        meta: { showChat: true }
    },

]

// 创建"路由器"
const router = createRouter({
    history: createWebHistory(),
    routes,
})

// 导出"路由器" (此处使用ES6默认导出)
export default router