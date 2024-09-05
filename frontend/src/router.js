// src/router.js
import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from './views/AppDashboard.vue';
import TaskDetail from './views/TaskDetail.vue';

import TaskList from './components/TaskList.vue';

const routes = [
    { path: '/', component: Dashboard },
    { path: '/tasks', component: TaskList },
    { path: '/tasks/:taskId', component: TaskDetail, props: true },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;