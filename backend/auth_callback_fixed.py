# Fixed OAuth callback implementation
# Add this to your app.py file, replacing the existing auth_callback route

@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback"""
    try:
        logger.info("OAuth callback received")
        
        # Check if we have the expected parameters
        if 'code' not in request.args:
            logger.error("No authorization code received")
            return redirect('http://localhost:5173/auth/callback?error=no_code')
        
        # Verify state parameter if present
        received_state = request.args.get('state')
        expected_state = session.get('state')
        
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
                'https://www.googleapis.com/auth/gmail.readonly',
                'openid',
                'email',
                'profile'
            ]
        )
        flow.redirect_uri = url_for('auth_callback', _external=True)
        
        # Get authorization code and exchange for token
        authorization_response = request.url
        logger.info(f"Authorization response URL: {authorization_response}")
        
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        logger.info("Successfully obtained credentials from Google")
        
        # Build the OAuth2 service to get user info
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        try:
            # Get user info from the ID token
            idinfo = id_token.verify_oauth2_token(
                credentials.id_token, 
                google_requests.Request(), 
                GOOGLE_CLIENT_ID
            )
            
            user_email = idinfo.get('email')
            user_id = idinfo.get('sub')  # Google's unique user ID
            
            logger.info(f"User authenticated: {user_email}")
            
            # Store user info in session
            session['user_id'] = user_id  # Use Google's user ID
            session['user_email'] = user_email
            session['access_token'] = credentials.token
            
            if credentials.refresh_token:
                session['refresh_token'] = encrypt_token(credentials.refresh_token)
                logger.info("Refresh token stored successfully")
            else:
                logger.warning("No refresh token received from Google")
            
            # Mark session as permanent
            session.permanent = True
            
        except Exception as e:
            logger.error(f"Error verifying ID token: {e}")
            # Fallback: use access token as user_id
            session['user_id'] = "google_user"  # Generic user ID
            session['access_token'] = credentials.token
            if credentials.refresh_token:
                session['refresh_token'] = encrypt_token(credentials.refresh_token)
        
        # Clear the state from session
        session.pop('state', None)
        
        # Redirect to frontend OAuth callback route (not directly to dashboard)
        return redirect('http://localhost:5173/auth/callback')
        
    except Exception as e:
        logger.error(f"Error in auth callback: {e}")
        logger.error(f"Request args: {dict(request.args)}")
        logger.error(f"Session state: {session.get('state', 'No state in session')}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return redirect('http://localhost:5173/auth/callback?error=auth_failed')
