/**
 * Authentication Context for managing global auth state
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import { message } from 'antd'
import { AuthContextType, User } from '../types/auth'
import * as authService from '../services/authService'

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = authService.getToken()
      const storedUser = authService.getUser()

      if (storedToken && storedUser) {
        setToken(storedToken)
        setUser(storedUser)

        // Optionally verify token is still valid
        try {
          const currentUser = await authService.getCurrentUser()
          setUser(currentUser)
        } catch (error) {
          // Token is invalid, clear everything
          authService.logout()
          setToken(null)
          setUser(null)
        }
      }

      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true)
      const response = await authService.login(username, password)
      
      setToken(response.access_token)
      setUser(response.user)
      
      message.success(`Welcome back, ${response.user.full_name}!`)
      navigate('/dashboard')
    } catch (error: any) {
      message.error(error.message || 'Login failed')
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    authService.logout()
    setToken(null)
    setUser(null)
    message.info('Logged out successfully')
    navigate('/login')
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
    authService.updateStoredUser(updatedUser)
  }

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!token && !!user,
    isLoading,
    login,
    logout,
    updateUser
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext

