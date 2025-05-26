import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Mail, BarChart3, Shield, Clock } from 'lucide-react'

const Landing = () => {
  const { isAuthenticated, login, loading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])

  const handleLogin = async () => {
    try {
      await login()
    } catch (error) {
      console.error('Login failed:', error)
      alert('Login failed. Please try again.')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Mail className="h-8 w-8 text-primary-600" />
            <h1 className="text-2xl font-bold text-gray-900">Inbox Clarity</h1>
          </div>
          <a href="/privacy" className="text-gray-600 hover:text-primary-600">
            Privacy Policy
          </a>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            AI-Powered Email Classification
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Get instant clarity on your inbox composition. Our AI automatically 
            categorizes your last 100 emails to help you understand what's in your inbox.
          </p>
          
          <button
            onClick={handleLogin}
            className="btn-primary text-lg px-8 py-4 mb-12"
          >
            Sign in with Google
          </button>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mt-16">
            <div className="card text-center">
              <Mail className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Gmail Integration</h3>
              <p className="text-gray-600">
                Securely connect to your Gmail account with OAuth 2.0
              </p>
            </div>
            
            <div className="card text-center">
              <BarChart3 className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Smart Categories</h3>
              <p className="text-gray-600">
                8 intelligent categories: Work, Personal, Finance, and more
              </p>
            </div>
            
            <div className="card text-center">
              <Shield className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Privacy First</h3>
              <p className="text-gray-600">
                Your emails are processed securely and never stored
              </p>
            </div>
            
            <div className="card text-center">
              <Clock className="h-12 w-12 text-primary-600 mx-auto mb-4" />
              <h3 className="font-semibold text-lg mb-2">Free Daily Limit</h3>
              <p className="text-gray-600">
                Process up to 100 emails daily with our free tier
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Landing
