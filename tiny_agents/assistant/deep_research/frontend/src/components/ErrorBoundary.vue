<template>
  <slot v-if="!error"></slot>
  <div v-else class="error-boundary" role="alert">
    <div class="error-boundary__icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
      </svg>
    </div>
    <h2 class="error-boundary__title">出错了</h2>
    <p class="error-boundary__message">{{ errorMessage }}</p>
    <div class="error-boundary__actions">
      <button class="btn btn--secondary" @click="handleRetry">
        重试
      </button>
      <button class="btn btn--primary" @click="handleReload">
        重新加载页面
      </button>
    </div>
    <details v-if="errorDetails" class="error-boundary__details">
      <summary>查看详情</summary>
      <pre>{{ errorDetails }}</pre>
    </details>
  </div>
</template>

<script setup lang="ts">
import { ref, onErrorCaptured } from "vue";

const errorMessage = ref("发生了未知错误");
const errorDetails = ref<string | null>(null);
const error = ref(false);

const emit = defineEmits<{
  (e: "error", error: Error): void;
  (e: "retry"): void;
}>();

onErrorCaptured((err: Error) => {
  error.value = true;
  errorMessage.value = err.message || "发生了未知错误";
  errorDetails.value = err.stack || null;
  emit("error", err);
  return false; // 阻止错误继续传播
});

function handleRetry() {
  error.value = false;
  errorMessage.value = "";
  errorDetails.value = null;
  emit("retry");
}

function handleReload() {
  window.location.reload();
}
</script>

<style scoped>
.error-boundary {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  margin: 24px;
}

.error-boundary__icon {
  width: 64px;
  height: 64px;
  color: var(--color-error);
  margin-bottom: 16px;
}

.error-boundary__icon svg {
  width: 100%;
  height: 100%;
}

.error-boundary__title {
  font-size: 20px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.error-boundary__message {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 24px;
  max-width: 400px;
}

.error-boundary__actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.error-boundary__details {
  margin-top: 16px;
  text-align: left;
  width: 100%;
  max-width: 600px;
}

.error-boundary__details summary {
  cursor: pointer;
  font-size: 12px;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}

.error-boundary__details pre {
  background: var(--color-bg-secondary);
  padding: 12px;
  border-radius: var(--radius-md);
  font-size: 11px;
  overflow-x: auto;
  color: var(--color-text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 500;
  border: none;
  transition: all 0.2s ease;
  cursor: pointer;
}

.btn--primary {
  background: var(--color-accent);
  color: white;
}

.btn--primary:hover {
  background: var(--color-accent-hover);
}

.btn--secondary {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.btn--secondary:hover {
  background: var(--color-bg-secondary);
}
</style>
