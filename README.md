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
- A Google Cloud Console project with Gmail API enabled
- A Google Cloud project with Google Gemini API access
- A Supabase account and project

## Setup Instructions

Follow these steps to get the project up and running on your local machine.

### 1. Environment Configuration

Sensitive information and API keys are managed via environment variables. You will need to create `.env` files in both the `backend/` and `frontend/` directories. **Never commit your actual `.env` files to version control.**

#### Backend (`backend/.env`)
Copy `backend/.env.example` to `backend/.env` and fill in your actual values:
```
# Google OAuth Credentials: Obtain these from Google Cloud Console (see "Google Cloud Setup" below)
GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET

# Google Gemini API Key: Obtain this from Google AI Studio (see "Google Cloud Setup" below)
GEMINI_API_KEY=YOUR_GEMINI_API_KEY

# Supabase Configuration: Obtain these from your Supabase project settings (see "Database Setup" below)
SUPABASE_URL=YOUR_SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY

# Security Keys:
# SECRET_KEY: A strong, random string for Flask session management. You can generate one using `secrets.token_hex(32)`.
SECRET_KEY=your-secret-key-here
# ENCRYPTION_KEY: A Fernet key for encrypting OAuth tokens. If left empty, the backend will generate one at startup (for development only). For production, generate a strong key using `Fernet.generate_key().decode()`.
ENCRYPTION_KEY=your-encryption-key-here

# Development Settings (optional)
FLASK_ENV=development
FLASK_DEBUG=True
```

#### Frontend (`frontend/.env`)
Copy `frontend/.env.example` to `frontend/.env` and fill in your actual values:
```
# API URL: The URL where your backend Flask application is running.
VITE_API_URL=http://localhost:5000

# Supabase Configuration (for frontend): Obtain these from your Supabase project settings (see "Database Setup" below)
VITE_SUPABASE_URL=YOUR_SUPABASE_URL
VITE_SUPABASE_ANON_KEY=YOUR_SUPABASE_ANON_KEY
```

### 2. Database Setup (Supabase)

1.  **Create a new Supabase project**: Go to [Supabase](https://supabase.com/) and create a new project.
2.  **Get your Supabase URL and Keys**:
    *   Navigate to `Project Settings` -> `API`.
    *   Copy your `Project URL` (this is `YOUR_SUPABASE_URL`).
    *   Copy your `service_role` key (this is `YOUR_SUPABASE_SERVICE_ROLE_KEY`).
    *   Copy your `anon` (public) key (this is `YOUR_SUPABASE_ANON_KEY`).
3.  **Run the SQL schema**:
    *   In your Supabase project dashboard, go to `SQL Editor`.
    *   Open the `database_schema.sql` file from this repository.
    *   Copy the contents of `database_schema.sql` and paste it into the Supabase SQL editor.
    *   Run the query to create the necessary `users` table.

### 3. Google Cloud Setup

You need to set up a Google Cloud Project to obtain OAuth 2.0 credentials for Gmail access and an API key for Google Gemini.

1.  **Go to Google Cloud Console**: Visit [https://console.cloud.google.com/](https://console.cloud.google.com/).
2.  **Create or Select a Project**: Create a new project or select an existing one.
3.  **Enable APIs**:
    *   Navigate to `APIs & Services` -> `Enabled APIs & Services`.
    *   Search for and enable:
        *   `Gmail API`
        *   `Google Cloud AI Platform API` (for Gemini)
4.  **Create OAuth 2.0 Credentials (for Gmail)**:
    *   Go to `APIs & Services` -> `Credentials`.
    *   Click `+ CREATE CREDENTIALS` and select `OAuth client ID`.
    *   Application type: `Web application`.
    *   Name: Choose a descriptive name (e.g., "Inbox Clarity Web App").
    *   **Authorized redirect URIs**: Add `http://localhost:5000/auth/callback`. This is crucial for the OAuth flow.
    *   Click `CREATE`. You will be provided with your `Client ID` (`YOUR_GOOGLE_CLIENT_ID`) and `Client Secret` (`YOUR_GOOGLE_CLIENT_SECRET`).
5.  **Get Gemini API Key**:
    *   Go to [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Create a new API key. This will be `YOUR_GEMINI_API_KEY`.

### 4. Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the Flask application:
    ```bash
    python app.py
    ```
    The backend will run on `http://localhost:5000`.

### 5. Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install Node.js dependencies:
    ```bash
    npm install
    ```
3.  Run the React development server:
    ```bash
    npm run dev
    ```
    The frontend will typically run on `http://localhost:5173`.

## Usage

1.  Ensure both the backend and frontend servers are running.
2.  Open your web browser and navigate to `http://localhost:5173`.
3.  Click the "Sign in with Google" button to authenticate.
4.  Grant the necessary permissions for Gmail access.
5.  Once authenticated, click "Classify Emails" to analyze your last 100 emails.
6.  View the categorized breakdown of your inbox.

## Security Notes

-   All API keys and sensitive credentials **must** be stored as environment variables and never hardcoded or committed to version control.
-   OAuth tokens are encrypted before storage in the database.
-   Email content is processed in real-time by the Gemini AI and is not stored long-term on the server.
-   For production deployments, ensure all communications use HTTPS.

## Architecture

```mermaid
graph TD
    A[Frontend (React)] --> B(Backend Flask API)
    B --> C{Google Gmail API}
    B --> D{Google Gemini AI}
    B --> E[Supabase Database]
```

## Free Tier Limits

-   The application is configured to process a maximum of 100 emails per day per user in the free tier.
-   Usage counts reset at midnight UTC.
-   Future releases may include options for upgrading or custom limits.

## Contributing

We welcome contributions to Inbox Clarity! To contribute:

1.  **Fork** the repository on GitHub.
2.  **Clone** your forked repository to your local machine.
3.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `git checkout -b bugfix/issue-description`.
4.  **Make your changes**, adhering to the existing code style and conventions.
5.  **Test thoroughly** to ensure your changes work as expected and don't introduce regressions.
6.  **Commit your changes** with a clear and concise commit message.
7.  **Push your branch** to your forked repository.
8.  **Open a Pull Request** to the `main` branch of the original repository, describing your changes and their benefits.

Please ensure your pull requests are well-documented and easy to review. Thank you for contributing!
