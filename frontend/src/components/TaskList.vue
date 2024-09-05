<template>
    <div>
        <h2>Tasks</h2>
        <button @click="fetchTasks">Refresh</button>
        <ul>
        <li v-for="task in tasks" :key="task.task_id">
            <router-link :to="`/tasks/${task.task_id}`">{{ task.task_name }}</router-link>
            - <span>{{ task.task_status }}</span>
        </li>
        </ul>
    </div>
</template>
    
<script>
    import { useTaskStore } from '@/store/taskStore';
    
    export default {
        setup() {
            const taskStore = useTaskStore();
            const tasks = taskStore.tasks;
            const fetchTasks = taskStore.fetchTasks;
            
            return {
            tasks,
            fetchTasks
            };
        },
    };
</script>
