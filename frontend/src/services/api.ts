/**
 * Base API client configuration
 * Centralized Axios instance with interceptors and error handling
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import toast from 'react-hot-toast'

// API base URL - can be configured via environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token, logging, etc.
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // Add timestamp to prevent caching
    if (config.params) {
      config.params._t = Date.now()
    } else {
      config.params = { _t: Date.now() }
    }

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.params)
    }

    return config
  },
  (error: AxiosError) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors globally
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.url}`, response.data)
    }
    return response
  },
  (error: AxiosError) => {
    // Handle different error types
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const message = (error.response.data as any)?.detail || error.message

      switch (status) {
        case 400:
          toast.error(`Bad Request: ${message}`)
          break
        case 401:
          toast.error('Unauthorized. Please log in.')
          break
        case 403:
          toast.error('Access forbidden.')
          break
        case 404:
          toast.error('Resource not found.')
          break
        case 422:
          toast.error(`Validation Error: ${message}`)
          break
        case 500:
          toast.error('Server error. Please try again later.')
          break
        case 503:
          toast.error('Service unavailable. Please try again later.')
          break
        default:
          toast.error(`Error: ${message}`)
      }

      console.error(`[API Error] ${status}:`, message)
    } else if (error.request) {
      // Request made but no response received
      toast.error('Network error. Please check your connection.')
      console.error('[API Network Error]', error.request)
    } else {
      // Something else happened
      toast.error('An unexpected error occurred.')
      console.error('[API Error]', error.message)
    }

    return Promise.reject(error)
  }
)

// Generic API methods
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.get<T>(url, config).then((res) => res.data),

  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.post<T>(url, data, config).then((res) => res.data),

  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.put<T>(url, data, config).then((res) => res.data),

  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.patch<T>(url, data, config).then((res) => res.data),

  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.delete<T>(url, config).then((res) => res.data),
}

// Health check utility
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await api.get('/health')
    return response.status === 'healthy'
  } catch (error) {
    return false
  }
}

export default apiClient

