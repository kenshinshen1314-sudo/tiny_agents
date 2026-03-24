<template>
  <div class="app" :class="{ 'app--expanded': isExpanded }">
    <!-- 顶部导航 -->
    <header class="header" v-if="isExpanded">
      <div class="header__left">
        <button class="btn btn--icon" @click="$emit('reset')" title="返回">
        </button>
        <h1 class="header__title">{{ topic }}</h1>
        <span class="header__status" :class="statusClass">{{ statusText }}</span>
      </div>
      <div class="header__right">
        <div class="progress">
          <div class="progress__bar">
            <div class="progress__fill" :style="{ width: `${progressPercent}%` }"></div>
          </div>
          <span class="progress__text">{{ completedTasks }}/{{ totalTasks }}</span>
        </div>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main">
      <div class="workspace">
        <!-- 研究模式侧边栏 -->
        <aside class="sidebar">
          <div class="sidebar__section">
            <h3 class="sidebar__title">
              研究任务
            </h3>
            <div class="task-list" v-if="todoTasks.length">
              <div
                v-for="task in todoTasks"
                :key="task.id"
                class="task"
                :class="{
                  'task--active': activeTaskId === task.id,
                  'task--completed': task.status === 'completed'
                }"
                @click="$emit('select-task', task)"
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
              </div>
            </div>
            <p v-else class="sidebar__empty">等待任务规划...</p>
          </div>

          <div class="sidebar__section sidebar__section--logs">
            <h3 class="sidebar__title">
              研究日志
            </h3>
            <div class="logs">
              <div v-for="(log, idx) in progressLogs" :key="idx" class="log">
                <span class="log__dot"></span>
                <span class="log__text">{{ log }}</span>
              </div>
            </div>
          </div>
        </aside>

        <div class="content">
          <section class="panel" v-if="currentTask">
            <div class="panel__header">
              <div>
                <h2 class="panel__title">{{ currentTask.title }}</h2>
                <p class="panel__intent">{{ currentTask.intent }}</p>
              </div>
              <span class="badge" :class="`badge--${currentTask.status}`">
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
                  class="source"
                >
                  <span class="source__title">{{ source.title }}</span>
                  <span class="source__url">{{ formatUrl(source.url) }}</span>
                </a>
              </div>
            </div>
          </section>

          <div class="empty-state" v-else>
            <div class="empty-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
            </div>
            <p>选择一个任务查看详情</p>
          </div>

          <section class="report" v-if="reportMarkdown">
            <div class="report__header">
              <h3 class="report__title">
                最终报告
              </h3>
              <div class="report__actions">
                <button v-if="needsManualStart" class="btn btn--primary btn--sm" @click="$emit('start-research')">
                  开始执行
                </button>
                <button class="btn btn--secondary btn--sm" @click="$emit('download-report')">
                  下载
                </button>
              </div>
            </div>
            <div class="report__content" v-html="formatReport(reportMarkdown)"></div>
          </section>

          <div class="report-loading" v-else-if="loading">
            <div class="spinner"></div>
            <p>正在生成研究报告...</p>
            <span>完成所有任务后将自动生成</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface SourceItem {
  title: string;
  url: string;
  snippet: string;
  raw: string;
}

interface TodoTaskView {
  id: number;
  title: string;
  intent: string;
  query: string;
  status: string;
  summary?: string;
  sourceItems?: SourceItem[];
}

const props = defineProps<{
  topic: string;
  loading: boolean;
  error: string;
  progressLogs: string[];
  isExpanded: boolean;
  todoTasks: TodoTaskView[];
  activeTaskId: number | null;
  reportMarkdown: string;
}>();

defineEmits<{
  (e: 'reset'): void;
  (e: 'select-task', task: TodoTaskView): void;
  (e: 'download-report'): void;
  (e: 'start-research'): void;
}>();

const totalTasks = computed(() => props.todoTasks.length);
const completedTasks = computed(() =>
  props.todoTasks.filter(t => t.status === "completed").length
);
const progressPercent = computed(() =>
  totalTasks.value ? (completedTasks.value / totalTasks.value) * 100 : 0
);

const currentTask = computed(() =>
  props.todoTasks.find(t => t.id === props.activeTaskId)
);

// 检测报告是否显示"任务尚未执行"提示
const needsManualStart = computed(() => {
  if (!props.reportMarkdown) return false;
  return props.reportMarkdown.includes("报告生成受阻") ||
         props.reportMarkdown.includes("任务状态") &&
         props.reportMarkdown.includes("pending") &&
         !props.loading &&
         completedTasks.value === 0;
});

const statusText = computed(() => {
  if (props.loading) return "研究中";
  if (props.error) return "错误";
  if (completedTasks.value === totalTasks.value && totalTasks.value > 0) return "完成";
  return "就绪";
});

const statusClass = computed(() => {
  if (props.loading) return "status--running";
  if (props.error) return "status--error";
  if (completedTasks.value === totalTasks.value && totalTasks.value > 0) return "status--done";
  return "status--idle";
});

function formatStatus(status: string): string {
  const map: Record<string, string> = {
    pending: "待处理",
    in_progress: "进行中",
    completed: "已完成",
    skipped: "已跳过",
    failed: "失败"
  };
  return map[status] || status;
}

function formatUrl(url: string): string {
  try { return new URL(url).hostname; } catch { return url; }
}

function formatReport(text: string): string {
  if (!text) return "";
  return text
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');
}
</script>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

.header { display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: var(--color-bg-elevated); border-bottom: 1px solid var(--color-border); flex-shrink: 0; min-height: 56px; gap: 16px; }
.header__left { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.header__title { font-size: 16px; font-weight: 500; color: var(--color-text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.header__status { font-size: 12px; padding: 4px 10px; border-radius: 12px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); flex-shrink: 0; }
.header__status.status--running { background: var(--color-accent-light); color: var(--color-accent); }
.header__status.status--done { background: #D1FAE5; color: var(--color-success); }
.header__status.status--error { background: #FEE2E2; color: var(--color-error); }

.header__right { flex-shrink: 0; }
.progress { display: flex; align-items: center; gap: 12px; }
.progress__bar { width: 120px; height: 6px; background: var(--color-bg-tertiary); border-radius: 3px; overflow: hidden; }
.progress__fill { height: 100%; background: var(--color-accent); border-radius: 3px; transition: width 0.3s ease; }
.progress__text { font-size: 13px; color: var(--color-text-secondary); white-space: nowrap; }

.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 16px; border-radius: var(--radius-md); font-size: 12px; font-weight: 500; border: none; transition: all 0.2s ease; }
.btn--icon { width: 36px; height: 36px; padding: 0; background: transparent; border: 1px solid var(--color-border); }
.btn--icon svg { width: 18px; height: 18px; }
.btn--icon:hover { background: var(--color-bg-tertiary); }
.btn--secondary { background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border); }
.btn--secondary:hover { background: var(--color-bg-secondary); border-color: var(--color-border-hover); }
.btn--sm { padding: 6px 12px; font-size: 12px; }
.btn--sm svg { width: 14px; height: 14px; }

.main { flex: 1; display: flex; min-height: 0; overflow: hidden; }

.workspace { flex: 1; display: grid; grid-template-columns: 320px 1fr; min-height: 0; overflow: hidden; }

.sidebar { display: flex; flex-direction: column; background: var(--color-bg-secondary); border-right: 1px solid var(--color-border); overflow: hidden; }
.sidebar__section { padding: 20px; border-bottom: 1px solid var(--color-divider); }
.sidebar__section--logs { flex: 1; overflow: hidden; display: flex; flex-direction: column; }
.sidebar__title { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: var(--color-text-tertiary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px; }
.sidebar__title svg { width: 16px; height: 16px; }
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

.logs { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
.log { display: flex; gap: 8px; font-size: 12px; color: var(--color-text-secondary); }
.log__dot { width: 4px; height: 4px; background: var(--color-text-muted); border-radius: 50%; flex-shrink: 0; margin-top: 8px; }

.content { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 24px; min-width: 0; }

.panel, .report { background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 24px; }
.panel__header, .report__header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; }
.report__actions { display: flex; gap: 8px; align-items: center; }
.panel__title, .report__title { font-size: 20px; font-weight: 600; color: var(--color-text-primary); margin-bottom: 4px; }
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

.report__content { padding: 16px 20px; font-size: 13px; line-height: 1.7; color: var(--color-text-primary); }
.report__content :deep(h2) { font-size: 18px; font-weight: 600; color: var(--color-text-primary); margin: 24px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--color-divider); }
.report__content :deep(h3) { font-size: 15px; font-weight: 600; color: var(--color-text-primary); margin: 20px 0 10px; }
.report__content :deep(p) { margin-bottom: 12px; }
.report__content :deep(strong) { color: var(--color-accent); }

.report-loading { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 48px; }
.spinner { width: 40px; height: 40px; border: 3px solid var(--color-bg-tertiary); border-top-color: var(--color-accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px; }
.report-loading p { font-size: 16px; color: var(--color-text-primary); margin-bottom: 4px; }
.report-loading span { font-size: 12px; color: var(--color-text-muted); }

@media (max-width: 1024px) { .workspace { grid-template-columns: 1fr; } .sidebar { display: none; } }
</style>