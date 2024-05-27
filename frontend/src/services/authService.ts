/**
 * Authentication service for handling login, logout, and token management
 */

import axios from 'axios'
import { LoginRequest, LoginResponse, User } from '../types/auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const TOKEN_KEY = 'smart_grid_token'
const USER_KEY = 'smart_grid_user'

/**
 * Login user and store token
 */
export const login = async (username: string, password: string): Promise<LoginResponse> => {
  try {
    const response = await axios.post<LoginResponse>(
      `${API_BASE_URL}/api/v1/auth/login`,
      { username, password } as LoginRequest,
      {
        headers: {
          'Content-Type': 'application/json'
        }
      }
    )

    const { access_token, user } = response.data

    // Store token and user in localStorage
    localStorage.setItem(TOKEN_KEY, access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))

    return response.data
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error('Invalid username or password')
    }
    throw new Error(error.response?.data?.detail || 'Login failed')
  }
}

/**
 * Logout user and clear stored data
 */
export const logout = (): void => {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

/**
 * Get stored token
 */
export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * Get stored user
 */
export const getUser = (): User | null => {
  const userStr = localStorage.getItem(USER_KEY)
  if (!userStr) return null

  try {
    return JSON.parse(userStr) as User
  } catch {
    return null
  }
}

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return !!getToken()
}

/**
 * Get current user info from API
 */
export const getCurrentUser = async (): Promise<User> => {
  const token = getToken()
  if (!token) {
    throw new Error('No token found')
  }

  try {
    const response = await axios.get<User>(
      `${API_BASE_URL}/api/v1/auth/me`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    // Update stored user
    localStorage.setItem(USER_KEY, JSON.stringify(response.data))

    return response.data
  } catch (error: any) {
    if (error.response?.status === 401) {
      // Token is invalid, clear storage
      logout()
      throw new Error('Session expired')
    }
    throw new Error(error.response?.data?.detail || 'Failed to get user info')
  }
}

/**
 * Update stored user
 */
export const updateStoredUser = (user: User): void => {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export default {
  login,
  logout,
  getToken,
  getUser,
  isAuthenticated,
  getCurrentUser,
  updateStoredUser
}

