<template>
  <div class="home-container">
    <!-- 背景装饰 -->
    <div class="bg-decoration">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
      <div class="grid-overlay"></div>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <div class="badge">✨ AI-Powered</div>
      <h1 class="page-title">探索下一站</h1>
      <p class="page-subtitle">智能规划你的完美旅程</p>
    </div>

    <a-card class="form-card" :bordered="false">
      <a-form
        :model="formData"
        layout="vertical"
        @finish="handleSubmit"
      >
        <!-- 目的地和日期 -->
        <div class="form-section">
          <div class="section-header">
            <div class="section-number">01</div>
            <h3 class="section-title">基本信息</h3>
          </div>

          <a-row :gutter="24">
            <a-col :span="8">
              <a-form-item name="city" :rules="[{ required: true, message: '请输入目的地城市' }]">
                <template #label>
                  <span class="form-label">目的地</span>
                </template>
                <a-auto-complete
                  v-model:value="formData.city"
                  :options="cityOptions"
                  placeholder="搜索或输入城市..."
                  size="large"
                  class="custom-input"
                  filter-option
                >
                  <template #prefix>
                    <span class="input-icon">📍</span>
                  </template>
                  <template #option="{ label, value }">
                    <span class="city-option">
                      <span class="city-hot" v-if="hotCities.includes(value)">🔥</span>
                      <span class="city-label">{{ label }}</span>
                      <span class="city-value" v-if="value !== label">{{ value }}</span>
                    </span>
                  </template>
                </a-auto-complete>
              </a-form-item>
            </a-col>
            <a-col :span="6">
              <a-form-item name="start_date" :rules="[{ required: true, message: '请选择开始日期' }]">
                <template #label>
                  <span class="form-label">出发日期</span>
                </template>
                <a-date-picker
                  v-model:value="formData.start_date"
                  style="width: 100%"
                  size="large"
                  class="custom-input"
                  placeholder="选择日期"
                />
              </a-form-item>
            </a-col>
            <a-col :span="6">
              <a-form-item name="end_date" :rules="[{ required: true, message: '请选择结束日期' }]">
                <template #label>
                  <span class="form-label">返程日期</span>
                </template>
                <a-date-picker
                  v-model:value="formData.end_date"
                  style="width: 100%"
                  size="large"
                  class="custom-input"
                  placeholder="选择日期"
                />
              </a-form-item>
            </a-col>
            <a-col :span="4">
              <a-form-item>
                <template #label>
                  <span class="form-label">行程天数</span>
                </template>
                <div class="days-badge">
                  <span class="days-value">{{ formData.travel_days }}</span>
                  <span class="days-unit">天</span>
                </div>
              </a-form-item>
            </a-col>
          </a-row>
        </div>

        <!-- 偏好设置 -->
        <div class="preference-section">
          <div class="section-header">
            <div class="section-number">02</div>
            <h3 class="section-title">旅行偏好</h3>
          </div>

          <!-- 偏好卡片容器 -->
          <div class="preference-cards">
            <!-- 基础偏好卡片 -->
            <div class="preference-card">
              <div class="card-header">
                <span class="card-icon">🚄</span>
                <span class="card-title">出行方式</span>
              </div>
              <a-select v-model:value="formData.transportation" class="pref-select">
                <a-select-option value="公共交通">🚇 公共交通</a-select-option>
                <a-select-option value="自驾">🚗 自驾</a-select-option>
                <a-select-option value="步行">🚶 步行</a-select-option>
                <a-select-option value="混合">🔀 混合</a-select-option>
              </a-select>
            </div>

            <div class="preference-card">
              <div class="card-header">
                <span class="card-icon">🏨</span>
                <span class="card-title">住宿类型</span>
              </div>
              <a-select v-model:value="formData.accommodation" class="pref-select">
                <a-select-option value="经济型酒店">💰 经济型酒店</a-select-option>
                <a-select-option value="舒适型酒店">🏨 舒适型酒店</a-select-option>
                <a-select-option value="豪华酒店">⭐ 豪华酒店</a-select-option>
                <a-select-option value="民宿">🏡 民宿</a-select-option>
              </a-select>
            </div>

            <!-- 兴趣标签卡片 -->
            <div class="preference-card interest-card">
              <div class="card-header">
                <span class="card-icon">🎯</span>
                <span class="card-title">兴趣标签</span>
                <span class="card-hint">可多选</span>
              </div>
              <div class="tag-container">
                <div 
                  v-for="interest in interestOptions" 
                  :key="interest.value"
                  class="interest-tag"
                  :class="{ active: formData.preferences.includes(interest.value) }"
                  @click="togglePreference('preferences', interest.value)"
                >
                  <span class="tag-emoji">{{ interest.icon }}</span>
                  <span class="tag-label">{{ interest.label }}</span>
                </div>
              </div>
            </div>

            <!-- 饮食偏好卡片 -->
            <div class="preference-card food-card">
              <div class="card-header">
                <span class="card-icon">🍽️</span>
                <span class="card-title">口味偏好</span>
                <span class="card-hint">可多选</span>
              </div>
              <div class="tag-container">
                <div 
                  v-for="food in foodOptions" 
                  :key="food.value"
                  class="interest-tag flavor-tag"
                  :class="{ active: formData.food_preferences.includes(food.value) }"
                  @click="togglePreference('food_preferences', food.value)"
                >
                  <span class="tag-emoji">{{ food.icon }}</span>
                  <span class="tag-label">{{ food.label }}</span>
                </div>
              </div>
            </div>

            <!-- 就餐环境卡片 -->
            <div class="preference-card env-card">
              <div class="card-header">
                <span class="card-icon">🏪</span>
                <span class="card-title">就餐环境</span>
                <span class="card-hint">可多选</span>
              </div>
              <div class="tag-container">
                <div 
                  v-for="env in envOptions" 
                  :key="env.value"
                  class="interest-tag"
                  :class="{ active: formData.environment_preferences.includes(env.value) }"
                  @click="togglePreference('environment_preferences', env.value)"
                >
                  <span class="tag-emoji">{{ env.icon }}</span>
                  <span class="tag-label">{{ env.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 额外要求 -->
        <div class="form-section">
          <div class="section-header">
            <div class="section-number">03</div>
            <h3 class="section-title">特殊需求</h3>
          </div>

          <a-form-item name="free_text_input">
            <a-textarea
              v-model:value="formData.free_text_input"
              placeholder="告诉我们你的特殊需求，比如：想看日出、需要无障碍设施、饮食偏好等..."
              :rows="3"
              size="large"
              class="custom-textarea"
            />
          </a-form-item>
        </div>

        <!-- 提交按钮 -->
        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            :loading="loading"
            size="large"
            block
            class="submit-button"
          >
            <template v-if="!loading">
              <span class="button-icon">✈️</span>
              <span>生成专属旅行计划</span>
            </template>
            <template v-else>
              <span>正在规划中...</span>
            </template>
          </a-button>
        </a-form-item>

        <!-- 加载进度 - 实时规划进度卡片 -->
        <a-form-item v-if="loading">
          <div class="progress-card">
            <!-- 卡片头部 -->
            <div class="progress-header">
              <div class="progress-title">
                <RobotOutlined />
                <span>AI 正在规划您的旅行</span>
              </div>
              <div class="progress-dest">{{ formData.city }} · {{ formData.travel_days }}天</div>
            </div>

            <!-- 步骤进度条 -->
            <div class="step-progress">
              <div
                v-for="(step, index) in progressSteps"
                :key="index"
                class="step-item"
                :class="{ active: currentStep === index, completed: currentStep > index, pending: currentStep < index }"
              >
                <div class="step-icon">
                  <span v-if="currentStep > index">✓</span>
                  <LoadingOutlined v-else-if="currentStep === index" spin />
                  <span v-else>{{ index + 1 }}</span>
                </div>
                <div class="step-content">
                  <div class="step-title">{{ step.title }}</div>
                  <div class="step-desc">{{ step.description }}</div>
                </div>
              </div>
            </div>

            <!-- 当前状态 -->
            <div class="current-status">
              <div class="status-icon">{{ currentStepInfo.icon }}</div>
              <div class="status-text">{{ loadingStatus || currentStepInfo.text }}</div>
            </div>

            <!-- 总体进度 -->
            <a-progress
              :percent="loadingProgress"
              status="active"
              :stroke-color="{
                '0%': '#FF6B6B',
                '100%': '#FF8E53',
              }"
              :stroke-width="12"
              class="main-progress"
              :show-info="false"
            />
          </div>
        </a-form-item>
      </a-form>
    </a-card>

    <!-- 底部提示 -->
    <div class="footer-tip">
      <p>🌟 由 HelloAgents AI 驱动，为你打造独一无二的旅行体验</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { LoadingOutlined, RobotOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { generateTripPlan, generateTripPlanStream } from '@/services/api'
import type { TripFormData } from '@/types'
import type { Dayjs } from 'dayjs'

const router = useRouter()
const loading = ref(false)
const loadingProgress = ref(0)
const loadingStatus = ref('')
const currentStep = ref(0)

// 步骤进度配置
const progressSteps = [
  { title: '🔍 搜索景点', description: '正在搜索景点...' },
  { title: '🍜 搜索美食', description: '正在搜索美食地点...' },
  { title: '🌤️ 查询天气', description: '正在查询天气...' },
  { title: '🏨 推荐酒店', description: '正在搜索酒店...' },
  { title: '📋 生成行程', description: '正在生成旅行计划...' },
  { title: '🚗 计算路线', description: '正在计算交通路线...' },
]

// 当前步骤的详细信息
const currentStepInfo = computed(() => {
  if (currentStep.value < 0) {
    return { icon: '🔄', text: '正在连接服务器...' }
  }
  if (currentStep.value >= progressSteps.length) {
    return { icon: '✅', text: '完成!' }
  }
  const step = progressSteps[currentStep.value]
  return {
    icon: step.title.split(' ')[0],
    text: step.description
  }
})

// 热门城市列表
const hotCities = [
  '北京', '上海', '广州', '深圳', '杭州', '成都', '重庆', '西安', '南京', '苏州',
  '武汉', '长沙', '厦门', '青岛', '大连', '三亚', '桂林', '丽江', '拉萨', '乌鲁木齐'
]

// 城市选项
const cityOptions = hotCities.map(city => ({
  label: city,
  value: city
}))

// 兴趣标签选项
const interestOptions = [
  { value: '历史文化', label: '历史文化', icon: '🏛️' },
  { value: '自然风光', label: '自然风光', icon: '🏞️' },
  { value: '美食', label: '美食', icon: '🍜' },
  { value: '购物', label: '购物', icon: '🛍️' },
  { value: '艺术', label: '艺术', icon: '🎨' },
  { value: '休闲', label: '休闲', icon: '☕' },
  { value: '户外探险', label: '户外探险', icon: '🏔️' },
  { value: '摄影', label: '摄影', icon: '📸' },
  { value: '主题乐园', label: '主题乐园', icon: '🎢' },
  { value: '博物馆', label: '博物馆', icon: '🏛️' },
  { value: '夜生活', label: '夜生活', icon: '🌙' },
  { value: '运动健身', label: '运动健身', icon: '🏃' },
]

// 饮食偏好选项
const foodOptions = [
  { value: '清淡', label: '清淡', icon: '🥬' },
  { value: '微辣', label: '微辣', icon: '🌶️' },
  { value: '中辣', label: '中辣', icon: '🌶️' },
  { value: '特辣', label: '特辣', icon: '🔥' },
  { value: '麻辣', label: '麻辣', icon: '🌶️' },
  { value: '偏甜', label: '偏甜', icon: '🍬' },
  { value: '偏咸', label: '偏咸', icon: '🧂' },
  { value: '浓油赤酱', label: '浓油赤酱', icon: '🥘' },
]

// 就餐环境选项
const envOptions = [
  { value: '路边摊', label: '路边摊', icon: '🚏' },
  { value: '苍蝇馆', label: '苍蝇馆', icon: '🏪' },
  { value: '网红餐馆', label: '网红餐馆', icon: '📸' },
  { value: '星级酒店', label: '星级酒店', icon: '⭐' },
  { value: '商场', label: '商场', icon: '🏬' },
  { value: '小吃街', label: '小吃街', icon: '🍡' },
]

// 切换偏好选项
const togglePreference = (type: string, value: string) => {
  const arr = formData[type as keyof typeof formData] as string[]
  const index = arr.indexOf(value)
  if (index > -1) {
    arr.splice(index, 1)
  } else {
    arr.push(value)
  }
}

const formData = reactive<TripFormData & { start_date: Dayjs | null; end_date: Dayjs | null }>({
  city: '',
  start_date: null,
  end_date: null,
  travel_days: 1,
  transportation: '公共交通',
  accommodation: '经济型酒店',
  preferences: [],
  food_preferences: [],
  environment_preferences: [],
  free_text_input: ''
})

// 监听日期变化,自动计算旅行天数
watch([() => formData.start_date, () => formData.end_date], ([start, end]) => {
  if (start && end) {
    const days = end.diff(start, 'day') + 1
    if (days > 0 && days <= 30) {
      formData.travel_days = days
    } else if (days > 30) {
      message.warning('旅行天数不能超过30天')
      formData.end_date = null
    } else {
      message.warning('结束日期不能早于开始日期')
      formData.end_date = null
    }
  }
})

const handleSubmit = async () => {
  if (!formData.start_date || !formData.end_date) {
    message.error('请选择日期')
    return
  }

  loading.value = true
  loadingProgress.value = 0
  loadingStatus.value = '正在连接服务器...'
  currentStep.value = -1  // -1 表示等待连接

  try {
    const requestData: TripFormData = {
      city: formData.city,
      start_date: formData.start_date.format('YYYY-MM-DD'),
      end_date: formData.end_date.format('YYYY-MM-DD'),
      travel_days: formData.travel_days,
      transportation: formData.transportation,
      accommodation: formData.accommodation,
      preferences: formData.preferences,
      food_preferences: formData.food_preferences,
      environment_preferences: formData.environment_preferences,
      free_text_input: formData.free_text_input
    }

    // 使用SSE流式接口获取真实进度
    const response = await generateTripPlanStream(requestData, (progress) => {
      // 只在收到有效进度时更新（step >= 1）
      if (progress.step && progress.step >= 1) {
        loadingProgress.value = progress.progress || 0
        currentStep.value = (progress.step || 1) - 1
        loadingStatus.value = progress.message || ''
        console.log('📊 进度更新:', progress)
      }
    })

    console.log('📦 API 响应:', response)
    console.log('✅ 响应是否成功:', response.success)
    console.log('📊 响应数据:', response.data)

    if (response.success && response.data) {
      // 保存到sessionStorage
      const tripPlanJson = JSON.stringify(response.data)
      console.log('💾 准备保存到 sessionStorage，数据长度:', tripPlanJson.length)
      sessionStorage.setItem('tripPlan', tripPlanJson)

      // 验证是否保存成功
      const savedData = sessionStorage.getItem('tripPlan')
      console.log('🔍 从 sessionStorage 读取验证:', savedData ? '成功' : '失败')

      message.success('旅行计划生成成功!')

      // 短暂延迟后跳转
      setTimeout(() => {
        console.log('🚀 准备跳转到 /result')
        router.push('/result')
      }, 500)
    } else {
      message.error(response.message || '生成失败')
    }
  } catch (error: any) {
    console.error('生成旅行计划失败:', error)
    message.error(error.message || '生成旅行计划失败,请稍后重试')
  } finally {
    currentStep.value = 5
    loadingProgress.value = 100
    loadingStatus.value = '✅ 完成!'
    setTimeout(() => {
      loading.value = false
      loadingProgress.value = 0
      loadingStatus.value = ''
      currentStep.value = 0
    }, 1500)
  }
}
</script>

<style scoped>
/* ========== 全局变量 ========== */
:deep(:root) {
  --color-primary: #FF6B6B;
  --color-secondary: #FF8E53;
  --color-accent: #00B4D8;
  --color-bg-light: #FFF8F3;
  --color-text-dark: #1A1A2E;
  --color-text-gray: #4A4A68;
  --border-color: #E8E4EF;
  --shadow-soft: 0 8px 32px rgba(255, 107, 107, 0.12);
  --shadow-hover: 0 12px 48px rgba(255, 107, 107, 0.2);
}

/* ========== 容器 ========== */
.home-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #FFF8F3 0%, #FFF0E6 50%, #E8F4F8 100%);
  padding: 40px 20px 80px;
  position: relative;
  overflow: hidden;
}

/* ========== 背景装饰 ========== */
.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  overflow: hidden;
  z-index: 0;
}

.grid-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image:
    linear-gradient(rgba(255, 107, 107, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 107, 107, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
}

.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.6;
  animation: float 25s ease-in-out infinite;
}

.shape-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.shape-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
  bottom: 10%;
  left: -80px;
  animation-delay: 8s;
}

.shape-3 {
  width: 200px;
  height: 200px;
  background: linear-gradient(135deg, #FFB347 0%, #FFCC33 100%);
  top: 50%;
  right: 15%;
  animation-delay: 16s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(30px, -30px) scale(1.05);
  }
  50% {
    transform: translate(-20px, 20px) scale(0.95);
  }
  75% {
    transform: translate(20px, 30px) scale(1.02);
  }
}

/* ========== 页面标题 ========== */
.page-header {
  text-align: center;
  margin-bottom: 40px;
  position: relative;
  z-index: 1;
  animation: fadeInDown 0.8s ease-out;
}

.badge {
  display: inline-block;
  padding: 6px 16px;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
  font-size: 13px;
  font-weight: 600;
  border-radius: 20px;
  margin-bottom: 20px;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.page-title {
  font-size: 52px;
  font-weight: 800;
  color: #1A1A2E;
  margin-bottom: 12px;
  letter-spacing: -1px;
  line-height: 1.1;
}

.page-subtitle {
  font-size: 18px;
  color: #4A4A68;
  margin: 0;
  font-weight: 400;
}

/* ========== 表单卡片 ========== */
.form-card {
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08);
  animation: fadeInUp 0.8s ease-out 0.1s backwards;
  position: relative;
  z-index: 1;
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
}

.form-card :deep(.ant-card-body) {
  padding: 40px;
}

/* ========== 偏好设置区域 ========== */
.preference-section {
  margin-bottom: 28px;
}

.preference-section .section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #F5F5F5;
}

.preference-section .section-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
  font-size: 16px;
  font-weight: 700;
  border-radius: 10px;
}

.preference-section .section-title {
  font-size: 17px;
  font-weight: 700;
  color: #1A1A2E;
  margin: 0;
}

/* ========== 偏好卡片容器 ========== */
.preference-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

@media (max-width: 992px) {
  .preference-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 576px) {
  .preference-cards {
    grid-template-columns: 1fr;
  }
}

/* ========== 偏好卡片 ========== */
.preference-card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px;
  border: 1px solid #E8E4EF;
  transition: all 0.3s ease;
}

.preference-card:hover {
  border-color: #FFD4CC;
  box-shadow: 0 8px 24px rgba(255, 107, 107, 0.12);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.card-icon {
  font-size: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #1A1A2E;
}

.card-hint {
  margin-left: auto;
  font-size: 12px;
  color: #999;
  background: #F5F5F5;
  padding: 2px 8px;
  border-radius: 10px;
}

/* ========== 下拉选择器样式 ========== */
.pref-select {
  width: 100%;
}

.pref-select :deep(.ant-select-selector) {
  height: 48px !important;
  border-radius: 12px !important;
  border: 2px solid #E8E4EF !important;
  padding: 6px 16px !important;
  font-size: 15px;
}

.pref-select :deep(.ant-select-selection-item) {
  line-height: 34px !important;
}

.pref-select :deep(.ant-select-selector:hover) {
  border-color: #FFD4CC !important;
}

.pref-select :deep(.ant-select-focused .ant-select-selector) {
  border-color: #FF6B6B !important;
  box-shadow: 0 0 0 3px rgba(255, 107, 107, 0.1) !important;
}

/* ========== 兴趣标签容器 ========== */
.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* ========== 兴趣标签 ========== */
.interest-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: #F8F8F8;
  border: 1px solid #E8E4EF;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.25s ease;
  user-select: none;
}

.interest-tag:hover {
  background: #FFF0E6;
  border-color: #FFD4CC;
  transform: translateY(-1px);
}

.interest-tag.active {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}

.interest-tag.active .tag-emoji {
  transform: scale(1.1);
}

.tag-emoji {
  font-size: 16px;
  transition: transform 0.2s ease;
}

.tag-label {
  font-size: 13px;
  font-weight: 500;
}

/* 口味偏好标签 - 特殊颜色 */
.food-card .interest-tag.active {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
  box-shadow: 0 4px 12px rgba(82, 196, 26, 0.3);
}

/* 就餐环境标签 */
.env-card .interest-tag.active {
  background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

/* ========== 旧样式隐藏 ========== */
.form-section {
  margin-bottom: 28px;
  padding: 24px;
  background: #FAFAFA;
  border-radius: 16px;
  border: 1px solid #F0F0F0;
  transition: all 0.3s ease;
}

.form-section:hover {
  background: #FFFFFF;
  border-color: #FFE5DC;
  box-shadow: 0 4px 20px rgba(255, 107, 107, 0.08);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #F5F5F5;
}

.section-number {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
  font-size: 16px;
  font-weight: 700;
  border-radius: 10px;
}

.section-title {
  font-size: 17px;
  font-weight: 700;
  color: #1A1A2E;
  margin: 0;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #4A4A68;
  margin-bottom: 8px;
}

/* ========== 输入框 ========== */
.custom-input :deep(.ant-input),
.custom-input :deep(.ant-picker) {
  border-radius: 10px;
  border: 2px solid #E8E4EF;
  transition: all 0.25s ease;
  font-size: 15px;
}

.custom-input :deep(.ant-input:hover),
.custom-input :deep(.ant-picker:hover) {
  border-color: #FFD4CC;
}

.custom-input :deep(.ant-input:focus),
.custom-input :deep(.ant-picker-focused) {
  border-color: #FF6B6B;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1);
}

.input-icon {
  font-size: 16px;
}

/* ========== 选择框 ========== */
.custom-select :deep(.ant-select-selector) {
  border-radius: 10px !important;
  border: 2px solid #E8E4EF !important;
  font-size: 15px;
  transition: all 0.25s ease;
}

.custom-select:hover :deep(.ant-select-selector) {
  border-color: #FFD4CC !important;
}

.custom-select :deep(.ant-select-focused .ant-select-selector) {
  border-color: #FF6B6B !important;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1) !important;
}

.option-icon,
.tag-icon {
  margin-right: 6px;
}

/* ========== 天数徽章 ========== */
.days-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  padding: 0 20px;
  background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
  border-radius: 10px;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 180, 216, 0.3);
}

.days-badge .days-value {
  font-size: 22px;
  font-weight: 700;
  margin-right: 4px;
}

.days-badge .days-unit {
  font-size: 13px;
  font-weight: 500;
}

/* ========== 偏好标签 ========== */
.preference-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.custom-checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  width: 100%;
}

.preference-tag :deep(.ant-checkbox-wrapper) {
  margin: 0 !important;
  padding: 10px 16px;
  border: 2px solid #E8E4EF;
  border-radius: 12px;
  transition: all 0.25s ease;
  background: white;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.preference-tag :deep(.ant-checkbox-wrapper:hover) {
  border-color: #FFD4CC;
  background: #FFF8F3;
  transform: translateY(-1px);
}

.preference-tag :deep(.ant-checkbox-wrapper-checked) {
  border-color: #FF6B6B;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
}

.preference-tag :deep(.ant-checkbox-wrapper-checked) .tag-icon {
  filter: brightness(0) invert(1);
}

/* 自定义复选框样式 */
.preference-tag :deep(.ant-checkbox) {
  display: flex;
  align-self: center;
}

.preference-tag :deep(.ant-checkbox-inner) {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 2px solid #D9D9D9;
  background: white;
  transition: all 0.2s ease;
}

.preference-tag :deep(.ant-checkbox-wrapper:hover .ant-checkbox-inner) {
  border-color: #FF6B6B;
}

.preference-tag :deep(.ant-checkbox-checked .ant-checkbox-inner) {
  background: #FF6B6B;
  border-color: #FF6B6B;
}

.preference-tag :deep(.ant-checkbox-checked .ant-checkbox-inner::after) {
  width: 5px;
  height: 9px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg) scaleY(1);
  left: 5px;
  top: 1px;
}

.tag-icon {
  margin-right: 4px;
  font-size: 16px;
}

/* 隐藏原生复选框input */
.preference-tag :deep(.ant-checkbox-input) {
  display: none;
}

/* ========== 文本域 ========== */
.custom-textarea :deep(.ant-input) {
  border-radius: 10px;
  border: 2px solid #E8E4EF;
  transition: all 0.25s ease;
  font-size: 15px;
}

.custom-textarea :deep(.ant-input:hover) {
  border-color: #FFD4CC;
}

.custom-textarea :deep(.ant-input:focus) {
  border-color: #FF6B6B;
  box-shadow: 0 0 0 4px rgba(255, 107, 107, 0.1);
}

/* ========== 提交按钮 ========== */
.submit-button {
  height: 56px;
  border-radius: 14px;
  font-size: 17px;
  font-weight: 600;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  border: none;
  box-shadow: 0 8px 24px rgba(255, 107, 107, 0.35);
  transition: all 0.3s ease;
  margin-top: 8px;
}

.submit-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(255, 107, 107, 0.45);
  background: linear-gradient(135deg, #FF8E53 0%, #FF6B6B 100%);
}

.submit-button:active {
  transform: translateY(0);
}

.button-icon {
  margin-right: 8px;
  font-size: 18px;
}

/* ========== 进度卡片 ========== */
.progress-card {
  background: linear-gradient(135deg, #FFFFFF 0%, #FFF8F3 100%);
  border-radius: 16px;
  border: 2px solid #FFE5DC;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(255, 107, 107, 0.15);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #FFE5DC;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1A1A2E;
}

.progress-title :deep(.anticon) {
  font-size: 22px;
  color: #FF6B6B;
}

.progress-dest {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.loading-container {
  text-align: center;
  padding: 24px;
  background: linear-gradient(135deg, #FFF8F3 0%, #FFFFFF 100%);
  border-radius: 14px;
  border: 2px dashed #FFD4CC;
}

.loading-status {
  margin-top: 14px;
  color: #FF6B6B;
  font-size: 16px;
  font-weight: 500;
  text-align: center;
}

/* ========== 步骤进度条 ========== */
.step-progress {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: #FAFAFA;
  border-radius: 10px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.step-item.active {
  background: linear-gradient(135deg, #FFF8F3 0%, #FFFFFF 100%);
  border-color: #FF6B6B;
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.15);
}

.step-item.completed {
  background: #F6FFED;
  border-color: #95DE64;
}

.step-item.pending {
  opacity: 0.5;
}

.step-item.completed .step-icon {
  background: #95DE64;
  color: white;
}

.step-icon {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #E8E4EF;
  color: #4A4A68;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.step-item.active .step-icon {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.step-content {
  flex: 1;
}

.step-title {
  font-size: 14px;
  font-weight: 600;
  color: #1A1A2E;
}

.step-item.active .step-title {
  color: #FF6B6B;
}

.step-desc {
  font-size: 12px;
  color: #4A4A68;
  margin-top: 2px;
}

.step-loading {
  color: #FF6B6B;
}

/* ========== 当前状态 ========== */
.current-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 14px;
  background: linear-gradient(135deg, #FFF8F3 0%, #FFFFFF 100%);
  border-radius: 10px;
  margin-bottom: 16px;
  border: 1px solid #FFE5DC;
}

.status-icon {
  font-size: 24px;
}

.status-text {
  font-size: 16px;
  color: #4A4A68;
  font-weight: 500;
}

/* ========== 主进度条 ========== */
.main-progress {
  margin-top: 8px;
}

.main-progress :deep(.ant-progress-inner) {
  background: #FFE5DC;
  border-radius: 6px;
}

.main-progress :deep(.ant-progress-bg) {
  border-radius: 6px;
}

/* ========== 底部提示 ========== */
.footer-tip {
  text-align: center;
  margin-top: 30px;
  position: relative;
  z-index: 1;
}

.footer-tip p {
  color: #4A4A68;
  font-size: 14px;
  margin: 0;
}

/* ========== 动画 ========== */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ========== 响应式 ========== */
@media (max-width: 768px) {
  .page-title {
    font-size: 36px;
  }

  .form-card :deep(.ant-card-body) {
    padding: 24px;
  }
}

/* ========== 城市选择下拉框 ========== */
.city-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
}

.city-hot {
  font-size: 14px;
}

.city-label {
  font-weight: 500;
  color: #1A1A2E;
}

.city-value {
  font-size: 12px;
  color: #4A4A68;
  margin-left: auto;
}

/* 自定义下拉框样式 */
:deep(.ant-select-dropdown) {
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border: 1px solid #F0F0F0;
}

:deep(.ant-select-item-option) {
  border-radius: 8px;
  margin: 4px 8px;
  padding: 8px 12px;
  transition: all 0.2s ease;
}

:deep(.ant-select-item-option:hover) {
  background: #FFF8F3;
}

:deep(.ant-select-item-option-selected) {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
  color: white;
}

:deep(.ant-select-item-option-selected .city-label) {
  color: white;
}

:deep(.ant-select-item-option-selected .city-value) {
  color: rgba(255, 255, 255, 0.8);
}
</style>