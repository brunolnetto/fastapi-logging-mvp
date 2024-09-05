<template>
    <div>
      <h2>{{ task.task_name }} Details</h2>
      <p>Task Type: {{ task.task_type }}</p>
      <p>Status: {{ task.task_status }}</p>
      <h3>Logs</h3>
      <ul>
        <li v-for="log in logs" :key="log.talo_id">{{ log.talo_status }} - {{ log.talo_details }}</li>
      </ul>
    </div>
  </template>
  
  <script>
  import { useTaskStore } from '@/store/taskStore';
  import { onMounted } from 'vue';
  
  export default {
    setup(props) {
      const taskStore = useTaskStore();
      const task = taskStore.selectedTask;
      const logs = taskStore.taskLogs;
  
      onMounted(() => {
        taskStore.fetchTaskDetails(props.taskId);
      });
  
      return { task, logs };
    },
  };
  </script>
  