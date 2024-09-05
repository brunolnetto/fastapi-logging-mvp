<template>
    <div>
      <h2>Create a Task</h2>
      <form @submit.prevent="submitTask">
        <input v-model="taskName" placeholder="Task Name" required />
        <input v-model="taskType" placeholder="Task Type" required />
        <textarea v-model="taskDetails" placeholder="Task Details" />
        <button type="submit">Create Task</button>
      </form>
    </div>
  </template>
  
  <script>
  import { useTaskStore } from '@/store/taskStore';
  
  export default {
    setup() {
      const taskStore = useTaskStore();
      const taskName = ref('');
      const taskType = ref('');
      const taskDetails = ref('');
  
      const submitTask = async () => {
        await taskStore.createTask({
          task_name: taskName.value,
          task_type: taskType.value,
          task_details: taskDetails.value,
        });
      };
  
      return {
        taskName,
        taskType,
        taskDetails,
        submitTask,
      };
    },
  };
  </script>
  