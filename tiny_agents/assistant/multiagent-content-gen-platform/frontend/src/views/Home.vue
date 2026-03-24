<template>
  <div class="app">
    <!-- 初始状态 -->
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

        <h2 class="hero__title">{{ mode === 'research' ? '探索任何主题的深度洞察' : '自媒体内容创作助手' }}</h2>
        <p class="hero__subtitle">{{ mode === 'research' ? '基于多轮智能检索与深度分析，实时生成专业研究报告' : '输入素材，生成可直接发布的公众号/小红书/抖音内容' }}</p>

        <!-- 模式切换 Tabs -->
        <div class="tabs">
          <button
            class="tab"
            :class="{ 'tab--active': mode === 'research' }"
            @click="mode = 'research'"
          >
            深度研究
          </button>
          <button
            class="tab"
            :class="{ 'tab--active': mode === 'content' }"
            @click="mode = 'content'"
          >
            内容创作
          </button>
        </div>

        <!-- 输入框 -->
        <div class="input-area">
          <div class="input-card">
            <textarea
              v-model="form.topic"
              :placeholder="mode === 'research' ? '输入你想要深入研究的主题...' : '输入素材/主题/想分享的内容...'"
              rows="3"
              class="input"
              @keydown.enter.meta="handleSubmit"
              @keydown.enter.ctrl="handleSubmit"
            ></textarea>

            <!-- 内容创作模式额外选项 -->
            <div v-if="mode === 'content'" class="content-options">
              <div class="option-group">
                <label class="option-label">目标平台</label>
                <div class="option-buttons">
                  <button
                    v-for="p in platformOptions"
                    :key="p.value"
                    class="option-btn"
                    :class="{ 'option-btn--active': form.platform === p.value }"
                    @click="form.platform = p.value"
                  >
                    {{ p.label }}
                  </button>
                </div>
              </div>
              <div class="option-group">
                <label class="option-label">内容风格</label>
                <div class="option-buttons">
                  <button
                    v-for="s in styleOptions"
                    :key="s.value"
                    class="option-btn"
                    :class="{ 'option-btn--active': form.style === s.value }"
                    @click="form.style = s.value"
                  >
                    {{ s.label }}
                  </button>
                </div>
              </div>
            </div>

            <div class="input-actions">
              <div class="input-actions__left">
                <select v-if="mode === 'research'" v-model="form.search_api" class="select">
                  <option value="">搜索引擎</option>
                  <option v-for="opt in searchOptions" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </div>
              <button class="btn btn--primary" @click="handleSubmit" :disabled="loading || !form.topic.trim()">
                <span v-if="!loading">{{ mode === 'research' ? '开始研究' : '生成内容' }}</span>
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
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { baseURL } from "../services/api";

const router = useRouter();

const form = reactive({
  topic: "",
  search_api: "" as string,
  platform: "wechat" as string,
  style: "rational" as string,
});

const mode = ref<"research" | "content">("research");
const loading = ref(false);

const searchOptions = ["tavily", "serpapi", "duckduckgo", "searxng"];

const platformOptions = [
  { value: "wechat", label: "公众号" },
  { value: "xhs", label: "小红书" },
  { value: "douyin", label: "抖音" },
];

const styleOptions = [
  { value: "rational", label: "理性深度" },
  { value: "emotional", label: "情感共鸣" },
  { value: "humor", label: "轻松幽默" },
  { value: "sharp", label: "犀利观点" },
];

async function handleSubmit() {
  if (!form.topic.trim() || loading.value) return;
  loading.value = true;

  if (mode.value === "content") {
    // 内容创作模式 - 暂时保留在当前页面
    router.push({
      path: '/research',
      query: { mode: 'content', topic: form.topic, platform: form.platform, style: form.style }
    });
  } else {
    // 深度研究模式 - 跳转到研究页面
    router.push({
      path: '/research',
      query: { mode: 'research', topic: form.topic, search_api: form.search_api }
    });
  }
}
</script>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; }

.hero { flex: 1; display: flex; align-items: center; justify-content: center; padding: 48px 24px; }
.hero__content { max-width: 640px; width: 100%; text-align: center; }

.hero__logo { display: flex; align-items: center; justify-content: center; gap: 12px; margin-bottom: 32px; }
.logo-icon { width: 48px; height: 48px; color: var(--color-accent); }
.logo-icon svg { width: 100%; height: 100%; }
.logo-text { display: flex; flex-direction: column; align-items: flex-start; }
.logo-name { font-size: 20px; font-weight: 600; color: var(--color-text-primary); letter-spacing: -0.5px; }
.logo-tagline { font-size: 11px; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: 1px; }

.hero__title { font-family: var(--font-serif); font-size: 42px; font-weight: 500; color: var(--color-text-primary); margin-bottom: 12px; letter-spacing: -1px; }
.hero__subtitle { font-size: 16px; color: var(--color-text-secondary); margin-bottom: 24px; }

.tabs { display: flex; gap: 4px; padding: 4px; background: var(--color-bg-secondary); border-radius: var(--radius-lg); margin-bottom: 24px; }
.tab { flex: 1; padding: 10px 20px; background: transparent; border: none; border-radius: var(--radius-md); font-size: 14px; font-weight: 500; color: var(--color-text-secondary); cursor: pointer; transition: all 0.2s ease; }
.tab:hover { color: var(--color-text-primary); }
.tab--active { background: var(--color-bg-elevated); color: var(--color-text-primary); box-shadow: var(--shadow-sm); }

.input-area { margin-bottom: 24px; }
.input-card { background: var(--color-bg-elevated); border: 1px solid var(--color-border); border-radius: var(--radius-xl); padding: 4px; box-shadow: var(--shadow-lg); }
.input { width: 100%; padding: 16px 20px; background: transparent; border: none; font-size: 15px; color: var(--color-text-primary); resize: none; outline: none; }
.input::placeholder { color: var(--color-text-muted); }
.input-actions { display: flex; align-items: center; justify-content: space-between; padding: 4px 8px; border-top: 1px solid var(--color-divider); }
.input-actions__left { flex: 1; }
.select { padding: 4px 8px; background: transparent; border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: 12px; color: var(--color-text-secondary); cursor: pointer; }
.select:hover { border-color: var(--color-border-hover); }

.content-options { display: flex; flex-direction: column; gap: 12px; padding: 12px 16px; border-top: 1px solid var(--color-divider); }
.option-group { display: flex; align-items: center; gap: 12px; }
.option-label { font-size: 12px; color: var(--color-text-muted); min-width: 60px; }
.option-buttons { display: flex; gap: 6px; flex-wrap: wrap; }
.option-btn { padding: 4px 12px; background: var(--color-bg-tertiary); border: 1px solid var(--color-border); border-radius: var(--radius-md); font-size: 12px; color: var(--color-text-secondary); cursor: pointer; transition: all 0.2s ease; }
.option-btn:hover { border-color: var(--color-border-hover); }
.option-btn--active { background: var(--color-accent); border-color: var(--color-accent); color: white; }

.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 8px 16px; border-radius: var(--radius-md); font-size: 12px; font-weight: 500; border: none; transition: all 0.2s ease; }
.btn--primary { background: var(--color-accent); color: white; }
.btn--primary:hover:not(:disabled) { background: var(--color-accent-hover); }
.btn--primary:disabled { opacity: 0.5; cursor: not-allowed; }

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
</style>