import React, { useEffect, useState } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import OAuthCallback from './components/OAuthCallback'
import CategoryCard from './components/CategoryCard'

const Landing = () => {
  const { login, isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard')
    }
  }, [isAuthenticated, navigate])
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Inbox Clarity</h1>
        <p className="text-gray-600 mb-8">AI-Powered Gmail Classifier</p>
        <button 
          onClick={login}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg"
        >
          Sign in with Google
        </button>
      </div>
    </div>
  )
}
const Dashboard = () => {
  const { logout, isAuthenticated, loading } = useAuth()
  const navigate = useNavigate()
  const [classificationData, setClassificationData] = useState(null)
  const [isClassifying, setIsClassifying] = useState(false)
  const [usageData, setUsageData] = useState(null)
  const [error, setError] = useState(null)
  const [hasClassified, setHasClassified] = useState(false)
  
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      navigate('/')
    } else if (isAuthenticated) {
      fetchUsageData()
    }
  }, [isAuthenticated, loading, navigate])

  const fetchUsageData = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/user/usage`, {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setUsageData(data)
      }
    } catch (error) {
      console.error('Error fetching usage data:', error)
    }
  }

  const classifyEmails = async () => {
    setIsClassifying(true)
    setError(null)
    
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/emails/classify`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })
      
      const data = await response.json()
      
      if (response.ok) {
        setClassificationData(data)
        setHasClassified(true)
        // Refresh usage data after classification
        await fetchUsageData()
      } else {
        if (data.limit_reached) {
          setError(`Daily limit of ${data.daily_limit} emails reached. Please try again tomorrow.`)
        } else {
          setError(data.error || 'Failed to classify emails')
        }
      }
    } catch (error) {
      console.error('Error classifying emails:', error)
      setError('Network error. Please check if the backend is running.')
    } finally {
      setIsClassifying(false)
    }
  }
  
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }
  
  if (!isAuthenticated) {
    return null // Will redirect via useEffect
  }
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <button 
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg"
          >
            Logout
          </button>
        </div>
      </div>
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">🎉 Welcome to Inbox Clarity!</h2>
          <p className="text-gray-600">
            AI-powered email classification for your Gmail inbox
          </p>
        </div>

        {/* Usage Statistics */}
        {usageData && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-lg font-semibold mb-4">Daily Usage</h3>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Emails processed today:</span>
              <span className="font-semibold">{usageData.daily_processed} / {usageData.daily_limit}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(usageData.daily_processed / usageData.daily_limit) * 100}%` }}
              ></div>
            </div>
            <p className="text-sm text-gray-500 mt-2">
              {usageData.remaining} emails remaining today
            </p>
          </div>
        )}

        {/* Classification Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="text-center">
            <h3 className="text-xl font-semibold mb-4">Email Classification</h3>
            
            {!hasClassified && !isClassifying && (
              <div>
                <p className="text-gray-600 mb-6">
                  Click the button below to analyze and classify your last 100 Gmail emails using AI.
                </p>
                <button
                  onClick={classifyEmails}
                  disabled={usageData && usageData.remaining <= 0}
                  className={`px-6 py-3 rounded-lg font-medium transition-colors ${
                    usageData && usageData.remaining <= 0
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {usageData && usageData.remaining <= 0 ? 'Daily Limit Reached' : 'Classify My Emails'}
                </button>
              </div>
            )}

            {isClassifying && (
              <div className="py-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600 mb-2">Analyzing your emails...</p>
                <p className="text-sm text-gray-500">This may take a few moments</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                <p className="text-red-600">{error}</p>
                <button
                  onClick={() => setError(null)}
                  className="mt-2 text-sm text-red-500 underline"
                >
                  Dismiss
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Classification Results */}
        {classificationData && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-xl font-semibold mb-4">Classification Results</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {Object.entries(classificationData.categories).map(([category, count]) => (
                  <CategoryCard 
                    key={category} 
                    category={category} 
                    count={count} 
                  />
                ))}
              </div>
              
              <div className="border-t pt-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">{classificationData.total_processed}</div>
                    <div className="text-sm text-gray-600">Emails Processed</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">{classificationData.unread_count}</div>
                    <div className="text-sm text-gray-600">Unread Emails</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-600">
                      {Object.keys(classificationData.categories).length}
                    </div>
                    <div className="text-sm text-gray-600">Categories</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="text-center">
              <button
                onClick={classifyEmails}
                disabled={isClassifying || (usageData && usageData.remaining <= 0)}
                className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                  isClassifying || (usageData && usageData.remaining <= 0)
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {isClassifying ? 'Processing...' : 'Classify Again'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

const Privacy = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-2xl font-bold text-gray-900">Privacy Policy</h1>
      <p className="text-gray-600">Privacy information will go here.</p>
    </div>
  </div>
)

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/auth/callback" element={<OAuthCallback />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/privacy" element={<Privacy />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
