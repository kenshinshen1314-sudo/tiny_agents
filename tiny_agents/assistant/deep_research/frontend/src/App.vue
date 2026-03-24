<template>
  <ErrorBoundary @retry="handleGlobalRetry">
    <div class="app" :class="{ 'app--expanded': isExpanded }">
      <!-- 顶部导航 -->
      <AppHeader
        v-if="isExpanded"
        :topic="form.topic"
        :status-text="statusText"
        :status-class="statusClass"
        :progress-percent="progressPercent"
        :completed-tasks="completedTasks"
        :total-tasks="totalTasks"
        @reset="resetResearch"
      />

      <!-- 主内容区 -->
      <main class="main">
        <!-- 初始状态 -->
        <ResearchInput
          v-if="!isExpanded"
          :form="form"
          :loading="loading"
          @submit="handleSubmit"
        />

        <!-- 研究状态 -->
        <div v-else class="workspace">
          <TaskSidebar
            :todo-tasks="todoTasks"
            :active-task-id="activeTaskId"
            :progress-logs="progressLogs"
            :retrying-task-id="retryingTaskId"
            @select-task="selectTask"
            @retry-task="handleRetryTask"
          />

          <div class="content">
            <TaskPanel :current-task="currentTask" />

            <ErrorBoundary @retry="handleReportRetry">
              <ReportView
                :report-markdown="reportMarkdown"
                :loading="loading"
                :is-regenerating-report="isRegeneratingReport"
                :sanitized-content="formatReport(reportMarkdown)"
                @regenerate="handleRegenerateReport"
                @download="downloadReport"
              />
            </ErrorBoundary>
          </div>
        </div>
      </main>
    </div>
  </ErrorBoundary>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount } from "vue";
import { useResearch } from "./composables/useResearch";
import AppHeader from "./components/AppHeader.vue";
import ResearchInput from "./components/ResearchInput.vue";
import TaskSidebar from "./components/TaskSidebar.vue";
import TaskPanel from "./components/TaskPanel.vue";
import ReportView from "./components/ReportView.vue";
import ErrorBoundary from "./components/ErrorBoundary.vue";

const research = useResearch();

const {
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
} = research;

// 全局未捕获 Promise 错误处理
function handleUnhandledRejection(event: PromiseRejectionEvent) {
  console.error("Unhandled Promise rejection:", event.reason);
  event.preventDefault();
}

// 全局 JS 错误处理
function handleGlobalError(event: ErrorEvent) {
  console.error("Global error:", event.error);
}

// 报告区域重试
function handleReportRetry() {
  console.log("Report retry requested");
}

// 全局重试
function handleGlobalRetry() {
  console.log("Global retry requested");
  resetResearch();
}

onMounted(() => {
  window.addEventListener("unhandledrejection", handleUnhandledRejection);
  window.addEventListener("error", handleGlobalError);
});

onBeforeUnmount(() => {
  window.removeEventListener("unhandledrejection", handleUnhandledRejection);
  window.removeEventListener("error", handleGlobalError);

  if (research.abortController) {
    research.abortController.abort();
  }
});
</script>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; }
.main { flex: 1; display: flex; }
.workspace { flex: 1; display: grid; grid-template-columns: 320px 1fr; min-height: 0; }
.content { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 24px; }

@media (max-width: 1024px) {
  .workspace { grid-template-columns: 1fr; }
  .sidebar { display: none; }
}
</style>
