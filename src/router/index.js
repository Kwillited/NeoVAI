import { createRouter, createWebHistory } from 'vue-router';
import LoginRegister from '../components/LoginRegister.vue'; // 对应你的组件路径
import App from '../App.vue'; // 你的主应用组件

const routes = [
  {
    path: '/',
    name: 'Home',
    component: App,
    meta: { requiresAuth: true } // 需要登录才能访问
  },
  {
    path: '/auth',
    name: 'Auth',
    component: LoginRegister,
    meta: { requiresAuth: false } // 不需要登录
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

// 路由守卫：未登录时重定向到登录页
router.beforeEach((to, from, next) => {
  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    // 检查是否有token（实际项目根据存储方式调整）
    const hasToken = localStorage.getItem('userToken') || sessionStorage.getItem('userToken');
    if (hasToken) {
      next();
    } else {
      next('/auth'); // 未登录则跳转到登录页
    }
  } else {
    next();
  }
});

export default router;