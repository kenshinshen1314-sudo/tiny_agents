<template>
  <header class="header" role="banner">
    <div class="header__left">
      <button
        class="btn btn--icon"
        @click="$emit('reset')"
        :title="'返回'"
        aria-label="返回首页"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
        </svg>
      </button>
      <h1 class="header__title">{{ topic }}</h1>
      <span class="header__status" :class="statusClass" role="status">
        {{ statusText }}
      </span>
    </div>
    <div class="header__right">
      <div class="progress" role="progressbar" :aria-valuenow="progressPercent" aria-valuemin="0" aria-valuemax="100">
        <div class="progress__bar">
          <div class="progress__fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
        <span class="progress__text">{{ completedTasks }}/{{ totalTasks }}</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  topic: string;
  statusText: string;
  statusClass: string;
  progressPercent: number;
  completedTasks: number;
  totalTasks: number;
}>();

defineEmits<{
  (e: "reset"): void;
}>();
</script>

<style scoped>
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

.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 16px; border-radius: var(--radius-md); font-size: 12px; font-weight: 500; border: none; transition: all 0.2s ease; cursor: pointer; }
.btn--icon { width: 36px; height: 36px; padding: 0; background: transparent; border: 1px solid var(--color-border); }
.btn--icon svg { width: 18px; height: 18px; }
.btn--icon:hover { background: var(--color-bg-tertiary); }
</style>
