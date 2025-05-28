import os
import json
import base64
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import google.generativeai as genai
from supabase.client import create_client, Client
import logging
from cryptography.fernet import Fernet
import secrets
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, wait_exponential
from google.api_core import exceptions
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Custom wait strategy for ResourceExhausted errors
def wait_exponential_from_exception(retry_state):
    exc = retry_state.outcome.exception()
    if isinstance(exc, exceptions.ResourceExhausted) and exc.details:
        try:
            # Attempt to parse the retry_delay from the exception details
            # The details string format is like: "...retry_delay { seconds: 59 }..."
            # This is a simple regex to extract the seconds value
            import re
            match = re.search(r"retry_delay {\s*seconds: (\d+)\s*}", str(exc.details))
            if match:
                delay = int(match.group(1))
                logger.info(f"ResourceExhausted: Waiting for {delay} seconds before retrying.")
                return delay
        except Exception as e:
            logger.warning(f"Could not parse retry_delay from exception details: {e}. Falling back to exponential wait.")
    # Fallback to default exponential wait if delay not found or not ResourceExhausted
    return wait_exponential(multiplier=1, min=4, max=60)(retry_state)

# Import configuration
from config import config

# Allow insecure transport for OAuth 2 during local development
# WARNING: Do NOT use this in production!
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Configure session for cross-origin requests
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # Allow cross-origin requests
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)

# Enable CORS for frontend
CORS(app, origins=['http://localhost:5173', 'http://localhost:5174', 'http://localhost:5175'], supports_credentials=True)

# Configuration from environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# Validate required environment variables
if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    logger.error("Missing required Google OAuth credentials")
    raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required")

if not GEMINI_API_KEY:
    logger.error("Missing required Gemini API key")
    raise ValueError("GEMINI_API_KEY environment variable is required")

if not SUPABASE_SERVICE_KEY:
    logger.error("Missing required Supabase Service Key")
    raise ValueError("SUPABASE_SERVICE_KEY environment variable is required")

if not SUPABASE_URL:
    logger.error("Missing required Supabase URL")
    raise ValueError("SUPABASE_URL environment variable is required")

logger.info("Successfully loaded environment variables")
import base64

ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Generate a new Fernet key if none provided
    ENCRYPTION_KEY = Fernet.generate_key()
    logger.warning("No ENCRYPTION_KEY provided, generated a new one")
else:
    # Convert string to Fernet-compatible key
    try:
        # Create a consistent key from the provided string
        import hashlib
        key_bytes = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()
        ENCRYPTION_KEY = base64.urlsafe_b64encode(key_bytes)
        logger.info("Successfully configured encryption key")
    except Exception as e:
        logger.error(f"Error setting up encryption key: {e}")
        # Fallback to generating a new key
        ENCRYPTION_KEY = Fernet.generate_key()
        logger.warning("Fallback to generated encryption key")

# Initialize services
genai.configure(api_key=GEMINI_API_KEY) # Use the standard configure method
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
cipher_suite = Fernet(ENCRYPTION_KEY)

# Email classification categories
CATEGORIES = [
    "Personal", "Work", "Bank/Finance", "Promotions/Ads", 
    "Notifications", "Travel", "Shopping", "Social Media"
]

DAILY_FREE_LIMIT = 100

# Get API timeout from config
API_TIMEOUT = config['default'].API_TIMEOUT

class EmailClassifier:
    def __init__(self):
        # Updated to use the current Gemini model
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Use gemini-1.5-flash instead of gemini-pro
    
    @retry(
        stop=stop_after_attempt(5), # Increased attempts for quota errors
        wait=wait_exponential_from_exception, # Use custom wait strategy
        retry=retry_if_exception_type(exceptions.ResourceExhausted) # Only retry on ResourceExhausted
    )
    def classify_email(self, subject, sender, snippet):
        """Classify email using Gemini API with retry logic and timeout"""
        prompt = f"""
        Classify the following email content into one of these categories: {', '.join(CATEGORIES)}.
        
        Email Subject: '{subject}'
        Sender: '{sender}'
        Body Snippet: '{snippet}'
        
        Categories:
        - Personal: Emails from friends, family, personal contacts
        - Work: Professional correspondence, project updates, company-wide emails
        - Bank/Finance: Statements, transaction alerts, financial updates
        - Promotions/Ads: Marketing emails, newsletters, sales offers
        - Notifications: System alerts, app notifications (non-social media), reminders
        - Travel: Flight confirmations, hotel bookings, rental car reservations
        - Shopping: Order confirmations, shipping updates, receipts from online purchases
        - Social Media: Notifications from Facebook, Instagram, Twitter, LinkedIn, etc.
        
        Respond with only the category name.
        """
        
        # Log the email being classified
        logger.info(f"Classifying email - Subject: {subject[:50]}, Sender: {sender[:50]}")
        
        response = self.model.generate_content(prompt, request_options={'timeout': API_TIMEOUT})
        category = response.text.strip()
        
        # Log Gemini's response
        logger.info(f"Gemini response: '{category}'")
        
        # Validate category
        if category in CATEGORIES:
            return category
        else:
            # Log when defaulting
            logger.warning(f"Invalid category '{category}' from Gemini, defaulting to Notifications")
            return "Notifications"

classifier = EmailClassifier()

def encrypt_token(token):
    """Encrypt OAuth token for secure storage"""
    return cipher_suite.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token):
    """Decrypt OAuth token"""
    return cipher_suite.decrypt(encrypted_token.encode()).decode()

def get_user_data(user_id):
    """Get user data from Supabase"""
    try:
        result = supabase.table('users').select('*').eq('user_id', user_id).execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        logger.error(f"Error getting user data: {e}")
        return None

def update_user_usage(user_id, processed_count):
    """Update user's daily usage count"""
    try:
        today = datetime.now().date().isoformat()
        user_data = get_user_data(user_id)
        
        if user_data:
            # Check if it's a new day
            if user_data.get('last_processed_date') != today:
                # Reset count for new day
                supabase.table('users').update({
                    'daily_processed_count': processed_count,
                    'last_processed_date': today
                }).eq('user_id', user_id).execute()
            else:
                # Update existing count
                new_count = user_data.get('daily_processed_count', 0) + processed_count
                supabase.table('users').update({
                    'daily_processed_count': new_count
                }).eq('user_id', user_id).execute()
        else:
            # Create new user record
            supabase.table('users').insert({
                'user_id': user_id,
                'daily_processed_count': processed_count,
                'last_processed_date': today
            }).execute()
            
    except Exception as e:
        logger.error(f"Error updating user usage: {e}")

def check_daily_limit(user_id):
    """Check if user has exceeded daily limit"""
    try:
        today = datetime.now().date().isoformat()
        user_data = get_user_data(user_id)
        
        if not user_data:
            return True  # New user, allow processing
        
        if user_data.get('last_processed_date') != today:
            return True  # New day, allow processing
        
        current_count = user_data.get('daily_processed_count', 0)
        return current_count < DAILY_FREE_LIMIT
        
    except Exception as e:
        logger.error(f"Error checking daily limit: {e}")
        return False

@app.route('/auth/google')
def google_auth():
    """Initiate Google OAuth flow"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:5000/auth/callback"]
                }
            },
            scopes=[
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/gmail.readonly',
                'openid',
                'https://www.googleapis.com/auth/userinfo.email'
            ]
        )
        flow.redirect_uri = url_for('auth_callback', _external=True)
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        session['state'] = state
        return jsonify({'auth_url': authorization_url})
        
    except Exception as e:
        logger.error(f"Error initiating Google auth: {e}")
        return jsonify({'error': 'Failed to initiate authentication'}), 500

@app.route('/')
def index():
    return("Welcome To Backend")

@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback"""
    try:
        logger.info("OAuth callback received")
        logger.info(f"Request args: {dict(request.args)}")
        
        # Check if we have the expected parameters
        if 'code' not in request.args:
            logger.error("No authorization code received")
            return redirect('http://localhost:5173/auth/callback?error=no_code')
        
        # Verify state parameter if present
        received_state = request.args.get('state')
        expected_state = session.get('state')
        
        logger.info(f"State verification - received: {received_state}, expected: {expected_state}")
        
        if received_state and expected_state and received_state != expected_state:
            logger.error(f"State mismatch: expected {expected_state}, got {received_state}")
            return redirect('http://localhost:5173/auth/callback?error=state_mismatch')
        
        # Create OAuth flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:5000/auth/callback"]
                }
            },
            scopes=[
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/gmail.readonly',
                'openid',
                'https://www.googleapis.com/auth/userinfo.email'
            ]
        )
        flow.redirect_uri = url_for('auth_callback', _external=True)
        
        # Get authorization code and exchange for token
        authorization_response = request.url
        logger.info(f"Authorization response URL: {authorization_response}")
        
        token_response = flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        logger.info("Successfully obtained credentials from Google")
        logger.info(f"Token response keys: {list(token_response.keys())}")
        
        # Build the OAuth2 service to get user info
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        user_email = "authenticated_user@example.com"  # Default fallback
        user_id = "google_authenticated_user"  # Default fallback
        
        try:
            # Get user info from the ID token
            id_token_str = token_response.get('id_token')
            if id_token_str:
                idinfo = id_token.verify_oauth2_token(
                    id_token_str, 
                    google_requests.Request(), 
                    GOOGLE_CLIENT_ID
                )
                
                user_email = idinfo.get('email', user_email)
                user_id = idinfo.get('sub', user_id)  # Google's unique user ID
                logger.info(f"User authenticated: {user_email}")
            else:
                logger.warning("No ID token found, using fallback user info")
            
        except Exception as e:
            logger.error(f"Error verifying ID token: {e}")
            logger.info("Using fallback user identification")
        
        # Store user info in session
        session.permanent = True
        session['user_id'] = user_id
        session['user_email'] = user_email
        session['access_token'] = credentials.token
        
        if credentials.refresh_token:
            session['refresh_token'] = encrypt_token(credentials.refresh_token)
            logger.info("Refresh token stored successfully")
        else:
            logger.warning("No refresh token received from Google")
        
        # Clear the state from session
        session.pop('state', None)
        
        logger.info(f"Session after auth: user_id={session.get('user_id')}, email={session.get('user_email')}")
        
        # Redirect to frontend OAuth callback route
        return redirect('http://localhost:5173/auth/callback?success=true')
        
    except Exception as e:
        logger.error(f"Error in auth callback: {e}")
        logger.error(f"Request args: {dict(request.args)}")
        logger.error(f"Session state: {session.get('state', 'No state in session')}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return redirect('http://localhost:5173/auth/callback?error=auth_failed')

@app.route('/api/user/status')
def user_status():
    """Get current user authentication status"""
    try:
        if 'user_id' not in session:
            return jsonify({'authenticated': False})
        
        return jsonify({'authenticated': True})
        
    except Exception as e:
        logger.error(f"Error checking user status: {e}")
        return jsonify({'authenticated': False})

@app.route('/api/emails/classify', methods=['POST'])
def classify_emails():
    """Fetch and classify user's Gmail emails"""
    try:
        logger.info(f"Classify emails request received")
        logger.info(f"Session keys: {list(session.keys())}")
        logger.info(f"User ID in session: {session.get('user_id', 'NOT SET')}")
        logger.info(f"Refresh token in session: {'refresh_token' in session}")
        
        if 'user_id' not in session or 'refresh_token' not in session:
            logger.error("Authentication check failed - missing session data")
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        logger.info(f"Processing emails for user: {user_id}")
        
        # Check daily limit
        if not check_daily_limit(user_id):
            logger.info(f"Daily limit reached for user: {user_id}")
            return jsonify({
                'error': 'Daily processing limit reached',
                'limit_reached': True,
                'daily_limit': DAILY_FREE_LIMIT
            }), 429
        
        # Create credentials from stored tokens
        refresh_token = decrypt_token(session['refresh_token'])
        logger.info("Successfully decrypted refresh token")
        
        # Create credentials from stored tokens
        refresh_token = decrypt_token(session['refresh_token'])
        logger.info("Successfully decrypted refresh token")
        
        credentials = Credentials(
            token=None,  # We'll refresh to get a new access token
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET
        )
        
        # Refresh token to get access token
        logger.info("Refreshing credentials...")
        try:
            credentials.refresh(Request())
            logger.info("Successfully refreshed credentials")
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}")
            raise # Re-raise to be caught by outer try-except
        
        # Build Gmail service with a custom http object for timeout
        logger.info("Building Gmail service...")
        # Import httplib2 and create a http object with timeout
        service = build('gmail', 'v1', credentials=credentials)
        logger.info("Gmail service built successfully")
        
        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
        def fetch_messages_with_retry():
            logger.info("Fetching emails from Gmail with retry...")
            return service.users().messages().list(
                userId='me',
                maxResults=100,
                labelIds=['INBOX']
            ).execute()

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
        def get_message_with_retry(message_id):
            logger.info(f"Getting message {message_id} with retry...")
            return service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['Subject', 'From']
            ).execute()

        # Fetch last 100 emails
        results = fetch_messages_with_retry()
        
        messages = results.get('messages', [])
        logger.info(f"Found {len(messages)} messages")
        
        if not messages:
            logger.info("No messages found")
            return jsonify({
                'categories': {category: 0 for category in CATEGORIES},
                'total_processed': 0,
                'unread_count': 0
            })

        # Initialize category counts
        category_counts = {category: 0 for category in CATEGORIES}
        unread_count = 0
        processed_count = 0
        
        # Process each email
        logger.info("Starting email classification...")
        # Log first 5 emails for debugging
        sample_emails = []
        
        for i, message in enumerate(messages):
            try:
                logger.info(f"Processing message {i+1}/{len(messages)}")
                
                msg = get_message_with_retry(message['id'])
                
                # Extract email data
                headers = msg['payload'].get('headers', [])
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                
                # Get snippet
                snippet = msg.get('snippet', '')
                
                # Store sample for debugging
                if i < 5:
                    sample_emails.append({
                        'subject': subject,
                        'sender': sender,
                        'snippet': snippet[:100] + '...' if len(snippet) > 100 else snippet
                    })
                
                # Check if unread
                if 'UNREAD' in msg.get('labelIds', []):
                    unread_count += 1
                
                # Classify email
                logger.info(f"Classifying email: {subject[:50]}...")
                category = classifier.classify_email(subject, sender, snippet)
                category_counts[category] += 1
                processed_count += 1
                
                logger.info(f"Email classified as: {category}")
                
                # Break if we hit the daily limit
                if processed_count >= DAILY_FREE_LIMIT:
                    break
                    
            except Exception as e:
                logger.error(f"Error processing message {message['id']}: {e}")
                # Log the full traceback for more detailed error information
                import traceback
                logger.error(f"Full traceback for message {message['id']}: {traceback.format_exc()}")
                continue
        
        # Log sample emails for debugging
        logger.info(f"Sample of processed emails: {json.dumps(sample_emails, indent=2)}")
        logger.info(f"Classification complete. Processed {processed_count} emails")
        
        # Update user usage
        update_user_usage(user_id, processed_count)
        
        result = {
            'categories': category_counts,
            'total_processed': processed_count,
            'unread_count': unread_count,
            'daily_limit': DAILY_FREE_LIMIT
        }
        
        logger.info(f"Returning result: {result}")
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error classifying emails: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Failed to classify emails', 'details': str(e)}), 500

@app.route('/api/user/usage')
def user_usage():
    """Get user's current usage statistics"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user_id = session['user_id']
        user_data = get_user_data(user_id)
        
        today = datetime.now().date().isoformat()
        
        if not user_data or user_data.get('last_processed_date') != today:
            daily_count = 0
        else:
            daily_count = user_data.get('daily_processed_count', 0)
        
        return jsonify({
            'daily_processed': daily_count,
            'daily_limit': DAILY_FREE_LIMIT,
            'remaining': DAILY_FREE_LIMIT - daily_count
        })
        
    except Exception as e:
        logger.error(f"Error getting user usage: {e}")
        return jsonify({'error': 'Failed to get usage data'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    session.clear()
    return jsonify({'success': True})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'google_oauth_configured': bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
        'gemini_configured': bool(GEMINI_API_KEY),
        'encryption_configured': bool(ENCRYPTION_KEY)
    })

@app.route('/debug/session')
def debug_session():
    """Debug endpoint to check session state"""
    return jsonify({
        'session_id': request.cookies.get('session'),
        'has_user_id': 'user_id' in session,
        'has_refresh_token': 'refresh_token' in session,
        'user_id': session.get('user_id', 'Not set'),
        'user_email': session.get('user_email', 'Not set'),
        'session_keys': list(session.keys()),
        'permanent': session.permanent
    })

@app.route('/debug/test-classifier', methods=['POST'])
def test_classifier():
    """Debug endpoint to test Gemini classifier"""
    try:
        data = request.get_json()
        subject = data.get('subject', 'Test Subject')
        sender = data.get('sender', 'test@example.com')
        snippet = data.get('snippet', 'This is a test email')
        
        # Test the classifier
        result = classifier.classify_email(subject, sender, snippet)
        
        # Also test with some predefined examples
        test_cases = [
            {
                'subject': 'Your Amazon order has shipped',
                'sender': 'shipment-tracking@amazon.com',
                'snippet': 'Your order #123-456 has been shipped and will arrive tomorrow'
            },
            {
                'subject': 'Your bank statement is ready',
                'sender': 'notifications@bankofamerica.com',
                'snippet': 'Your monthly statement for account ending in 1234 is now available'
            },
            {
                'subject': 'Meeting tomorrow at 3pm',
                'sender': 'john.doe@company.com',
                'snippet': 'Hi, just a reminder about our project meeting tomorrow at 3pm'
            },
            {
                'subject': '50% off everything this weekend!',
                'sender': 'deals@store.com',
                'snippet': 'Don\'t miss our biggest sale of the year - 50% off all items'
            }
        ]
        
        test_results = []
        for test in test_cases:
            category = classifier.classify_email(test['subject'], test['sender'], test['snippet'])
            test_results.append({
                'subject': test['subject'],
                'expected_category': 'Shopping' if 'Amazon' in test['subject'] else 
                                   'Bank/Finance' if 'bank' in test['subject'] else
                                   'Work' if 'meeting' in test['subject'].lower() else
                                   'Promotions/Ads',
                'actual_category': category
            })
        
        return jsonify({
            'custom_test': {
                'input': {'subject': subject, 'sender': sender, 'snippet': snippet},
                'category': result
            },
            'predefined_tests': test_results
        })
        
    except Exception as e:
        logger.error(f"Error in test classifier: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
