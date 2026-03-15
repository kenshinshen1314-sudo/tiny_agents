<template>
  <div id="app">
    <a-layout style="min-height: 100vh">
      <a-layout-header class="app-header">
        <div class="header-content">
          <div class="logo">
            <span class="logo-icon">✈️</span>
            <span class="logo-text">探索下一站</span>
          </div>
          <div class="header-actions">
            <div class="header-tag">
              <span class="tag-dot"></span>
              <span class="tag-text">AI-Powered</span>
            </div>
          </div>
        </div>
      </a-layout-header>
      <a-layout-content class="app-content">
        <router-view />
      </a-layout-content>
      <a-layout-footer class="app-footer">
        <p>🌍 由 TinyAgents 驱动 · 让每一次旅行都难忘</p>
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
/* ========== 全局样式 ========== */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* ========== Header ========== */
.app-header {
  background: white !important;
  border-bottom: 1px solid #F0F0F0;
  padding: 0 !important;
  height: 64px !important;
  line-height: 64px !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* ========== Header Tag ========== */
.header-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
  border-radius: 20px;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.tag-dot {
  width: 6px;
  height: 6px;
  background: white;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* ========== Content ========== */
.app-content {
  background: transparent !important;
  padding: 0 !important;
}

/* ========== Footer ========== */
.app-footer {
  background: white !important;
  border-top: 1px solid #F0F0F0;
  text-align: center;
  padding: 20px 0 !important;
}

.app-footer p {
  color: #4A4A68;
  font-size: 14px;
  margin: 0;
}

/* ========== 全局滚动条 ========== */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #F5F5F5;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #FF8E53 0%, #FF6B6B 100%);
}
</style>
