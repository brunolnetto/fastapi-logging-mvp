<template>
    <div>
      <h1>Task Scheduler Dashboard</h1>
      <div>
        <p>Total Tasks: {{ taskCount }}</p>
        <p>Total Logs: {{ logCount }}</p>
      </div>
    </div>
  </template>
  
  <script>
  import { useTaskStore } from '@/store/taskStore';
  
  export default {
    setup() {
      const taskStore = useTaskStore();
      return {
        taskCount: taskStore.taskCount,
        logCount: taskStore.logCount
      };
    },
  };
  </script>
  