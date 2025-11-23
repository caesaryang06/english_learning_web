import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'
import LoginView from '@/components/LoginView.vue'
import HomeView from '@/components/HomeView.vue'
import LearnView from '@/components/LearnView.vue'
import TestView from '@/components/TestView.vue'

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: LoginView,
        meta: { requiresAuth: false }
    },
    {
        path: '/',
        name: 'Home',
        component: HomeView,
        meta: { requiresAuth: true }
    },
    {
        path: '/learn',
        name: 'Learn',
        component: LearnView,
        meta: { requiresAuth: true }
    },
    {
        path: '/test',
        name: 'Test',
        component: TestView,
        meta: { requiresAuth: true }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore()

    // 检查是否需要登录
    if (to.meta.requiresAuth) {
        if (!userStore.isLoggedIn) {
            // 尝试从后端验证登录状态
            const isLoggedIn = await userStore.checkLogin()
            if (!isLoggedIn) {
                next('/login')
                return
            }
        }
    }

    // 如果已登录，访问登录页则跳转到首页
    if (to.path === '/login' && userStore.isLoggedIn) {
        next('/')
        return
    }

    next()
})

export default router