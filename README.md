# Inbox Clarity - AI-Powered Gmail Classifier

A web application that helps users understand their email inbox composition by automatically classifying emails using Google's Gemini AI. Built with Flask (backend) and React (frontend).

## Features

- **Google OAuth Authentication**: Secure login with Google accounts
- **Gmail Integration**: Fetches last 100 emails from user's inbox
- **AI Classification**: Uses Google Gemini to categorize emails into 8 categories:
  - Personal
  - Work
  - Bank/Finance
  - Promotions/Ads
  - Notifications
  - Travel
  - Shopping
  - Social Media
- **Freemium Model**: 100 emails per day for free users
- **Real-time Processing**: Emails are classified on-demand
- **Privacy-First**: Email content is processed but not stored long-term

## Tech Stack

- **Backend**: Flask, Google APIs, Supabase
- **Frontend**: React, Vite, Tailwind CSS
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini API
- **Authentication**: Google OAuth 2.0

## Prerequisites

- Python 3.8+
- Node.js 18+
- Google Cloud Console project with Gmail API enabled
- Supabase account
- Google Gemini API access

## Setup Instructions

### 1. Environment Configuration

#### Backend (.env)
Copy `backend/.env.example` to `backend/.env` and fill in:
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GEMINI_API_KEY=your-gemini-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-key
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

#### Frontend (.env)
Copy `frontend/.env.example` to `frontend/.env` and fill in:
```
VITE_API_URL=http://localhost:5000
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 2. Database Setup

1. Create a new Supabase project
2. Run the SQL from `database_schema.sql` in your Supabase SQL editor
3. This will create the required tables and indexes

### 3. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API and Google Cloud AI Platform API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:5000/auth/callback`
5. Get Gemini API key from Google AI Studio

### 4. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

The backend will run on `http://localhost:5000`

### 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:5173`

## Usage

1. Open `http://localhost:5173` in your browser
2. Click "Sign in with Google"
3. Grant permissions for Gmail access
4. Click "Classify Emails" to analyze your last 100 emails
5. View the breakdown by category

## Security Notes

- All API keys must be stored as environment variables
- OAuth tokens are encrypted before storage
- Email content is processed in real-time and not stored
- All communications use HTTPS in production

## Architecture

```
Frontend (React) ← → Backend (Flask) ← → Gmail API
                         ↓
                   Supabase Database
                         ↓
                   Google Gemini AI
```

## Free Tier Limits

- 100 emails processed per day per user
- Usage resets at midnight UTC
- Upgrade options planned for future releases

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
