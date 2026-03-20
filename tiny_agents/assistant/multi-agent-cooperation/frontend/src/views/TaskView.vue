<template>
  <div class="task-view">
    <div class="container">
      <el-page-header @back="goHome" title="返回首页">
        <template #content>
          <span class="task-title">任务详情</span>
        </template>
      </el-page-header>

      <el-card class="task-card">
        <template #header>
          <div class="card-header">
            <span>任务进度</span>
            <el-tag :type="statusType">{{ task?.status || 'pending' }}</el-tag>
          </div>
        </template>

        <el-progress
          :percentage="task?.progress || 0"
          :status="progressStatus"
          :stroke-width="20"
        />

        <div class="task-info">
          <div class="info-item">
            <span class="label">任务描述：</span>
            <span>{{ task?.user_input }}</span>
          </div>
          <div class="info-item">
            <span class="label">创建时间：</span>
            <span>{{ formatTime(task?.created_at) }}</span>
          </div>
        </div>

        <div class="actions">
          <el-button
            v-if="task?.status === 'pending' || task?.status === 'paused'"
            type="primary"
            @click="handleStart"
          >
            开始执行
          </el-button>
          <el-button
            v-if="task?.status === 'executing'"
            @click="handlePause"
          >
            暂停
          </el-button>
          <el-button
            v-if="task?.status !== 'completed' && task?.status !== 'failed'"
            type="danger"
            @click="handleCancel"
          >
            取消
          </el-button>
        </div>
      </el-card>

      <!-- Agent状态 -->
      <el-card class="agents-card">
        <template #header>
          <span>Agent状态</span>
        </template>

        <div class="agents-grid">
          <div v-for="role in roles" :key="role.name" class="agent-item">
            <el-tag :type="getRoleStatusType(role.status)">
              {{ role.status }}
            </el-tag>
            <span class="role-name">{{ role.name }}</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { taskApi } from '@/api/tasks';
import type { Task, Role } from '@/types';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();

const taskId = computed(() => route.params.id as string);
const task = ref<Task | null>(null);
const roles = ref<Role[]>([
  { name: 'ProductManager', status: 'idle' },
  { name: 'Architect', status: 'idle' },
  { name: 'FrontendDev', status: 'idle' },
  { name: 'BackendDev', status: 'idle' },
  { name: 'QAEngineer', status: 'idle' }
]);

const statusType = computed(() => {
  const map: Record<string, string> = {
    pending: 'info',
    analyzing: 'warning',
    team_building: 'warning',
    executing: 'primary',
    completed: 'success',
    failed: 'danger',
    paused: 'warning'
  };
  return map[task.value?.status || 'pending'] || 'info';
});

const progressStatus = computed(() => {
  if (task.value?.status === 'completed') return 'success';
  if (task.value?.status === 'failed') return 'exception';
  return undefined;
});

function formatTime(time?: string) {
  if (!time) return '-';
  return new Date(time).toLocaleString();
}

function getRoleStatusType(status: string) {
  const map: Record<string, string> = {
    idle: 'info',
    waiting: 'warning',
    working: 'primary',
    completed: 'success',
    failed: 'danger'
  };
  return map[status] || 'info';
}

function goHome() {
  router.push('/');
}

async function handleStart() {
  await taskApi.start(taskId.value);
  ElMessage.success('任务已开始');
}

async function handlePause() {
  await taskApi.pause(taskId.value);
  ElMessage.info('任务已暂停');
}

async function handleCancel() {
  await taskApi.cancel(taskId.value);
  ElMessage.warning('任务已取消');
}

onMounted(async () => {
  try {
    const response = await taskApi.get(taskId.value);
    task.value = {
      id: response.data.id,
      status: response.data.status,
      progress: response.data.progress,
      user_input: '',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      cost: 0
    };
  } catch (e) {
    ElMessage.error('获取任务失败');
  }
});
</script>

<style scoped>
.task-view {
  min-height: 100vh;
  padding: 24px;
}

.container {
  max-width: 900px;
  margin: 0 auto;
}

.task-title {
  font-size: 18px;
  font-weight: bold;
}

.task-card,
.agents-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-info {
  margin-top: 20px;
}

.info-item {
  margin-bottom: 12px;
  display: flex;
  gap: 8px;
}

.label {
  color: #909399;
  flex-shrink: 0;
}

.actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.role-name {
  font-weight: 500;
}
</style>