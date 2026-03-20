import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Task } from '@/types';
import { taskApi } from '@/api/tasks';

export const useTaskStore = defineStore('task', () => {
  const tasks = ref<Task[]>([]);
  const currentTask = ref<Task | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const activeTasks = computed(() =>
    tasks.value.filter(t => ['analyzing', 'team_building', 'executing'].includes(t.status))
  );

  async function createTask(input: string) {
    loading.value = true;
    error.value = null;
    try {
      const response = await taskApi.create({ user_input: input });
      const task: Task = {
        id: response.data.id,
        user_input: input,
        status: response.data.status,
        progress: response.data.progress,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        cost: 0
      };
      tasks.value.unshift(task);
      return task;
    } catch (e: any) {
      error.value = e.message;
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTasks() {
    loading.value = true;
    try {
      const response = await taskApi.list();
      tasks.value = response.data.map((t: any) => ({
        id: t.id,
        status: t.status,
        progress: t.progress,
        user_input: '',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        cost: 0
      }));
    } finally {
      loading.value = false;
    }
  }

  async function startTask(taskId: string) {
    await taskApi.start(taskId);
    const task = tasks.value.find(t => t.id === taskId);
    if (task) {
      task.status = 'executing';
    }
  }

  return {
    tasks,
    currentTask,
    loading,
    error,
    activeTasks,
    createTask,
    fetchTasks,
    startTask
  };
});