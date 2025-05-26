import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import api from '../utils/api'
import LoadingSpinner from '../components/LoadingSpinner'
import CategoryCard from '../components/CategoryCard'
import { 
  Mail, LogOut, BarChart3, RefreshCw, AlertCircle, 
  TrendingUp
} from 'lucide-react'

const Dashboard = () => {
  const { isAuthenticated, logout, loading: authLoading } = useAuth()
  const navigate = useNavigate()
  const [emailData, setEmailData] = useState(null)
  const [usage, setUsage] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/')
    }
  }, [isAuthenticated, authLoading, navigate])

  useEffect(() => {
    if (isAuthenticated) {
      fetchUsage()
    }
  }, [isAuthenticated])

  const fetchUsage = async () => {
    try {
      const response = await api.get('/api/user/usage')
      setUsage(response.data)
    } catch (error) {
      console.error('Error fetching usage:', error)
    }
  }

  const classifyEmails = async () => {
    setProcessing(true)
    setError(null)
    
    try {
      const response = await api.post('/api/emails/classify')
      setEmailData(response.data)
      await fetchUsage() // Refresh usage after processing
    } catch (error) {
      console.error('Error classifying emails:', error)
      if (error.response?.status === 429) {
        setError('Daily processing limit reached. Try again tomorrow!')
      } else {
        setError('Failed to classify emails. Please try again.')
      }
    } finally {
      setProcessing(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" message="Loading your dashboard..." />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Mail className="h-8 w-8 text-primary-600" />
              <h1 className="text-2xl font-bold text-gray-900">Inbox Clarity</h1>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center space-x-2 text-gray-600 hover:text-red-600"
            >
              <LogOut className="h-5 w-5" />
              <span>Logout</span>
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {/* Usage Stats */}
        {usage && (
          <div className="card mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold mb-1">Daily Usage</h3>
                <p className="text-gray-600">
                  {usage.daily_processed} of {usage.daily_limit} emails processed today
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-primary-600">
                  {usage.remaining}
                </div>
                <div className="text-sm text-gray-500">remaining</div>
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-4">
              <div 
                className="bg-primary-600 h-2 rounded-full" 
                style={{ width: `${(usage.daily_processed / usage.daily_limit) * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Classification Section */}
        <div className="card mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Email Classification</h2>
            <button
              onClick={classifyEmails}
              disabled={processing || (usage && usage.remaining <= 0)}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`h-5 w-5 ${processing ? 'animate-spin' : ''}`} />
              <span>{processing ? 'Processing...' : 'Classify Emails'}</span>
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center space-x-3">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {processing && (
            <div className="text-center py-12">
              <LoadingSpinner 
                size="lg" 
                message="Fetching and classifying your emails... This may take a moment." 
              />
            </div>
          )}

          {emailData && !processing && (
            <div>
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="card bg-blue-50 border-blue-200">
                  <div className="flex items-center space-x-3">
                    <BarChart3 className="h-8 w-8 text-blue-600" />
                    <div>
                      <div className="text-2xl font-bold text-blue-900">
                        {emailData.total_processed}
                      </div>
                      <div className="text-blue-700">Total Processed</div>
                    </div>
                  </div>
                </div>
                
                <div className="card bg-green-50 border-green-200">
                  <div className="flex items-center space-x-3">
                    <Mail className="h-8 w-8 text-green-600" />
                    <div>
                      <div className="text-2xl font-bold text-green-900">
                        {emailData.unread_count}
                      </div>
                      <div className="text-green-700">Unread Emails</div>
                    </div>
                  </div>
                </div>

                {/* Classification Trend */}
                <div className="card bg-purple-50 border-purple-200">
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-8 w-8 text-purple-600" />
                    <div>
                      <div className="text-2xl font-bold text-purple-900">
                        Coming Soon!
                      </div>
                      <div className="text-purple-700">Classification Trend</div>
                    </div>
                  </div>
                </div>

                {/* Top Categories */}
                <div className="card bg-yellow-50 border-yellow-200">
                  <div className="flex items-center space-x-3">
                    <BarChart3 className="h-8 w-8 text-yellow-600" />
                    <div>
                      <div className="text-2xl font-bold text-yellow-900">
                        {Object.entries(emailData.categories)
                          .sort(([, countA], [, countB]) => countB - countA)
                          .slice(0, 1)
                          .map(([category]) => category)}
                      </div>
                      <div className="text-yellow-700">Top Category</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Categories Grid */}
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(emailData.categories).map(([category, count]) => (
                  <CategoryCard
                    key={category}
                    category={category}
                    count={count}
                    onClick={(cat) => console.log(`Clicked ${cat}`)}
                  />
                ))}
              </div>
            </div>
          )}

          {!emailData && !processing && (
            <div className="text-center py-12">
              <Mail className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Ready to analyze your inbox
              </h3>
              <p className="text-gray-600 mb-6">
                Click "Classify Emails" to process your last 100 emails and see the breakdown by category.
              </p>
            </div>
          )}
        </div>

        {/* Info Section */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">How it works</h3>
          <div className="grid md:grid-cols-3 gap-6 text-sm text-gray-600">
            <div>
              <div className="font-medium text-gray-900 mb-2">1. Secure Connection</div>
              <p>We securely access your Gmail using OAuth 2.0 - no passwords stored.</p>
            </div>
            <div>
              <div className="font-medium text-gray-900 mb-2">2. AI Classification</div>
              <p>Our AI analyzes email content and categorizes them into 8 smart categories.</p>
            </div>
            <div>
              <div className="font-medium text-gray-900 mb-2">3. Clear Overview</div>
              <p>Get instant insight into your inbox composition to better manage your emails.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
