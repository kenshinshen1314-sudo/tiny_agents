<template>
  <div class="home">
    <div class="container">
      <h1>多Agent协作系统</h1>
      <p class="subtitle">输入您的需求，AI团队将为您完成</p>

      <el-card class="input-card">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="6"
          placeholder="例如：帮我开发一个用户管理系统，需要用户登录、文章发布、评论功能"
        />

        <div class="actions">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleAnalyze"
          >
            分析需求
          </el-button>
        </div>
      </el-card>

      <!-- 模板选择 -->
      <el-card v-if="showTemplateSelect" class="template-card">
        <template #header>
          <span>选择团队模板</span>
        </template>

        <div class="analysis-result">
          <el-tag>任务类型: {{ analysisResult?.task_type }}</el-tag>
          <el-tag type="warning">复杂度: {{ analysisResult?.complexity }}</el-tag>
        </div>

        <el-radio-group v-model="selectedTemplate">
          <el-radio
            v-for="template in templates"
            :key="template.id"
            :value="template.id"
            border
          >
            <div class="template-option">
              <div class="template-name">{{ template.name }}</div>
              <div class="template-desc">{{ template.description }}</div>
              <div class="template-roles">
                角色: {{ template.roles.join(', ') }}
              </div>
            </div>
          </el-radio>
        </el-radio-group>

        <div class="actions">
          <el-button @click="showTemplateSelect = false">上一步</el-button>
          <el-button type="primary" @click="handleCreateTask">确认并执行</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useTaskStore } from '@/stores/task';
import { templateApi } from '@/api/templates';
import type { TeamTemplate, AnalyzeResult } from '@/types';
import { ElMessage } from 'element-plus';

const router = useRouter();
const taskStore = useTaskStore();

const userInput = ref('');
const loading = ref(false);
const showTemplateSelect = ref(false);
const analysisResult = ref<AnalyzeResult | null>(null);
const selectedTemplate = ref('');
const templates = ref<TeamTemplate[]>([]);

async function handleAnalyze() {
  if (!userInput.value.trim()) {
    ElMessage.warning('请输入需求描述');
    return;
  }

  loading.value = true;
  try {
    const [templatesRes, analyzeRes] = await Promise.all([
      templateApi.list(),
      templateApi.analyze(userInput.value)
    ]);

    templates.value = templatesRes.data;
    analysisResult.value = analyzeRes.data;
    selectedTemplate.value = analyzeRes.data.recommended_template;
    showTemplateSelect.value = true;
  } catch (e) {
    ElMessage.error('分析失败，请重试');
  } finally {
    loading.value = false;
  }
}

async function handleCreateTask() {
  if (!selectedTemplate.value) {
    ElMessage.warning('请选择团队模板');
    return;
  }

  loading.value = true;
  try {
    const task = await taskStore.createTask(userInput.value);
    ElMessage.success('任务创建成功');
    router.push(`/task/${task.id}`);
  } catch (e) {
    ElMessage.error('创建失败');
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  padding: 40px 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: #303133;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: #909399;
  margin-bottom: 32px;
}

.input-card,
.template-card {
  margin-top: 24px;
}

.actions {
  margin-top: 20px;
  text-align: center;
}

.analysis-result {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.template-option {
  padding: 8px 0;
}

.template-name {
  font-weight: bold;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: #909399;
}

.template-roles {
  font-size: 12px;
  color: #67c23a;
  margin-top: 4px;
}

.el-radio-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>