<template>
  <section class="panel" v-if="currentTask" aria-labelledby="task-title">
    <div class="panel__header">
      <div>
        <h2 id="task-title" class="panel__title">{{ currentTask.title }}</h2>
        <p class="panel__intent">{{ currentTask.intent }}</p>
      </div>
      <span class="badge" :class="`badge--${currentTask.status}`" role="status">
        {{ formatStatus(currentTask.status) }}
      </span>
    </div>

    <div class="panel__query" v-if="currentTask.query">
      <span class="query__label">检索词</span>
      <code class="query__text">{{ currentTask.query }}</code>
    </div>

    <div class="panel__section" v-if="currentTask.summary">
      <h3 class="panel__section-title">任务总结</h3>
      <div class="summary">{{ currentTask.summary }}</div>
    </div>

    <div class="panel__section" v-if="currentTask.sourceItems?.length">
      <h3 class="panel__section-title">信息来源</h3>
      <div class="sources">
        <a
          v-for="(source, idx) in currentTask.sourceItems"
          :key="idx"
          :href="source.url"
          target="_blank"
          rel="noopener noreferrer"
          class="source"
        >
          <span class="source__title">{{ source.title }}</span>
          <span class="source__url">{{ formatUrl(source.url) }}</span>
        </a>
      </div>
    </div>
  </section>

  <div v-else class="empty-state" role="status">
    <div class="empty-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
      </svg>
    </div>
    <p>选择一个任务查看详情</p>
  </div>
</template>

<script setup lang="ts">
import type { TodoTaskView } from "../composables/useResearch";

defineProps<{
  currentTask?: TodoTaskView;
}>();

function formatStatus(status: string): string {
  const map: Record<string, string> = {
    pending: "待处理",
    in_progress: "进行中",
    completed: "已完成",
    skipped: "已跳过",
    failed: "失败",
  };
  return map[status] || status;
}

function formatUrl(url: string): string {
  try {
    return new URL(url).hostname;
  } catch {
    return url;
  }
}
</script>

<style scoped>
.panel { background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 24px; }
.panel__header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.panel__title { font-size: 20px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 4px; }
.panel__intent { font-size: 12px; color: var(--color-text-secondary); }
.badge { font-size: 12px; padding: 4px 10px; border-radius: 12px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); }
.badge--completed { background: #D1FAE5; color: var(--color-success); }
.badge--in_progress { background: var(--color-accent-light); color: var(--color-accent); }
.badge--failed { background: #FEE2E2; color: var(--color-error); }

.panel__query { display: flex; align-items: center; gap: 8px; padding: 12px; background: var(--color-bg-secondary); border-radius: var(--radius-md); margin-bottom: 20px; }
.query__label { font-size: 11px; color: var(--color-text-muted); text-transform: uppercase; }
.query__text { font-family: var(--font-mono); font-size: 12px; color: var(--color-accent); }

.panel__section { margin-top: 20px; }
.panel__section-title { font-size: 12px; font-weight: 600; color: var(--color-text-tertiary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px; }

.summary { font-size: 12px; line-height: 1.7; color: var(--color-text-primary); padding: 16px; background: var(--color-bg-secondary); border-radius: var(--radius-md); border-left: 3px solid var(--color-accent); }

.sources { display: flex; flex-direction: column; gap: 8px; }
.source { display: flex; flex-direction: column; gap: 2px; padding: 12px; background: var(--color-bg-secondary); border: 1px solid var(--color-border); border-radius: var(--radius-md); text-decoration: none; transition: all 0.2s ease; }
.source:hover { background: var(--color-bg-tertiary); border-color: var(--color-border-hover); }
.source__title { font-size: 12px; color: var(--color-text-primary); }
.source__url { font-size: 12px; color: var(--color-text-muted); }

.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: var(--color-text-muted); }
.empty-icon { width: 64px; height: 64px; margin-bottom: 16px; opacity: 0.3; }
.empty-icon svg { width: 100%; height: 100%; }
</style>
