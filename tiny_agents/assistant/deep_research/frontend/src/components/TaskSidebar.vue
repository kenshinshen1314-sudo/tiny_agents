<template>
  <aside class="sidebar" role="complementary" aria-label="任务列表">
    <div class="sidebar__section">
      <h3 class="sidebar__title">研究任务</h3>
      <div class="task-list" v-if="todoTasks.length">
        <div
          v-for="task in todoTasks"
          :key="task.id"
          class="task"
          :class="{
            'task--active': activeTaskId === task.id,
            'task--completed': task.status === 'completed'
          }"
          @click="selectTask(task)"
          role="button"
          :tabindex="0"
          @keydown.enter="selectTask(task)"
          :aria-selected="activeTaskId === task.id"
        >
          <div class="task__status">
            <span v-if="task.status === 'completed'" class="task__check">✓</span>
            <span v-else-if="task.status === 'in_progress'" class="task__spinner"></span>
            <span v-else class="task__num">{{ task.id }}</span>
          </div>
          <div class="task__info">
            <span class="task__title">{{ task.title }}</span>
            <span class="task__intent">{{ task.intent }}</span>
          </div>
          <button
            v-if="task.status === 'failed'"
            class="task__retry"
            :disabled="retryingTaskId === task.id"
            @click.stop="handleRetryTask(task)"
            title="重试此任务"
            :aria-label="`重试任务: ${task.title}`"
          >
            <span v-if="retryingTaskId === task.id" class="task__spinner"></span>
            <span v-else>↻</span>
          </button>
        </div>
      </div>
      <p v-else class="sidebar__empty">等待任务规划...</p>
    </div>

    <div class="sidebar__section sidebar__section--logs">
      <h3 class="sidebar__title">研究日志</h3>
      <div class="logs" role="log" aria-live="polite">
        <div v-for="(log, idx) in progressLogs" :key="idx" class="log">
          <span class="log__dot"></span>
          <span class="log__text">{{ log }}</span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { TodoTaskView } from "../composables/useResearch";

defineProps<{
  todoTasks: TodoTaskView[];
  activeTaskId: number | null;
  progressLogs: string[];
  retryingTaskId: number | null;
}>();

const emit = defineEmits<{
  (e: "select-task", task: TodoTaskView): void;
  (e: "retry-task", task: TodoTaskView): void;
}>();

function selectTask(task: TodoTaskView) {
  emit("select-task", task);
}

function handleRetryTask(task: TodoTaskView) {
  emit("retry-task", task);
}
</script>

<style scoped>
.sidebar { display: flex; flex-direction: column; background: var(--color-bg-secondary); border-right: 1px solid var(--color-border); overflow: hidden; }
.sidebar__section { padding: 20px; border-bottom: 1px solid var(--color-divider); }
.sidebar__section--logs { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
.sidebar__title { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: var(--color-text-tertiary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }
.sidebar__empty { font-size: 12px; color: var(--color-text-muted); text-align: center; padding: 20px; }

.task-list { display: flex; flex-direction: column; gap: 8px; }
.task { display: flex; gap: 12px; padding: 12px; background: var(--color-bg-elevated); border: 1px solid transparent; border-radius: var(--radius-md); cursor: pointer; transition: all 0.2s ease; }
.task:hover { background: var(--color-bg-tertiary); }
.task--active { background: var(--color-accent-light); border-color: var(--color-accent); }
.task--completed .task__status { background: var(--color-success); color: white; }
.task__status { width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; background: var(--color-bg-tertiary); border-radius: 50%; font-size: 11px; font-weight: 600; color: var(--color-text-muted); flex-shrink: 0; }
.task--active .task__status { background: var(--color-accent); color: white; }
.task__check { font-size: 12px; }
.task__spinner { width: 10px; height: 10px; border: 2px solid transparent; border-top-color: currentColor; border-radius: 50%; animation: spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.task__info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.task__title { font-size: 12px; font-weight: 500; color: var(--color-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.task__intent { font-size: 12px; color: var(--color-text-muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.task__retry { display: flex; align-items: center; justify-content: center; width: 24px; height: 24px; border: none; background: var(--color-bg-tertiary); border-radius: 50%; font-size: 14px; color: var(--color-text-secondary); cursor: pointer; flex-shrink: 0; transition: all 0.2s ease; }
.task__retry:hover:not(:disabled) { background: var(--color-accent); color: white; }
.task__retry:disabled { opacity: 0.5; cursor: not-allowed; }

.logs { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.log { display: flex; gap: 8px; font-size: 12px; color: var(--color-text-secondary); }
.log__dot { width: 4px; height: 4px; background: var(--color-text-muted); border-radius: 50%; flex-shrink: 0; margin-top: 8px; }
</style>
