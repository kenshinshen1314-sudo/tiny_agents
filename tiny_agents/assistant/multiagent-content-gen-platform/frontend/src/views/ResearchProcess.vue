<template>
  <ResearchProcessResult
    :topic="topic"
    :loading="loading"
    :error="error"
    :progress-logs="progressLogs"
    :is-expanded="true"
    :todo-tasks="todoTasks"
    :active-task-id="activeTaskId"
    :report-markdown="reportMarkdown"
    @reset="goHome"
    @select-task="selectTask"
    @download-report="downloadReport"
    @start-research="restartResearch"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { runResearchStream, type ResearchStreamEvent } from "../services/api";
import ResearchProcessResult from "../components/ResearchProcessResult.vue";

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

const route = useRoute();
const router = useRouter();

const topic = ref(route.query.topic as string || "");
const mode = ref(route.query.mode as string || "research");
const platform = ref(route.query.platform as string || "wechat");
const style = ref(route.query.style as string || "rational");
const searchApi = ref(route.query.search_api as string || "");

const loading = ref(false);
const error = ref("");
const progressLogs = ref<string[]>([]);
const todoTasks = ref<TodoTaskView[]>([]);
const activeTaskId = ref<number | null>(null);
const reportMarkdown = ref("");

const totalTasks = ref(0);
const completedTasks = ref(0);

function goHome() {
  router.push('/');
}

function selectTask(task: TodoTaskView) {
  activeTaskId.value = task.id;
}

function downloadReport() {
  const content = reportMarkdown.value;
  if (!content) return;
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  const topicName = topic.value.trim().replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, "_").slice(0, 20) || "report";
  link.download = `${topicName}_${new Date().toISOString().slice(0, 10)}.md`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function restartResearch() {
  // 重置状态并重新执行研究
  loading.value = true;
  error.value = "";
  progressLogs.value = [];
  todoTasks.value = [];
  activeTaskId.value = null;
  reportMarkdown.value = "";
  completedTasks.value = 0;
  totalTasks.value = 0;

  try {
    await runResearchStream(
      { topic: topic.value, search_api: searchApi.value || undefined },
      handleEvent
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

function handleEvent(event: ResearchStreamEvent) {
  const e = event as Record<string, unknown>;
  if (e.type === "todo_list" && Array.isArray(e.tasks)) {
    todoTasks.value = (e.tasks as unknown[]).map((t: any) => parseTask(t));
    totalTasks.value = todoTasks.value.length;
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
    completedTasks.value = todoTasks.value.filter(t => t.status === "completed").length;
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

onMounted(async () => {
  if (mode.value === "content") {
    // 内容创作模式
    loading.value = true;
    progressLogs.value = ["正在生成内容..."];
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/content/generate/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.value,
          platform: platform.value,
          style: style.value,
        }),
      });
      if (!response.ok) throw new Error(`生成失败: ${response.status}`);
      const reader = response.body?.getReader();
      if (!reader) throw new Error("无法读取响应");
      const decoder = new TextDecoder();
      let contentResult = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        const lines = text.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                contentResult += data.chunk;
                reportMarkdown.value = contentResult;
              } else if (data.done) {
                progressLogs.value = ["内容生成完成!"];
              } else if (data.error) {
                throw new Error(data.error);
              }
            } catch {}
          }
        }
      }
    } catch (err) {
      error.value = err instanceof Error ? err.message : "未知错误";
      progressLogs.value = ["错误: " + error.value];
    } finally {
      loading.value = false;
    }
  } else {
    // 研究模式
    loading.value = true;
    progressLogs.value = [];
    todoTasks.value = [];
    activeTaskId.value = null;
    reportMarkdown.value = "";
    try {
      await runResearchStream(
        { topic: topic.value, search_api: searchApi.value || undefined },
        handleEvent
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
});
</script>