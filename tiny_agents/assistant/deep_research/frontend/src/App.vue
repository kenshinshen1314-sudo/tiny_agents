<template>
  <div class="app" :class="{ 'app--expanded': isExpanded }">
    <!-- 顶部导航 -->
    <header class="header" v-if="isExpanded">
      <div class="header__left">
        <button class="btn btn--icon" @click="resetResearch" title="返回">
        </button>
        <h1 class="header__title">{{ form.topic }}</h1>
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
      <!-- 初始状态 -->
      <div v-if="!isExpanded" class="hero">
        <div class="hero__content">
          <!-- Logo -->
          <div class="hero__logo">
            <div class="logo-icon">
              <svg viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="14" stroke="currentColor" stroke-width="1.5"/>
                <path d="M10 16C10 12.6863 12.6863 10 16 10C19.3137 10 22 12.6863 22 16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                <circle cx="16" cy="20" r="2" fill="currentColor"/>
              </svg>
            </div>
            <div class="logo-text">
              <span class="logo-name">深度研究</span>
              <span class="logo-tagline">Deep Research</span>
            </div>
          </div>

          <h2 class="hero__title">探索任何主题的深度洞察</h2>
          <p class="hero__subtitle">基于多轮智能检索与深度分析，实时生成专业研究报告</p>

          <!-- 输入框 -->
          <div class="input-area">
            <div class="input-card">
              <textarea
                v-model="form.topic"
                placeholder="输入你想要深入研究的主题..."
                rows="3"
                class="input"
                @keydown.enter.meta="handleSubmit"
                @keydown.enter.ctrl="handleSubmit"
              ></textarea>
              <div class="input-actions">
                <select v-model="form.search_api" class="select">
                  <option value="">搜索引擎</option>
                  <option v-for="opt in searchOptions" :key="opt" :value="opt">{{ opt }}</option>
                </select>
                <button class="btn btn--primary" @click="handleSubmit" :disabled="loading || !form.topic.trim()">
                  <span v-if="!loading">开始研究</span>
                  <span v-else class="loading">
                    <span class="loading__dot"></span>
                    <span class="loading__dot"></span>
                    <span class="loading__dot"></span>
                  </span>
                </button>
              </div>
            </div>
          </div>

          <!-- 示例 -->
          <div class="examples">
            <span class="examples__label">试试：</span>
            <button class="example" @click="form.topic = '人工智能在医疗领域的应用'">AI 医疗</button>
            <button class="example" @click="form.topic = '量子计算发展趋势'">量子计算</button>
            <button class="example" @click="form.topic = '全球气候变化应对策略'">气候变化</button>
            <button class="example" @click="form.topic = '深度研究openclaw的安全问题'">openclaw安全</button>
            <button class="example" @click="form.topic = '深度研究openclaw助力opc(一人公司)的几个方向'">openclaw opc</button>

          </div>

          <!-- 底部 -->
          <div class="hero__footer">
            <div class="feature">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <span>智能搜索</span>
            </div>
            <div class="feature">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>多源整合</span>
            </div>
            <div class="feature">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
              </svg>
              <span>结构化报告</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 研究状态 -->
      <div v-else class="workspace">
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
                @click="selectTask(task)"
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
              <button class="btn btn--secondary btn--sm" @click="downloadReport">
                下载
              </button>
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
import { computed, onBeforeUnmount, reactive, ref } from "vue";
import { runResearchStream, type ResearchStreamEvent } from "./services/api";

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

const form = reactive({
  topic: "",
  search_api: "" as string,
});

const loading = ref(false);
const error = ref("");
const progressLogs = ref<string[]>([]);
const isExpanded = ref(false);

const todoTasks = ref<TodoTaskView[]>([]);
const activeTaskId = ref<number | null>(null);
const reportMarkdown = ref("");

const searchOptions = ["tavily", "serpapi", "duckduckgo", "searxng"];

const totalTasks = computed(() => todoTasks.value.length);
const completedTasks = computed(() =>
  todoTasks.value.filter(t => t.status === "completed").length
);
const progressPercent = computed(() =>
  totalTasks.value ? (completedTasks.value / totalTasks.value) * 100 : 0
);

const currentTask = computed(() =>
  todoTasks.value.find(t => t.id === activeTaskId.value)
);

const statusText = computed(() => {
  if (loading.value) return "研究中";
  if (error.value) return "错误";
  if (completedTasks.value === totalTasks.value && totalTasks.value > 0) return "完成";
  return "就绪";
});

const statusClass = computed(() => {
  if (loading.value) return "status--running";
  if (error.value) return "status--error";
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

function selectTask(task: TodoTaskView) { activeTaskId.value = task.id; }

function resetResearch() {
  isExpanded.value = false;
  form.topic = "";
  todoTasks.value = [];
  activeTaskId.value = null;
  reportMarkdown.value = "";
  progressLogs.value = [];
  error.value = "";
}

function downloadReport() {
  const content = reportMarkdown.value;
  if (!content) return;
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  const topic = form.topic.trim().replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, "_").slice(0, 20) || "report";
  link.download = `${topic}_${new Date().toISOString().slice(0, 10)}.md`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

function parseSources(raw: string): SourceItem[] {
  if (!raw || typeof raw !== "string") return [];
  const items: SourceItem[] = [];
  const lines = String(raw).split("\n");
  let current: Partial<SourceItem> | null = null;
  for (const line of lines) {
    if (!line) continue;
    const titleMatch = line.match(/^\* (.+?) :/);
    const urlMatch = line.match(/: (https?:\/\/[^\s]+)/);
    if (titleMatch && titleMatch[1]) {
      if (current?.title) items.push(current as SourceItem);
      current = { title: titleMatch[1], url: "", snippet: "", raw: "" };
    } else if (urlMatch && urlMatch[1] && current) {
      current.url = urlMatch[1];
    }
  }
  if (current?.title) items.push(current as SourceItem);
  return items.slice(0, 5);
}

function parseTask(data: any): TodoTaskView {
  return {
    id: Number(data.id) || 0,
    title: String(data.title || ""),
    intent: String(data.intent || ""),
    query: String(data.query || ""),
    status: String(data.status || "pending"),
    summary: data.summary ? String(data.summary) : undefined,
    sourceItems: data.sources_summary ? parseSources(String(data.sources_summary)) : undefined
  };
}

async function handleSubmit() {
  if (!form.topic.trim() || loading.value) return;
  loading.value = true;
  error.value = "";
  progressLogs.value = [];
  todoTasks.value = [];
  activeTaskId.value = null;
  reportMarkdown.value = "";
  isExpanded.value = true;
  const controller = new AbortController();
  try {
    await runResearchStream(
      { topic: form.topic, search_api: form.search_api || undefined },
      handleEvent,
      { signal: controller.signal }
    );
    if (!reportMarkdown.value) reportMarkdown.value = "报告生成中...";
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      progressLogs.value.push("已取消");
    } else {
      error.value = err instanceof Error ? err.message : "未知错误";
      progressLogs.value.push("错误: " + error.value);
    }
  } finally {
    loading.value = false;
  }
}

function handleEvent(event: ResearchStreamEvent) {
  const e = event as Record<string, unknown>;
  if (e.type === "todo_list" && Array.isArray(e.tasks)) {
    todoTasks.value = (e.tasks as unknown[]).map((t: any) => parseTask(t));
    progressLogs.value.push("已规划 " + todoTasks.value.length + " 个任务");
    return;
  }
  if (e.type === "task_status") {
    const taskId = Number(e.task_id) || 0;
    const task = todoTasks.value.find(t => t.id === taskId);
    if (task) {
      task.status = String(e.status || "");
      if (e.summary) task.summary = String(e.summary);
      if (e.sources_summary) task.sourceItems = parseSources(String(e.sources_summary));
    }
    const status = String(e.status || "");
    if (status === "in_progress") {
      activeTaskId.value = taskId || null;
      progressLogs.value.push("开始: " + String(e.title || ""));
    } else if (status === "completed") {
      progressLogs.value.push("完成: " + String(e.title || ""));
    } else if (status === "failed") {
      progressLogs.value.push("失败: " + String(e.title || ""));
    }
    return;
  }
  if (e.type === "sources" && e.task_id) {
    const task = todoTasks.value.find(t => t.id === Number(e.task_id));
    if (task && e.raw_context) task.sourceItems = parseSources(String(e.latest_sources || ""));
    return;
  }
  if (e.type === "task_summary_chunk" && e.task_id) {
    const task = todoTasks.value.find(t => t.id === Number(e.task_id));
    if (task) task.summary = (task.summary || "") + String(e.content || "");
    return;
  }
  if (e.type === "tool_call") {
    progressLogs.value.push(String(e.agent || "Agent") + " 调用了 " + String(e.tool || "tool"));
    return;
  }
  if (e.type === "final_report") {
    const report = typeof e.report === "string" && e.report.trim() ? e.report.trim() : "";
    reportMarkdown.value = report || "报告生成失败";
    progressLogs.value.push("报告已生成");
    return;
  }
  if (e.type === "error") {
    const detail = typeof e.detail === "string" ? e.detail : "错误";
    error.value = detail;
    progressLogs.value.push("错误: " + detail);
    return;
  }
}

onBeforeUnmount(() => {});
</script>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; }

.header { display: flex; align-items: center; justify-content: space-between; padding: 12px 24px; background: var(--color-bg-elevated); border-bottom: 1px solid var(--color-border); position: sticky; top: 0; z-index: 100; }
.header__left { display: flex; align-items: center; gap: 16px; }
.header__title { font-size: 16px; font-weight: 500; color: var(--color-text-primary); }
.header__status { font-size: 12px; padding: 4px 10px; border-radius: 12px; background: var(--color-bg-tertiary); color: var(--color-text-secondary); }
.header__status.status--running { background: var(--color-accent-light); color: var(--color-accent); }
.header__status.status--done { background: #D1FAE5; color: var(--color-success); }
.header__status.status--error { background: #FEE2E2; color: var(--color-error); }

.progress { display: flex; align-items: center; gap: 12px; }
.progress__bar { width: 100px; height: 4px; background: var(--color-bg-tertiary); border-radius: 2px; overflow: hidden; }
.progress__fill { height: 100%; background: var(--color-accent); border-radius: 2px; transition: width 0.3s ease; }
.progress__text { font-size: 12px; color: var(--color-text-tertiary); }

.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 16px; border-radius: var(--radius-md); font-size: 12px; font-weight: 500; border: none; transition: all 0.2s ease; }
.btn--icon { width: 36px; height: 36px; padding: 0; background: transparent; border: 1px solid var(--color-border); }
.btn--icon svg { width: 18px; height: 18px; }
.btn--icon:hover { background: var(--color-bg-tertiary); }
.btn--primary { background: var(--color-accent); color: white; }
.btn--primary:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn--primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn--secondary { background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border); }
.btn--secondary:hover { background: var(--color-bg-secondary); border-color: var(--color-border-hover); }
.btn--sm { padding: 6px 12px; font-size: 12px; }
.btn--sm svg { width: 14px; height: 14px; }

.main { flex: 1; display: flex; }

.hero { flex: 1; display: flex; align-items: center; justify-content: center; padding: 48px 24px; }
.hero__content { max-width: 640px; width: 100%; text-align: center; }

.hero__logo { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 32px; }
.logo-icon { width: 48px; height: 48px; color: var(--color-accent); }
.logo-icon svg { width: 100%; height: 100%; }
.logo-text { display: flex; flex-direction: column; align-items: flex-start; }
.logo-name { font-size: 20px; font-weight: 600; color: var(--color-text-primary); letter-spacing: -0.5px; }
.logo-tagline { font-size: 11px; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 1px; }

.hero__title { font-family: var(--font-serif); font-size: 42px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 12px; letter-spacing: -1px; }
.hero__subtitle { font-size: 16px; color: var(--color-text-secondary); margin-bottom: 32px; }

.input-area { margin-bottom: 24px; }
.input-card { background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-xl); padding: 4px; box-shadow: var(--shadow-lg); }
.input { width: 100%; padding: 16px 20px; background: transparent; border: none; font-size: 15px; color: var(--color-text-primary); resize: none; outline: none; }
.input::placeholder { color: var(--color-text-muted); }
.input-actions { display: flex; justify-content: space-between; padding: 4px 8px; border-top: 1px solid var(--color-divider); }
.select { padding: 4px 8px; background: transparent; border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: 12px; color: var(--color-text-secondary); cursor: pointer; }
.select:hover { border-color: var(--color-border-hover); }

.loading { display: flex; align-items: center; gap: 4px; }
.loading__dot { width: 6px; height: 6px; background: white; border-radius: 50%; animation: loadingBounce 1.4s ease-in-out infinite; }
.loading__dot:nth-child(1) { animation-delay: 0s; }
.loading__dot:nth-child(2) { animation-delay: 0.2s; }
.loading__dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes loadingBounce { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }

.examples { display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap; }
.examples__label { font-size: 12px; color: var(--color-text-muted); }
.example { padding: 6px 14px; background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-radius: var(--radius-full); font-size: 12px; color: var(--color-text-secondary); transition: all 0.2s ease; }
.example:hover { background: var(--color-bg-secondary); border-color: var(--color-accent); color: var(--color-accent); }

.hero__footer { display: flex; justify-content: center; gap: 32px; margin-top: 48px; padding-top: 32px; border-top: 1px solid var(--color-divider); }
.feature { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--color-text-muted); }
.feature svg { width: 16px; height: 16px; }

.workspace { flex: 1; display: grid; grid-template-columns: 320px 1fr; min-height: 0; }

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

.content { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 24px; }

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

.report { background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; }
.report__header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--color-divider); }
.report__title { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: var(--color-text-primary); }
.report__title svg { width: 18px; height: 18px; color: var(--color-accent); }
.report__content { padding: 20px; font-size: 12px; line-height: 1.8; color: var(--color-text-primary); max-height: 500px; overflow-y: auto; }
.report__content :deep(h2) { font-size: 18px; font-weight: 600; color: var(--color-text-primary); margin: 24px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--color-divider); }
.report__content :deep(h3) { font-size: 15px; font-weight: 600; color: var(--color-text-primary); margin: 20px 0 8px; }
.report__content :deep(p) { margin-bottom: 12px; }
.report__content :deep(strong) { color: var(--color-accent); }

.report-loading { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 48px; }
.spinner { width: 40px; height: 40px; border: 3px solid var(--color-bg-tertiary); border-top-color: var(--color-accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px; }
.report-loading p { font-size: 16px; color: var(--color-text-primary); margin-bottom: 4px; }
.report-loading span { font-size: 12px; color: var(--color-text-muted); }

@media (max-width: 1024px) { .workspace { grid-template-columns: 1fr; } .sidebar { display: none; } }
@media (max-width: 768px) { .hero__title { font-size: 28px; } .hero__footer { flex-direction: column; gap: 16px; } }
</style>
