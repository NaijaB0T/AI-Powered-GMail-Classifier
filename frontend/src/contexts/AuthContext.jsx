import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async (retries = 3) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/user/status`, {
        credentials: 'include',
        cache: 'no-cache' // Prevent caching issues
      })
      const data = await response.json()
      setIsAuthenticated(data.authenticated)
      if (data.authenticated) {
        setUser({ authenticated: true })
      } else {
        setUser(null)
      }
    } catch (error) {
      console.error('Error checking auth status:', error)
      
      // Retry logic for network issues
      if (retries > 0) {
        await new Promise(resolve => setTimeout(resolve, 1000))
        return checkAuthStatus(retries - 1)
      }
      
      setIsAuthenticated(false)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/google`, {
        credentials: 'include'
      })
      const data = await response.json()
      
      if (data.auth_url) {
        window.location.href = data.auth_url
      } else {
        alert('Failed to get Google auth URL')
      }
    } catch (error) {
      console.error('Login error:', error)
      alert('Login failed. Please try again.')
    }
  }

  const logout = async () => {
    try {
      await fetch(`${import.meta.env.VITE_API_URL}/api/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      })
      setIsAuthenticated(false)
      setUser(null)
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const value = {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
    checkAuthStatus
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
