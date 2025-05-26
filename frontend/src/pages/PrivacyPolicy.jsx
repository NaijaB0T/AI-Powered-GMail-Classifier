import React from 'react'
import { Link } from 'react-router-dom'
import { Mail, ArrowLeft } from 'lucide-react'

const PrivacyPolicy = () => {
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
            <Link to="/" className="flex items-center space-x-2 text-primary-600 hover:text-primary-700">
              <ArrowLeft className="h-5 w-5" />
              <span>Back to Home</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="card">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Privacy Policy</h1>
          
          <div className="prose prose-gray max-w-none">
            <h2 className="text-2xl font-semibold mb-4">Data We Access</h2>
            <p className="mb-4">
              Inbox Clarity accesses the following data from your Gmail account:
            </p>
            <ul className="list-disc pl-6 mb-6">
              <li>Email metadata (subject, sender, date)</li>
              <li>Email snippets (first ~100-160 characters of email body)</li>
              <li>Read/unread status of emails</li>
              <li>Your basic profile information (name, email address)</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">How We Use Your Data</h2>
            <p className="mb-4">
              Your email data is used solely for classification purposes:
            </p>
            <ul className="list-disc pl-6 mb-6">
              <li>Email content is sent to Google's Gemini AI for categorization</li>
              <li>We store your user account information and usage statistics</li>
              <li>We do NOT store your email content long-term</li>
              <li>Processing is done in real-time and email content is not retained</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Data Security</h2>
            <p className="mb-4">
              We take data security seriously:
            </p>
            <ul className="list-disc pl-6 mb-6">
              <li>All communications are encrypted using HTTPS</li>
              <li>OAuth tokens are encrypted before storage</li>
              <li>We use Google's secure OAuth 2.0 authentication</li>
              <li>No passwords are stored on our servers</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Third-Party Services</h2>
            <p className="mb-4">
              Inbox Clarity uses the following third-party services:
            </p>
            <ul className="list-disc pl-6 mb-6">
              <li><strong>Google Gmail API:</strong> To access your email data</li>
              <li><strong>Google Gemini AI:</strong> To classify your emails</li>
              <li><strong>Supabase:</strong> To store user account and usage data</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Your Rights</h2>
            <p className="mb-4">
              You have the following rights regarding your data:
            </p>
            <ul className="list-disc pl-6 mb-6">
              <li>You can revoke access to your Gmail account at any time</li>
              <li>You can request deletion of your account data</li>
              <li>You can view what data we have stored about you</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Data Retention</h2>
            <p className="mb-4">
              We retain minimal data:
            </p>
            <ul className="list-disc pl-6 mb-6">
              <li>User account information (for login purposes)</li>
              <li>Usage statistics (for free tier limits)</li>
              <li>Email content is processed in real-time and not stored</li>
            </ul>

            <h2 className="text-2xl font-semibold mb-4">Contact</h2>
            <p className="mb-4">
              If you have questions about this privacy policy or your data, 
              please contact us through our support channels.
            </p>

            <p className="text-sm text-gray-500 mt-8">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>
        </div>
      </main>
    </div>
  )
}

export default PrivacyPolicy
