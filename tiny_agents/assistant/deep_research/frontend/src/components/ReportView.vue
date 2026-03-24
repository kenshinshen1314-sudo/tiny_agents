<template>
  <section class="report" v-if="reportMarkdown" aria-labelledby="report-title">
    <div class="report__header">
      <h3 id="report-title" class="report__title">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        最终报告
      </h3>
      <div class="report__actions">
        <button
          class="btn btn--secondary btn--sm"
          :disabled="isRegeneratingReport"
          @click="$emit('regenerate')"
          aria-label="重新生成报告"
        >
          {{ isRegeneratingReport ? "生成中..." : "重新生成" }}
        </button>
        <button class="btn btn--secondary btn--sm" @click="$emit('download')" aria-label="下载报告">
          下载
        </button>
      </div>
    </div>
    <div class="report__content" v-html="sanitizedContent" aria-live="polite"></div>
  </section>

  <div v-else-if="loading" class="report-loading" role="status" aria-live="polite">
    <div class="spinner"></div>
    <p>正在生成研究报告...</p>
    <span>完成所有任务后将自动生成</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  reportMarkdown: string;
  loading: boolean;
  isRegeneratingReport: boolean;
  sanitizedContent: string;
}>();

defineEmits<{
  (e: "regenerate"): void;
  (e: "download"): void;
}>();
</script>

<style scoped>
.report { background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; }
.report__header { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--color-divider); }
.report__actions { display: flex; gap: 8px; }
.report__title { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: var(--color-text-primary); }
.report__title svg { width: 18px; height: 18px; color: var(--color-accent); }
.report__content { padding: 20px; font-size: 12px; line-height: 1.8; color: var(--color-text-primary); max-height: 500px; overflow-y: auto; }
.report__content :deep(h2) { font-size: 18px; font-weight: 600; color: var(--color-text-primary); margin: 24px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--color-divider); }
.report__content :deep(h3) { font-size: 15px; font-weight: 600; color: var(--color-text-primary); margin: 20px 0 8px; }
.report__content :deep(p) { margin-bottom: 12px; }
.report__content :deep(strong) { color: var(--color-accent); }

.report-loading { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-lg); padding: 48px; }
.spinner { width: 40px; height: 40px; border: 3px solid var(--color-bg-tertiary); border-top-color: var(--color-accent); border-radius: 50%; animation: spin 0.8s linear infinite; margin-bottom: 16px; }
@keyframes spin { to { transform: rotate(360deg); } }
.report-loading p { font-size: 16px; color: var(--color-text-primary); margin-bottom: 4px; }
.report-loading span { font-size: 12px; color: var(--color-text-muted); }

.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 16px; border-radius: var(--radius-md); font-size: 12px; font-weight: 500; border: none; transition: all 0.2s ease; cursor: pointer; }
.btn--secondary { background: var(--color-bg-tertiary); color: var(--color-text-secondary); border: 1px solid var(--color-border); }
.btn--secondary:hover { background: var(--color-bg-secondary); border-color: var(--color-border-hover); }
.btn--sm { padding: 6px 12px; font-size: 12px; }
</style>
