<template>
  <div class="hero">
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
            <select v-model="form.search_api" class="select" aria-label="选择搜索引擎">
              <option value="">搜索引擎</option>
              <option v-for="opt in searchOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
            <button
              class="btn btn--primary"
              @click="handleSubmit"
              :disabled="loading || !form.topic.trim()"
              aria-label="开始研究"
            >
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
        <button class="example" @click="form.topic = '深度研究openclaw引发的宿主机安全问题'">openclaw安全</button>
        <button class="example" @click="form.topic = '深度研究2026年类openclaw的ai工具大量兴起对opc(一人公司)的助力作用'">openclaw opc</button>
        <button class="example" @click="form.topic = '深度探索ai智能时代内容创作者的审美和品味对作品传播的正向效用'">审美和品味</button>

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
</template>

<script setup lang="ts">
defineProps<{
  form: { topic: string; search_api: string };
  loading: boolean;
}>();

const emit = defineEmits<{
  (e: "submit"): void;
}>();

const searchOptions = ["tavily", "serpapi", "searxng"];

function handleSubmit() {
  emit("submit");
}
</script>

<style scoped>
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
.input-actions { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-top: 1px solid var(--color-divider); }
.select { padding: 6px 10px; background: transparent; border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: 12px; color: var(--color-text-secondary); cursor: pointer; transition: all 0.2s ease; }
.select:hover { border-color: var(--color-border-hover); background: var(--color-bg-secondary); }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--radius-lg);
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  letter-spacing: 0.3px;
}

.btn--primary {
  background: linear-gradient(135deg, var(--color-accent) 0%, #E8850C 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(217, 119, 6, 0.25), 0 1px 2px rgba(0, 0, 0, 0.1);
  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

.btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, var(--color-accent-hover) 0%, #D97706 100%);
  box-shadow: 0 4px 12px rgba(217, 119, 6, 0.35), 0 2px 4px rgba(0, 0, 0, 0.15);
  transform: translateY(-1px);
}

.btn--primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 1px 4px rgba(217, 119, 6, 0.2), 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn--primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading { display: flex; align-items: center; gap: 4px; }
.loading__dot { width: 6px; height: 6px; background: white; border-radius: 50%; animation: loadingBounce 1.4s ease-in-out infinite; }
.loading__dot:nth-child(1) { animation-delay: 0s; }
.loading__dot:nth-child(2) { animation-delay: 0.2s; }
.loading__dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes loadingBounce { 0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }

.examples { display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap; }
.examples__label { font-size: 12px; color: var(--color-text-muted); }
.example { padding: 6px 14px; background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-radius: var(--radius-full); font-size: 12px; color: var(--color-text-secondary); transition: all 0.2s ease; cursor: pointer; }
.example:hover { background: var(--color-bg-secondary); border-color: var(--color-accent); color: var(--color-accent); }

.hero__footer { display: flex; justify-content: center; gap: 32px; margin-top: 48px; padding-top: 32px; border-top: 1px solid var(--color-divider); }
.feature { display: flex; align-items: center; gap: 8px; font-size: 12px; color: var(--color-text-muted); }
.feature svg { width: 16px; height: 16px; }

@media (max-width: 768px) {
  .hero__title { font-size: 28px; }
  .hero__footer { flex-direction: column; gap: 16px; }
}
</style>
