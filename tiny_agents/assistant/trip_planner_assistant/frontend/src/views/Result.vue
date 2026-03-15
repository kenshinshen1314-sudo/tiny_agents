<template>
  <div class="magazine-result-container">
    <!-- 装饰性背景 -->
    <div class="decorative-bg">
      <div class="deco-shape deco-1"></div>
      <div class="deco-shape deco-2"></div>
    </div>

    <!-- 页面头部 -->
    <div class="magazine-header">
      <div class="header-brand">
        <div class="brand-line"></div>
        <span class="brand-text">TRAVEL</span>
        <div class="brand-line"></div>
      </div>
      <a-space size="middle">
        <a-button class="elegant-btn outline-btn" @click="goBack">
          <span>← 返回</span>
        </a-button>
        <a-button v-if="!editMode" @click="toggleEditMode" class="elegant-btn subtle-btn">
          ✎ 编辑
        </a-button>
        <template v-else>
          <a-button @click="saveChanges" type="primary" class="elegant-btn primary-btn">
            ✓ 保存
          </a-button>
          <a-button @click="cancelEdit" class="elegant-btn outline-btn">
            × 取消
          </a-button>
        </template>
        <a-dropdown v-if="!editMode">
          <template #overlay>
            <a-menu>
              <a-menu-item key="image" @click="exportAsImage">📷 导出图片</a-menu-item>
              <a-menu-item key="pdf" @click="exportAsPDF">📄 导出PDF</a-menu-item>
            </a-menu>
          </template>
          <a-button class="elegant-btn subtle-btn">
            📥 导出
          </a-button>
        </a-dropdown>
      </a-space>
    </div>

    <div v-if="tripPlan" class="magazine-content">
      <!-- 侧边导航 -->
      <div class="side-nav">
        <a-affix :offset-top="80">
          <a-menu mode="inline" :selected-keys="[activeSection]" @click="scrollToSection" class="nav-menu">
            <a-menu-item key="overview">📋 概览</a-menu-item>
            <a-menu-item key="budget" v-if="tripPlan.budget">💰 预算</a-menu-item>
            <a-menu-item key="map">📍 地图</a-menu-item>
            <a-menu-item v-for="(day, index) in tripPlan.days" :key="`day-${index}`">
              第{{ day.day_index + 1 }}天
            </a-menu-item>
            <a-menu-item key="weather" v-if="tripPlan.weather_info && tripPlan.weather_info.length">🌤️ 天气</a-menu-item>
          </a-menu>
        </a-affix>
      </div>

      <!-- 主内容区 -->
      <div class="main-content">
        <!-- 英雄区域 -->
        <section class="hero-section">
          <div class="hero-left">
            <div class="hero-meta">
              <span class="meta-tag">{{ tripPlan.city }}</span>
              <span class="meta-divider">/</span>
              <span class="meta-date">{{ tripPlan.start_date }} — {{ tripPlan.end_date }}</span>
            </div>
            <h1 class="hero-title">
              <span class="title-line">{{ tripPlan.city }}</span>
              <span class="title-line title-accent">旅行计划</span>
            </h1>
            <p class="hero-description">{{ tripPlan.overall_suggestions }}</p>
          </div>
          <div class="hero-right">
            <div id="amap-container" class="map-container"></div>
          </div>
        </section>

        <!-- 预算概览 -->
        <section v-if="tripPlan.budget" id="budget" class="budget-section">
          <div class="section-header">
            <span class="section-number">01</span>
            <h2 class="section-title">预算概览</h2>
          </div>
          <div class="budget-grid">
            <div class="budget-item">
              <span class="budget-icon">🎫</span>
              <div>
                <span class="budget-label">景点门票</span>
                <span class="budget-value">¥{{ tripPlan.budget.total_attractions }}</span>
              </div>
            </div>
            <div class="budget-item">
              <span class="budget-icon">🏨</span>
              <div>
                <span class="budget-label">酒店住宿</span>
                <span class="budget-value">¥{{ tripPlan.budget.total_hotels }}</span>
              </div>
            </div>
            <div class="budget-item">
              <span class="budget-icon">🍽️</span>
              <div>
                <span class="budget-label">餐饮费用</span>
                <span class="budget-value">¥{{ tripPlan.budget.total_meals }}</span>
              </div>
            </div>
            <div class="budget-item">
              <span class="budget-icon">🚗</span>
              <div>
                <span class="budget-label">交通费用</span>
                <span class="budget-value">¥{{ tripPlan.budget.total_transportation }}</span>
              </div>
            </div>
          </div>
          <div class="budget-total">
            <span>预估总费用</span>
            <span class="total-amount">¥{{ tripPlan.budget.total }}</span>
          </div>
        </section>

        <!-- 每日行程 -->
        <section class="days-section">
          <div class="section-header">
            <span class="section-number">02</span>
            <h2 class="section-title">每日行程</h2>
          </div>
          <div class="days-timeline">
            <div
              v-for="(day, index) in tripPlan.days"
              :key="index"
              :id="`day-${index}`"
              class="day-block"
            >
              <div class="day-marker">
                <span class="day-number">{{ String(day.day_index + 1).padStart(2, '0') }}</span>
              </div>
              <div class="day-content">
                <!-- 日期和描述 -->
                <div class="day-header">
                  <div class="day-date">
                    <span class="date-day">{{ new Date(day.date).getDate() }}</span>
                    <span class="date-month">{{ new Date(day.date).toLocaleDateString('zh-CN', { month: 'short' }) }}</span>
                  </div>
                  <div class="day-info">
                    <h3 class="day-title">{{ day.description }}</h3>
                    <div class="day-meta">
                      <span class="day-meta-item">🚗 {{ day.transportation }}</span>
                      <span class="day-meta-item">🏨 {{ day.accommodation }}</span>
                    </div>
                  </div>
                </div>

                <!-- 景点列表 -->
                <div class="attractions-grid">
                  <div
                    v-for="(attraction, attrIndex) in day.attractions"
                    :key="attrIndex"
                    class="attraction-card"
                  >
                    <div class="attraction-image">
                      <img
                        v-if="attractionPhotos[`${day.day_index}-${attrIndex}`]"
                        :src="attractionPhotos[`${day.day_index}-${attrIndex}`]"
                        :alt="attraction.name"
                        @error="(e) => handleImageError(e, day.day_index, attrIndex)"
                      />
                      <div v-else class="image-placeholder">
                        <span class="placeholder-icon">📷</span>
                        <span class="placeholder-text">{{ attraction.name?.charAt(0) || '?' }}</span>
                      </div>
                      <span class="attraction-badge">{{ attrIndex + 1 }}</span>
                      <span v-if="attraction.ticket_price" class="price-badge">¥{{ attraction.ticket_price }}</span>
                      <div v-if="editMode" class="edit-overlay">
                        <a-button size="small" @click="moveAttraction(day.day_index, attrIndex, 'up')" :disabled="attrIndex === 0">↑</a-button>
                        <a-button size="small" @click="moveAttraction(day.day_index, attrIndex, 'down')" :disabled="attrIndex === day.attractions.length - 1">↓</a-button>
                        <a-button size="small" danger @click="deleteAttraction(day.day_index, attrIndex)">×</a-button>
                      </div>
                    </div>
                    <div class="attraction-info">
                      <h4 class="attraction-name">{{ attraction.name }}</h4>
                      <p class="attraction-desc">{{ attraction.description }}</p>
                      <div class="attraction-meta">
                        <span v-if="attraction.visit_duration" class="meta-tag">⏱ {{ attraction.visit_duration }}分钟</span>
                        <span v-if="attraction.rating" class="meta-tag">⭐ {{ attraction.rating }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 交通路线 -->
                <div v-if="day.routes && day.routes.length" class="routes-section">
                  <h4 class="subsection-title">交通路线</h4>
                  <div v-for="(route, routeIndex) in day.routes" :key="routeIndex" class="route-card">
                    <div class="route-header">
                      <span class="route-from">{{ route.origin }}</span>
                      <span class="route-arrow">→</span>
                      <span class="route-to">{{ route.destination }}</span>
                    </div>
                    <div class="route-stats">
                      <span>⏱ {{ route.duration }}分钟</span>
                      <span>📏 {{ route.distance }}公里</span>
                      <span class="route-mode">{{ route.mode }}</span>
                    </div>
                  </div>
                </div>

                <!-- 餐饮 -->
                <div v-if="day.meals && day.meals.length" class="meals-section">
                  <h4 class="subsection-title">餐饮推荐</h4>
                  <div class="meals-grid">
                    <div v-for="(meal, mealIndex) in day.meals" :key="mealIndex" class="meal-card">
                      <span class="meal-type">{{ getMealLabel(meal.type) }}</span>
                      <span class="meal-name">{{ meal.name }}</span>
                      <span v-if="meal.estimated_cost" class="meal-price">¥{{ meal.estimated_cost }}</span>
                    </div>
                  </div>
                </div>

                <!-- 酒店 -->
                <div v-if="day.hotel" class="hotel-section">
                  <h4 class="subsection-title">住宿安排</h4>
                  <div class="hotel-card">
                    <div class="hotel-placeholder">🏨</div>
                    <div class="hotel-info">
                      <h4 class="hotel-name">{{ day.hotel.name }}</h4>
                      <p class="hotel-address">{{ day.hotel.address }}</p>
                      <div class="hotel-meta">
                        <span class="hotel-price">{{ day.hotel.price_range }}</span>
                        <span class="hotel-rating">⭐ {{ day.hotel.rating }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 天气信息 -->
        <section v-if="tripPlan.weather_info && tripPlan.weather_info.length" id="weather" class="weather-section">
          <div class="section-header">
            <span class="section-number">03</span>
            <h2 class="section-title">天气信息</h2>
          </div>
          <div class="weather-grid">
            <div v-for="(weather, index) in tripPlan.weather_info" :key="index" class="weather-card">
              <div class="weather-date">
                <span class="weather-day">{{ new Date(weather.date).getDate() }}</span>
                <span class="weather-month">{{ new Date(weather.date).toLocaleDateString('zh-CN', { month: 'short' }) }}</span>
              </div>
              <div class="weather-temp">{{ weather.night_temp }}° — {{ weather.day_temp }}°</div>
              <div class="weather-condition">{{ weather.day_weather }}</div>
              <div class="weather-details">
                <span>🌙 {{ weather.night_weather }}</span>
                <span>💨 {{ weather.wind_power }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">✈️</div>
      <h3>暂无行程计划</h3>
      <p>开始规划您的下一次冒险</p>
      <a-button type="primary" size="large" @click="router.push('/')">开始规划</a-button>
    </div>

    <!-- 回到顶部 -->
    <div v-show="showBackTop" class="back-top" @click="scrollToTop">↑</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import AMapLoader from '@amap/amap-jsapi-loader'
import html2canvas from 'html2canvas'
import jsPDF from 'jspdf'
import type { TripPlan } from '@/types'

const router = useRouter()
const tripPlan = ref<TripPlan | null>(null)
const editMode = ref(false)
const originalPlan = ref<TripPlan | null>(null)
const attractionPhotos = ref<Record<string, string>>({})
const activeSection = ref('overview')
const showBackTop = ref(false)
let map: any = null

const totalAttractions = computed(() => {
  if (!tripPlan.value?.days) return 0
  return tripPlan.value.days.reduce((sum, day) => sum + (day.attractions?.length || 0), 0)
})

onMounted(async () => {
  const data = sessionStorage.getItem('tripPlan')
  if (data) {
    tripPlan.value = JSON.parse(data)
    await loadAttractionPhotos()
    await nextTick()
    initMap()
  }
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  if (map) map.destroy()
  window.removeEventListener('scroll', handleScroll)
})

const handleScroll = () => {
  showBackTop.value = window.scrollY > 400
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const initMap = async () => {
  if (!tripPlan.value) return

  try {
    const AMap = await AMapLoader.load({
      key: import.meta.env.VITE_AMAP_WEB_JS_KEY || 'YOUR_AMAP_KEY',
      version: '2.0',
      plugins: ['AMap.Scale', 'AMap.ToolBar']
    })

    const mapContainer = document.getElementById('amap-container')
    if (!mapContainer) return

    map = new AMap.Map(mapContainer, {
      zoom: 11,
      center: [116.397428, 39.90923],
      mapStyle: 'amap://styles/whitesmoke',
      viewMode: '3D'
    })

    const markers: any[] = []
    tripPlan.value.days.forEach((day, dayIndex) => {
      day.attractions.forEach((attraction, attrIndex) => {
        if (attraction.location?.longitude && attraction.location?.latitude) {
          const marker = new AMap.Marker({
            position: [attraction.location.longitude, attraction.location.latitude],
            title: attraction.name
          })
          markers.push(marker)
        }
      })
    })

    if (markers.length > 0) {
      map.add(markers)
      map.setFitView(markers)
    }
  } catch (error) {
    console.error('地图加载失败:', error)
  }
}

const goBack = () => {
  router.push('/')
}

const scrollToSection = ({ key }: { key: string }) => {
  activeSection.value = key
  const element = document.getElementById(key)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const toggleEditMode = () => {
  editMode.value = true
  originalPlan.value = JSON.parse(JSON.stringify(tripPlan.value))
  message.info('进入编辑模式')
}

const saveChanges = () => {
  editMode.value = false
  if (tripPlan.value) {
    sessionStorage.setItem('tripPlan', JSON.stringify(tripPlan.value))
  }
  message.success('修改已保存')
}

const cancelEdit = () => {
  if (originalPlan.value) {
    tripPlan.value = JSON.parse(JSON.stringify(originalPlan.value))
  }
  editMode.value = false
  message.info('已取消编辑')
}

const deleteAttraction = (dayIndex: number, attrIndex: number) => {
  if (!tripPlan.value) return
  const day = tripPlan.value.days[dayIndex]
  if (day.attractions.length <= 1) {
    message.warning('每天至少需要保留一个景点')
    return
  }
  day.attractions.splice(attrIndex, 1)
  message.success('景点已删除')
}

const moveAttraction = (dayIndex: number, attrIndex: number, direction: 'up' | 'down') => {
  if (!tripPlan.value) return
  const day = tripPlan.value.days[dayIndex]
  const attractions = day.attractions
  if (direction === 'up' && attrIndex > 0) {
    [attractions[attrIndex], attractions[attrIndex - 1]] = [attractions[attrIndex - 1], attractions[attrIndex]]
  } else if (direction === 'down' && attrIndex < attractions.length - 1) {
    [attractions[attrIndex], attractions[attrIndex + 1]] = [attractions[attrIndex + 1], attractions[attrIndex]]
  }
}

const getMealLabel = (type: string): string => {
  const labels: Record<string, string> = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '小吃'
  }
  return labels[type] || type
}

const loadAttractionPhotos = async () => {
  if (!tripPlan.value) return

  // 收集所有需要加载的景点照片请求
  const photoRequests: Array<{key: string, name: string, city: string, category?: string}> = []

  for (const day of tripPlan.value.days) {
    for (let attrIndex = 0; attrIndex < day.attractions.length; attrIndex++) {
      const attraction = day.attractions[attrIndex]
      const photoKey = `${day.day_index}-${attrIndex}`
      if (!attractionPhotos.value[photoKey]) {
        photoRequests.push({
          key: photoKey,
          name: attraction.name,
          city: tripPlan.value.city,
          category: attraction.category
        })
      }
    }
  }

  // 批量并行加载照片
  if (photoRequests.length > 0) {
    console.log(`[Result] 开始加载 ${photoRequests.length} 张景点照片...`)

    const loadPromises = photoRequests.map(async (req) => {
      try {
        const params = new URLSearchParams({
          name: req.name,
          city: req.city
        })
        if (req.category) {
          params.append('category', req.category)
        }

        const response = await fetch(`/api/poi/photo?${params.toString()}`)
        if (response.ok) {
          const result = await response.json()
          if (result.data?.photo_url) {
            // 预加载图片以确保它可用
            await preloadImage(result.data.photo_url)
            attractionPhotos.value[req.key] = result.data.photo_url
            console.log(`[Result] ✅ 照片加载成功: ${req.name}`)
          } else {
            console.log(`[Result] ⚠️ 未找到照片: ${req.name}`)
          }
        }
      } catch (error) {
        console.error(`[Result] ❌ 获取景点照片失败: ${req.name}`, error)
      }
    })

    await Promise.allSettled(loadPromises)
    console.log(`[Result] 景点照片加载完成`)
  }
}

// 预加载图片工具函数
const preloadImage = (src: string): Promise<void> => {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve()
    img.onerror = () => reject(new Error(`图片加载失败: ${src}`))
    img.src = src
  })
}

// 处理图片加载失败
const handleImageError = (e: Event, dayIndex: number, attrIndex: number) => {
  console.error(`[Result] 图片加载失败: day-${dayIndex}-attr-${attrIndex}`)
  const photoKey = `${dayIndex}-${attrIndex}`
  // 移除失败的图片URL，显示占位符
  delete attractionPhotos.value[photoKey]
}

// 杂志风格占位图 - 根据景点名称返回对应的精美占位图
const getPlaceholderImage = (name: string): string | null => {
  if (!name) return null
  const nameLower = name.toLowerCase()

  // 杂志风格占位图映射 - 使用Unsplash高质量图片
  const placeholders: Record<string, string> = {
    // 著名景点
    '故宫': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80',
    '长城': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80',
    '天坛': 'https://images.unsplash.com/photo-1537410856881-6c5a0f81b0e1?w=800&q=80',
    '颐和园': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '西湖': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '黄山': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '桂林': 'https://images.unsplash.com/photo-1537531383496-f4749a4b8590?w=800&q=80',
    '张家界': 'https://images.unsplash.com/photo-1537531383496-f4749a4b8590?w=800&q=80',
    '九寨沟': 'https://images.unsplash.com/photo-1537531383496-f4749a4b8590?w=800&q=80',
    '丽江': 'https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800&q=80',
    '大理': 'https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800&q=80',
    '凤凰': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '乌镇': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '周庄': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '西塘': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '平遥': 'https://images.unsplash.com/photo-1565193351677-443995a00d43?w=800&q=80',
    '拉萨': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '布达拉宫': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '泰山': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '华山': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '峨眉山': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '普陀山': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '九华山': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '少林寺': 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80',
    '兵马俑': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '大雁塔': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '钟楼': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '鼓楼': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '回民街': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '洪崖洞': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '解放碑': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '磁器口': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '宽窄巷子': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '锦里': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '春熙路': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '都江堰': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '青城山': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '大熊猫': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800&q=80',
    '熊猫': 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=800&q=80',
    '外滩': 'https://images.unsplash.com/photo-1548266652-99cf277df5c8?w=800&q=80',
    '东方明珠': 'https://images.unsplash.com/photo-1548266652-99cf277df5c8?w=800&q=80',
    '豫园': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '城隍庙': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '田子坊': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '新天地': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '静安寺': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '中山陵': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '明孝陵': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '夫子庙': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '秦淮河': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '总统府': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '玄武湖': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '拙政园': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '狮子林': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '虎丘': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '寒山寺': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '留园': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '周庄': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '同里': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',
    '鼓浪屿': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '南普陀': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '厦门大学': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '环岛路': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '曾厝垵': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '栈桥': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '八大关': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '崂山': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '五四广场': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '金沙滩': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '亚龙湾': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '天涯海角': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '蜈支洲岛': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '南山': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '大东海': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '广州塔': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '小蛮腰': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '陈家祠': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '沙面': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '白云山': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '世界之窗': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '欢乐谷': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '东部华侨城': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '黄鹤楼': 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80',
    '东湖': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '户部巷': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '橘子洲': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '岳麓山': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '太平老街': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '石林': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '滇池': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '翠湖': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '云南民族村': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '西山': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '滕王阁': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '三坊七巷': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '甲秀楼': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '黔灵山': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '青秀山': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '骑楼老街': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '假日海滩': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '塔尔寺': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '青海湖': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '西夏王陵': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '沙湖': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80',
    '大召寺': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '天津之眼': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '古文化街': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '五大道': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '沈阳故宫': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
    '张氏帅府': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80',
  }

  // 精确匹配
  for (const key in placeholders) {
    if (nameLower.includes(key.toLowerCase())) {
      return placeholders[key]
    }
  }

  // 根据关键词类别返回对应图片
  if (nameLower.includes('寺') || nameLower.includes('庙') || nameLower.includes('塔')) {
    return 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80'
  }
  if (nameLower.includes('山') || nameLower.includes('峰') || nameLower.includes('岭')) {
    return 'https://images.unsplash.com/photo-1548013146-72479768bada?w=800&q=80'
  }
  if (nameLower.includes('湖') || nameLower.includes('江') || nameLower.includes('河')) {
    return 'https://images.unsplash.com/photo-1537531383496-f4749a4b8590?w=800&q=80'
  }
  if (nameLower.includes('海') || nameLower.includes('湾') || nameLower.includes('滩')) {
    return 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80'
  }
  if (nameLower.includes('园') || nameLower.includes('林') || nameLower.includes('公园')) {
    return 'https://images.unsplash.com/photo-1598326061335-626a103a9919?w=800&q=80'
  }
  if (nameLower.includes('城') || nameLower.includes('镇') || nameLower.includes('古')) {
    return 'https://images.unsplash.com/photo-1527838832700-5059252407fa?w=800&q=80'
  }
  if (nameLower.includes('楼') || nameLower.includes('阁') || nameLower.includes('殿')) {
    return 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80'
  }
  if (nameLower.includes('博物馆') || nameLower.includes('展览馆')) {
    return 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&q=80'
  }

  // 默认返回高质量风景图
  return 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80'
}

// 图片加载完成回调
const onImageLoad = (dayIndex: number, attrIndex: number) => {
  console.log(`[Result] ✅ 图片加载成功: day-${dayIndex}-attr-${attrIndex}`)
}

const exportAsImage = async () => {
  try {
    message.loading({ content: '正在生成图片...', key: 'export' })
    const element = await getExportElement()
    if (!element) {
      message.error('导出失败：找不到内容')
      return
    }

    const canvas = await html2canvas(element, {
      backgroundColor: '#FAF7F2',
      scale: 2,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    const link = document.createElement('a')
    link.download = `旅行计划-${tripPlan.value?.city || '未命名'}-${new Date().toISOString().slice(0,10)}.png`
    link.href = canvas.toDataURL('image/png', 0.95)
    link.click()

    document.body.removeChild(element)
    message.success({ content: '图片导出成功', key: 'export' })
  } catch (error) {
    console.error('导出失败:', error)
    message.error({ content: '导出失败', key: 'export' })
  }
}

const exportAsPDF = async () => {
  try {
    message.loading({ content: '正在生成PDF...', key: 'export' })
    const element = await getExportElement()
    if (!element) {
      message.error('导出失败：找不到内容')
      return
    }

    const canvas = await html2canvas(element, {
      backgroundColor: '#FAF7F2',
      scale: 3,
      logging: false,
      useCORS: true,
      allowTaint: true
    })

    const imgData = canvas.toDataURL('image/jpeg', 0.95)
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const pdfWidth = 210
    const pdfHeight = 297
    const imgWidth = pdfWidth
    const imgHeight = (canvas.height * imgWidth) / canvas.width

    let heightLeft = imgHeight
    let position = 0

    pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight)
    heightLeft -= pdfHeight

    while (heightLeft > 0) {
      position = heightLeft - imgHeight
      pdf.addPage()
      pdf.addImage(imgData, 'JPEG', 0, position, imgWidth, imgHeight)
      heightLeft -= pdfHeight
    }

    pdf.save(`旅行计划-${tripPlan.value?.city || '未命名'}-${new Date().toISOString().slice(0,10)}.pdf`)

    document.body.removeChild(element)
    message.success({ content: 'PDF导出成功', key: 'export' })
  } catch (error) {
    console.error('导出失败:', error)
    message.error({ content: '导出失败', key: 'export' })
  }
}

const getExportElement = async (): Promise<HTMLElement | null> => {
  const exportContainer = document.createElement('div')
  exportContainer.className = 'export-container'
  exportContainer.style.cssText = `
    position: fixed;
    top: 0;
    left: -9999px;
    width: 1200px;
    background: #FAF7F2;
    padding: 40px;
  `

  const originalContent = document.querySelector('.magazine-result-container') as HTMLElement
  if (!originalContent) return null

  const contentToExport = originalContent.cloneNode(true) as HTMLElement

  const elementsToRemove = contentToExport.querySelectorAll('.side-nav, .back-top, .edit-overlay, .empty-state, .magazine-header')
  elementsToRemove.forEach(el => el.remove())

  const decorativeBg = contentToExport.querySelector('.decorative-bg')
  if (decorativeBg) {
    decorativeBg.innerHTML = `
      <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, rgba(232,138,93,0.05) 0%, rgba(220,201,75,0.05) 50%, rgba(217,232,247,0.05) 100%);"></div>
    `
  }

  const exportHeader = document.createElement('div')
  exportHeader.style.cssText = `
    text-align: center;
    padding: 40px 0 30px;
    border-bottom: 2px solid #E5E7EB;
    margin-bottom: 40px;
  `
  exportHeader.innerHTML = `
    <div style="font-family: 'Inter', sans-serif; font-size: 12px; letter-spacing: 4px; color: #C05621; margin-bottom: 16px;">
      TRAVEL PLAN
    </div>
    <h1 style="font-family: 'Playfair Display', serif; font-size: 42px; font-weight: 700; color: #111827; margin: 0 0 12px;">
      ${tripPlan.value?.city || ''} 旅行计划
    </h1>
    <div style="font-family: 'Inter', sans-serif; font-size: 14px; color: #6B7280;">
      ${tripPlan.value?.start_date || ''} — ${tripPlan.value?.end_date || ''}
    </div>
  `

  exportContainer.appendChild(exportHeader)
  exportContainer.appendChild(contentToExport.querySelector('.magazine-content') || contentToExport)

  document.body.appendChild(exportContainer)
  await waitForImages(exportContainer)

  return exportContainer
}

const waitForImages = (element: HTMLElement): Promise<void> => {
  return new Promise((resolve) => {
    const images = element.querySelectorAll('img')
    if (images.length === 0) {
      resolve()
      return
    }

    let loadedCount = 0
    const checkLoaded = () => {
      loadedCount++
      if (loadedCount === images.length) {
        setTimeout(resolve, 500)
      }
    }

    images.forEach((img) => {
      if (img.complete) {
        checkLoaded()
      } else {
        img.onload = checkLoaded
        img.onerror = checkLoaded
      }
    })

    setTimeout(resolve, 5000)
  })
}

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:wght@400;500;600;700&family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@400;500;600;700&display=swap');

/* 容器 */
.magazine-result-container {
  min-height: 100vh;
  background: #FAF7F2;
  position: relative;
  overflow-x: hidden;
}

/* 装饰背景 */
.decorative-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.deco-shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.3;
}

.deco-1 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #E88A5D 0%, #ECC94B 100%);
  top: -100px;
  right: -100px;
}

.deco-2 {
  width: 300px;
  height: 300px;
  background: linear-gradient(135deg, #D9E8F7 0%, #1a365d 100%);
  bottom: 20%;
  left: -50px;
}

/* 头部 */
.magazine-header {
  position: relative;
  z-index: 10;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-brand {
  display: flex;
  align-items: center;
  gap: 16px;
  font-family: 'Playfair Display', serif;
  font-size: 14px;
  letter-spacing: 4px;
  color: #6B7280;
}

.brand-line {
  width: 30px;
  height: 1px;
  background: #D1D5DB;
}

.elegant-btn {
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  height: 40px;
  padding: 0 20px;
  border-radius: 20px;
  transition: all 0.3s ease;
}

.outline-btn {
  background: transparent;
  border: 1px solid #E5E7EB;
}

.subtle-btn {
  background: #F9FAFB;
  border: 1px solid transparent;
}

.primary-btn {
  background: #1a365d;
  border-color: #1a365d;
}

/* 主内容 */
.magazine-content {
  position: relative;
  z-index: 1;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  gap: 24px;
  padding: 0 24px 64px;
}

/* 侧边导航 */
.side-nav {
  width: 180px;
  flex-shrink: 0;
}

.nav-menu {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.nav-menu :deep(.ant-menu-item) {
  margin: 4px 8px;
  border-radius: 8px;
}

.nav-menu :deep(.ant-menu-item-selected) {
  background: #1a365d !important;
  color: white !important;
}

/* 主内容区 */
.main-content {
  flex: 1;
  min-width: 0;
}

/* 英雄区域 */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 48px;
  padding: 32px 0;
}

.hero-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hero-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Inter', sans-serif;
  font-size: 12px;
  letter-spacing: 2px;
  text-transform: uppercase;
  color: #C05621;
  margin-bottom: 24px;
}

.meta-divider {
  color: #D1D5DB;
}

.hero-title {
  font-family: 'Playfair Display', serif;
  font-size: 48px;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 24px;
  color: #111827;
}

.title-line {
  display: block;
}

.title-accent {
  font-style: italic;
  color: #1a365d;
}

.hero-description {
  font-family: 'Crimson Pro', serif;
  font-size: 18px;
  line-height: 1.7;
  color: #6B7280;
}

.map-container {
  width: 100%;
  height: 400px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.15);
}

/* 章节头部 */
.section-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.section-number {
  font-family: 'Playfair Display', serif;
  font-size: 36px;
  font-weight: 300;
  font-style: italic;
  color: #C05621;
}

.section-title {
  font-family: 'Playfair Display', serif;
  font-size: 24px;
  font-weight: 600;
  color: #111827;
}

/* 预算区域 */
.budget-section {
  margin-bottom: 48px;
}

.budget-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.budget-item {
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.budget-icon {
  font-size: 28px;
}

.budget-item > div {
  display: flex;
  flex-direction: column;
}

.budget-label {
  font-size: 12px;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.budget-value {
  font-family: 'Playfair Display', serif;
  font-size: 20px;
  font-weight: 600;
  color: #111827;
}

.budget-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  background: #1a365d;
  border-radius: 12px;
  color: white;
}

.total-amount {
  font-family: 'Playfair Display', serif;
  font-size: 28px;
  font-weight: 700;
}

/* 每日行程 */
.days-section {
  margin-bottom: 48px;
}

.days-timeline {
  position: relative;
}

.days-timeline::before {
  content: '';
  position: absolute;
  left: 50px;
  top: 30px;
  bottom: 30px;
  width: 2px;
  background: linear-gradient(180deg, #E5E7EB 0%, transparent 100%);
}

.day-block {
  display: flex;
  gap: 24px;
  margin-bottom: 32px;
}

.day-marker {
  width: 60px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.day-number {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a365d;
  color: white;
  border-radius: 50%;
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 700;
  box-shadow: 0 0 0 4px rgba(26, 54, 93, 0.1);
}

.day-content {
  flex: 1;
}

.day-header {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.day-date {
  width: 70px;
  height: 70px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #C05621 0%, #E88A5D 100%);
  border-radius: 12px;
  color: white;
  flex-shrink: 0;
}

.date-day {
  font-family: 'Playfair Display', serif;
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.date-month {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.day-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.day-title {
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
}

.day-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6B7280;
}

/* 景点网格 */
.attractions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.attraction-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.attraction-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.attraction-image {
  position: relative;
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.attraction-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #F5EDE4 0%, #E8DED3 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.placeholder-icon {
  font-size: 36px;
  opacity: 0.5;
}

.placeholder-text {
  font-family: 'Playfair Display', serif;
  font-size: 42px;
  font-weight: 700;
  color: #D4C4B5;
}

.attraction-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 32px;
  height: 32px;
  background: #1a365d;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Playfair Display', serif;
  font-size: 14px;
  font-weight: 700;
}

.price-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.95);
  color: #C05621;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.edit-overlay {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.8);
  padding: 8px;
  border-radius: 8px;
}

.attraction-info {
  padding: 16px;
}

.attraction-name {
  font-family: 'Playfair Display', serif;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.attraction-desc {
  font-family: 'Crimson Pro', serif;
  font-size: 14px;
  line-height: 1.5;
  color: #6B7280;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.attraction-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.meta-tag {
  font-size: 12px;
  color: #9CA3AF;
}

/* 路线区域 */
.routes-section {
  margin-bottom: 20px;
}

.subsection-title {
  font-family: 'Playfair Display', serif;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.route-card {
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 12px;
}

.route-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.route-arrow {
  color: #9CA3AF;
}

.route-stats {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6B7280;
}

.route-mode {
  margin-left: auto;
  padding: 4px 12px;
  background: #F0F5FA;
  color: #1a365d;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

/* 餐饮区域 */
.meals-section {
  margin-bottom: 20px;
}

.meals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.meal-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.meal-type {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #D69E2E;
  color: white;
  border-radius: 8px;
  font-size: 16px;
  flex-shrink: 0;
}

.meal-name {
  flex: 1;
  font-size: 13px;
  font-weight: 500;
}

.meal-price {
  font-size: 12px;
  color: #C05621;
  font-weight: 600;
}

/* 酒店区域 */
.hotel-section {
  margin-bottom: 20px;
}

.hotel-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.hotel-placeholder {
  width: 120px;
  height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #D9E8F7 0%, #F0F5FA 100%);
  border-radius: 8px;
  font-size: 48px;
  flex-shrink: 0;
}

.hotel-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hotel-name {
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 600;
}

.hotel-address {
  font-size: 13px;
  color: #6B7280;
}

.hotel-meta {
  display: flex;
  gap: 16px;
}

.hotel-price {
  font-size: 14px;
  color: #C05621;
  font-weight: 600;
}

.hotel-rating {
  font-size: 14px;
  color: #6B7280;
}

/* 天气区域 */
.weather-section {
  margin-bottom: 48px;
}

.weather-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 16px;
}

.weather-card {
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.weather-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
}

.weather-day {
  font-family: 'Playfair Display', serif;
  font-size: 28px;
  font-weight: 700;
  color: #1a365d;
}

.weather-month {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #9CA3AF;
}

.weather-temp {
  font-family: 'Playfair Display', serif;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
}

.weather-condition {
  font-size: 13px;
  color: #6B7280;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #F3F4F6;
}

.weather-details {
  display: flex;
  justify-content: center;
  gap: 12px;
  font-size: 12px;
  color: #6B7280;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
}

.empty-state h3 {
  font-family: 'Playfair Display', serif;
  font-size: 24px;
  margin-bottom: 8px;
}

.empty-state p {
  color: #6B7280;
  margin-bottom: 32px;
}

/* 回到顶部 */
.back-top {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a365d;
  color: white;
  border-radius: 50%;
  box-shadow: 0 8px 24px rgba(26, 54, 93, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 100;
  font-size: 20px;
  font-weight: 700;
}

.back-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(26, 54, 93, 0.5);
}

/* 响应式 */
@media (max-width: 1024px) {
  .hero-section {
    grid-template-columns: 1fr;
  }

  .budget-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .attractions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .magazine-header {
    flex-direction: column;
    gap: 16px;
  }

  .magazine-content {
    flex-direction: column;
  }

  .side-nav {
    width: 100%;
  }

  .nav-menu {
    display: flex;
    overflow-x: auto;
  }

  .days-timeline::before {
    display: none;
  }

  .day-block {
    flex-direction: column;
  }

  .day-marker {
    flex-direction: row;
    width: 100%;
  }

  .budget-grid {
    grid-template-columns: 1fr;
  }

  .attractions-grid {
    grid-template-columns: 1fr;
  }

  .day-header {
    flex-direction: column;
  }

  .hotel-card {
    flex-direction: column;
  }

  .hotel-placeholder {
    width: 100%;
  }
}
</style>
