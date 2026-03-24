import { ref, computed, reactive, type Ref, type ComputedRef } from "vue";
import DOMPurify from "dompurify";
import {
  runResearchStream,
  retryTask,
  regenerateReport,
  type ResearchStreamEvent,
  type RetryTaskRequest,
  type RegenerateReportRequest,
} from "../services/api";

export interface SourceItem {
  title: string;
  url: string;
  snippet: string;
  raw: string;
}

export interface TodoTaskView {
  id: number;
  title: string;
  intent: string;
  query: string;
  status: string;
  summary?: string;
  sourceItems?: SourceItem[];
}

export interface UseResearchReturn {
  // State
  form: { topic: string; search_api: string };
  loading: Ref<boolean>;
  error: Ref<string>;
  progressLogs: Ref<string[]>;
  retryingTaskId: Ref<number | null>;
  isRegeneratingReport: Ref<boolean>;
  isExpanded: Ref<boolean>;
  todoTasks: Ref<TodoTaskView[]>;
  activeTaskId: Ref<number | null>;
  reportMarkdown: Ref<string>;

  // Computed
  totalTasks: ComputedRef<number>;
  completedTasks: ComputedRef<number>;
  progressPercent: ComputedRef<number>;
  currentTask: ComputedRef<TodoTaskView | undefined>;
  statusText: ComputedRef<string>;
  statusClass: ComputedRef<string>;

  // Methods
  handleSubmit: () => Promise<void>;
  handleRetryTask: (task: TodoTaskView) => Promise<void>;
  handleRegenerateReport: () => Promise<void>;
  selectTask: (task: TodoTaskView) => void;
  resetResearch: () => void;
  downloadReport: () => void;
  formatReport: (text: string) => string;
  abortController: AbortController | null;
}

export function useResearch(): UseResearchReturn {
  const form = reactive({
    topic: "",
    search_api: "",
  });

  const loading = ref(false);
  const error = ref("");
  const progressLogs = ref<string[]>([]);
  const retryingTaskId = ref<number | null>(null);
  const isRegeneratingReport = ref(false);
  const isExpanded = ref(false);

  const todoTasks = ref<TodoTaskView[]>([]);
  const activeTaskId = ref<number | null>(null);
  const reportMarkdown = ref("");

  let abortController: AbortController | null = null;

  const totalTasks = computed(() => todoTasks.value.length);
  const completedTasks = computed(() =>
    todoTasks.value.filter((t) => t.status === "completed").length
  );
  const progressPercent = computed(() =>
    totalTasks.value ? (completedTasks.value / totalTasks.value) * 100 : 0
  );

  const currentTask = computed(() =>
    todoTasks.value.find((t) => t.id === activeTaskId.value)
  );

  const statusText = computed(() => {
    if (loading.value) return "研究中";
    if (error.value) return "错误";
    if (completedTasks.value === totalTasks.value && totalTasks.value > 0)
      return "完成";
    return "就绪";
  });

  const statusClass = computed(() => {
    if (loading.value) return "status--running";
    if (error.value) return "status--error";
    if (completedTasks.value === totalTasks.value && totalTasks.value > 0)
      return "status--done";
    return "status--idle";
  });

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
      sourceItems: data.sources_summary
        ? parseSources(String(data.sources_summary))
        : undefined,
    };
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
      const task = todoTasks.value.find((t) => t.id === taskId);
      if (task) {
        const idx = todoTasks.value.findIndex((t) => t.id === taskId);
        if (idx !== -1) {
          todoTasks.value[idx] = {
            ...task,
            status: String(e.status || ""),
            summary: e.summary ? String(e.summary) : task.summary,
            sourceItems: e.sources_summary
              ? parseSources(String(e.sources_summary))
              : task.sourceItems,
          };
        }
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
      const task = todoTasks.value.find((t) => t.id === Number(e.task_id));
      if (task && e.raw_context) {
        const idx = todoTasks.value.findIndex((t) => t.id === Number(e.task_id));
        if (idx !== -1) {
          todoTasks.value[idx] = {
            ...task,
            sourceItems: parseSources(String(e.latest_sources || "")),
          };
        }
      }
      return;
    }

    if (e.type === "task_summary_chunk" && e.task_id) {
      const task = todoTasks.value.find((t) => t.id === Number(e.task_id));
      if (task) {
        const idx = todoTasks.value.findIndex((t) => t.id === Number(e.task_id));
        if (idx !== -1) {
          todoTasks.value[idx] = {
            ...task,
            summary: (task.summary || "") + String(e.content || ""),
          };
        }
      }
      return;
    }

    if (e.type === "tool_call") {
      progressLogs.value.push(
        String(e.agent || "Agent") + " 调用了 " + String(e.tool || "tool")
      );
      return;
    }

    if (e.type === "final_report") {
      const report =
        typeof e.report === "string" && e.report.trim()
          ? e.report.trim()
          : "";
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

  async function handleSubmit() {
    if (!form.topic.trim() || loading.value) return;
    loading.value = true;
    error.value = "";
    progressLogs.value = [];
    todoTasks.value = [];
    activeTaskId.value = null;
    reportMarkdown.value = "";
    isExpanded.value = true;
    abortController = new AbortController();

    try {
      await runResearchStream(
        { topic: form.topic, search_api: form.search_api || undefined },
        handleEvent,
        { signal: abortController.signal }
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

  async function handleRetryTask(task: TodoTaskView) {
    if (retryingTaskId.value !== null || !form.topic) return;

    retryingTaskId.value = task.id;
    progressLogs.value.push(`正在重试: ${task.title}...`);

    try {
      const result = await retryTask({
        topic: form.topic,
        task_id: task.id,
        tasks: todoTasks.value.map((t) => ({
          id: t.id,
          title: t.title,
          intent: t.intent,
          query: t.query,
          status: t.status,
          summary: t.summary,
          sources_summary: t.sourceItems
            ? t.sourceItems.map((s) => s.raw || "").join("\n")
            : undefined,
        })),
      });

      console.log("Retry result:", result);
      const taskId = Number(result.task_id);
      const idx = todoTasks.value.findIndex((t) => t.id === taskId);
      if (idx !== -1) {
        const existingTask = todoTasks.value[idx];
        if (existingTask) {
          todoTasks.value[idx] = {
            id: existingTask.id,
            title: existingTask.title,
            intent: existingTask.intent,
            query: existingTask.query,
            status: result.status,
            summary: result.summary,
          };
        }
      }

      progressLogs.value.push(`重试完成: ${result.title}`);
      if (activeTaskId.value === result.task_id) {
        activeTaskId.value = null;
        activeTaskId.value = result.task_id;
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "重试失败";
      progressLogs.value.push(`重试失败: ${msg}`);
      error.value = msg;
    } finally {
      retryingTaskId.value = null;
    }
  }

  async function handleRegenerateReport() {
    if (isRegeneratingReport.value || !form.topic || !todoTasks.value.length)
      return;

    isRegeneratingReport.value = true;
    progressLogs.value.push("正在重新生成报告...");

    try {
      const tasksData = todoTasks.value.map((t) => ({
        id: t.id,
        title: t.title,
        intent: t.intent,
        query: t.query,
        status: t.status,
        summary: t.summary,
        sources_summary: t.sourceItems
          ? t.sourceItems.map((s) => s.raw || "").join("\n")
          : undefined,
      }));

      const result = await regenerateReport({
        topic: form.topic,
        tasks: tasksData,
      });

      reportMarkdown.value = result.report;
      progressLogs.value.push(
        `报告已重新生成 (基于 ${result.task_count} 个任务)`
      );
    } catch (err) {
      const msg = err instanceof Error ? err.message : "重新生成报告失败";
      progressLogs.value.push(`重新生成报告失败: ${msg}`);
      error.value = msg;
    } finally {
      isRegeneratingReport.value = false;
    }
  }

  function selectTask(task: TodoTaskView) {
    activeTaskId.value = task.id;
  }

  function resetResearch() {
    isExpanded.value = false;
    form.topic = "";
    todoTasks.value = [];
    activeTaskId.value = null;
    reportMarkdown.value = "";
    progressLogs.value = [];
    error.value = "";
    if (abortController) {
      abortController.abort();
      abortController = null;
    }
  }

  function downloadReport() {
    const content = reportMarkdown.value;
    if (!content) return;
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    const topic =
      form.topic.trim().replace(/[^\u4e00-\u9fa5a-zA-Z0-9]/g, "_").slice(0, 20) ||
      "report";
    link.download = `${topic}_${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function formatReport(text: string): string {
    if (!text) return "";
    const html = text
      .replace(/^## (.+)$/gm, "<h2>$1</h2>")
      .replace(/^### (.+)$/gm, "<h3>$1</h3>")
      .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
      .replace(/\n\n/g, "</p><p>")
      .replace(/\n/g, "<br>");
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: [
        "h2",
        "h3",
        "strong",
        "p",
        "br",
        "ul",
        "ol",
        "li",
        "a",
        "em",
      ],
      ALLOWED_ATTR: ["href", "target", "rel"],
    });
  }

  return {
    form,
    loading,
    error,
    progressLogs,
    retryingTaskId,
    isRegeneratingReport,
    isExpanded,
    todoTasks,
    activeTaskId,
    reportMarkdown,
    totalTasks,
    completedTasks,
    progressPercent,
    currentTask,
    statusText,
    statusClass,
    handleSubmit,
    handleRetryTask,
    handleRegenerateReport,
    selectTask,
    resetResearch,
    downloadReport,
    formatReport,
    abortController,
  };
}
