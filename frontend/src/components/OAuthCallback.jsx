import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import LoadingSpinner from './LoadingSpinner'

const OAuthCallback = () => {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { checkAuthStatus, isAuthenticated } = useAuth()
  const [processing, setProcessing] = useState(true)

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Check for OAuth errors first
        const error = searchParams.get('error')
        if (error) {
          let errorMessage = 'Authentication failed. Please try again.'
          switch (error) {
            case 'no_code':
              errorMessage = 'No authorization code received from Google.'
              break
            case 'state_mismatch':
              errorMessage = 'Security validation failed. Please try again.'
              break
            case 'auth_failed':
              errorMessage = 'Authentication failed. Please try again.'
              break
            case 'no_state':
              errorMessage = 'Missing security token. Please try again.'
              break
            case 'no_session_state':
              errorMessage = 'Session expired. Please try again.'
              break
            default:
              errorMessage = `Authentication error: ${error}`
          }
          alert(errorMessage)
          navigate('/', { replace: true })
          return
        }

        // Give backend time to set session, then check auth status
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Force refresh auth status
        await checkAuthStatus()
        
        // Small delay to ensure state is updated
        await new Promise(resolve => setTimeout(resolve, 500))
        
      } catch (error) {
        console.error('Error processing OAuth callback:', error)
        alert('Authentication processing failed. Please try again.')
        navigate('/', { replace: true })
      } finally {
        setProcessing(false)
      }
    }

    handleCallback()
  }, [searchParams, navigate, checkAuthStatus])

  // Redirect to dashboard once authenticated
  useEffect(() => {
    if (!processing && isAuthenticated) {
      navigate('/dashboard', { replace: true })
    } else if (!processing && !isAuthenticated) {
      navigate('/', { replace: true })
    }
  }, [processing, isAuthenticated, navigate])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <LoadingSpinner size="lg" />
        <h2 className="text-xl font-semibold text-gray-900 mt-4 mb-2">
          Completing Sign In
        </h2>
        <p className="text-gray-600">
          Please wait while we verify your authentication...
        </p>
      </div>
    </div>
  )
}

export default OAuthCallback
