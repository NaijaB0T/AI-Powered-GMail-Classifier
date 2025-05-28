Inbox Clarity is an AI-powered web app that classifies Gmail emails using Google Gemini AI. Built with Flask and React, it helps users understand inbox composition, offering features like Google OAuth, email fetching, and a dashboard. It operates on a freemium model with privacy-first design.

"Inbox Clarity" is a web application designed to help users efficiently understand and manage their email inboxes by leveraging artificial intelligence. It automatically classifies emails using Google's Gemini AI, providing a clear overview of inbox composition. The project is built as a Minimum Viable Product (MVP) with a focus on core functionality, security, and a user-friendly experience.

## Core Problem Solved

Users often face cluttered inboxes, making it time-consuming to manually sort and prioritize emails. "Inbox Clarity" addresses this by offering an automated solution to categorize emails, providing a "bird's-eye view" of their email landscape and saving valuable time.

## Key Features

*   **Google OAuth Authentication**: Secure user login and authorization via Google accounts, ensuring safe access to Gmail data.
*   **Gmail Integration**: Fetches the last 100 emails from the user's primary inbox for classification.
*   **AI-Powered Classification**: Utilizes the Google Gemini API to categorize emails into 8 predefined categories: Personal, Work, Bank/Finance, Promotions/Ads, Notifications, Travel, Shopping, and Social Media.
*   **Intuitive Dashboard**: Presents a clean and responsive dashboard displaying the count of emails in each category, offering a quick visual summary of the inbox.
*   **Freemium Model**: Implements a daily processing limit of 100 emails for free users, with clear communication of this limit.
*   **Privacy-First Design**: Emphasizes secure handling of sensitive data, with OAuth tokens encrypted and email content processed in real-time without long-term storage.

## Technical Stack

The application is developed with a robust and modern tech stack:

*   **Backend**: Flask (Python) for handling API requests, Google OAuth callbacks, Gmail API integration, and Gemini AI classification.
*   **Frontend**: React, built with Vite for fast development and bundled with Tailwind CSS for a streamlined, responsive UI.
*   **Database**: Supabase (PostgreSQL) for user management, token storage, and tracking daily email processing limits.
*   **AI**: Google Gemini API for advanced email content analysis and categorization.
*   **Authentication**: Google OAuth 2.0 for secure and seamless user authentication.

## Architecture

The system follows a client-server architecture:
Frontend (React) communicates with the Backend (Flask), which in turn interacts with the Gmail API, Supabase Database, and Google Gemini AI for email fetching, data storage, and classification, respectively.

## Security and Performance

The project prioritizes security with encrypted token storage, strict use of environment variables for sensitive keys, and adherence to web security best practices. Performance is optimized for efficient API calls and provides clear progress indicators during email processing.

"Inbox Clarity" is a production-ready MVP, offering a valuable tool for anyone seeking to gain clarity and control over their email inbox.
