import axios from 'axios'
import type { TripFormData, TripPlanResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5分钟超时
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('✅ 收到响应:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('❌ 响应错误:', error.response?.status, error.code, error.message)
    
    // 详细的错误信息
    if (error.code === 'ECONNABORTED') {
      console.error('⏱️ 请求超时，可能原因：')
      console.error('   1. 后端AI处理时间较长')
      console.error('   2. 网络连接不稳定')
      console.error('   3. MCP工具调用失败')
    } else if (error.code === 'ERR_NETWORK') {
      console.error('🌐 网络错误，请检查后端是否运行')
    } else if (error.response?.status === 500) {
      console.error('💥 服务器内部错误:', error.response.data)
    }
    
    return Promise.reject(error)
  }
)

/**
 * 生成旅行计划
 */
export async function generateTripPlan(formData: TripFormData): Promise<TripPlanResponse> {
  try {
    const response = await apiClient.post<TripPlanResponse>('/api/trip/plan', formData)
    return response.data
  } catch (error: any) {
    console.error('生成旅行计划失败:', error)
    throw new Error(error.response?.data?.detail || error.message || '生成旅行计划失败')
  }
}

/**
 * 使用SSE流式生成旅行计划
 */
export async function generateTripPlanStream(
  formData: TripFormData,
  onProgress: (progress: any) => void
): Promise<TripPlanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/trip/plan/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  })

  if (!response.ok) {
    throw new Error(`请求失败: ${response.status}`)
  }

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  if (!reader) {
    throw new Error('无法读取响应流')
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (data.type === 'result') {
            // 后端返回的是 { type: 'result', success: true, data: {...} }
            // 需要转换为 { success: true, message: '', data: {...} }
            return {
              success: data.success,
              message: '旅行计划生成成功',
              data: data.data
            }
          } else if (data.status === 'completed') {
            // 只推送进度，不返回，等待后续的 result 数据
            onProgress(data)
          } else if (data.status === 'error') {
            throw new Error(data.message || '生成失败')
          } else {
            onProgress(data)
          }
        } catch (e) {
          console.error('解析SSE数据失败:', e)
        }
      }
    }
  }

  throw new Error('SSE流未返回结果')
}

/**
 * 健康检查
 */
export async function healthCheck(): Promise<any> {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error: any) {
    console.error('健康检查失败:', error)
    throw new Error(error.message || '健康检查失败')
  }
}

export default apiClient

