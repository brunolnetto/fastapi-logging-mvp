// src/store/taskStore.js
import { defineStore } from 'pinia';

import axios from 'axios';

const api = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL,
});

export const useTaskStore = defineStore('task', {
  state: () => ({
    tasks: [],
    selectedTask: null,
    taskLogs: [],
    taskCount: 0,
    logCount: 0,
  }),
  actions: {
    async fetchTasks() {
      try {
        const { data } = await api.get('/api/tasks');
        console.log(data);
        this.tasks = data;
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    },
    async fetchTaskDetails(taskId) {
      try {
        console.log('API Base URL:', process.env.VUE_APP_API_BASE_URL);
        const { data } = await api.get(`/api/tasks/${taskId}`);
        this.selectedTask = data.task;
        this.taskLogs = data.logs;
      } catch (error) {
        console.error('Error fetching task details:', error);
      }
    },
    async createTask(taskData) {
      try {
        console.log('API Base URL:', process.env.VUE_APP_API_BASE_URL);
        await api.post('/api/tasks', taskData);
        this.fetchTasks();
      } catch (error) {
        console.error('Error creating task:', error);
      }
    }
  },
});