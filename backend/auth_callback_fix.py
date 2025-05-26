@app.route('/auth/callback')
def auth_callback():
    """Handle Google OAuth callback"""
    try:
        logger.info("OAuth callback received")
        
        # Check if we have the expected parameters
        if 'code' not in request.args:
            logger.error("No authorization code received")
            return redirect('http://localhost:5173/?error=no_code')
        
        if 'state' not in request.args:
            logger.error("No state parameter received")
            return redirect('http://localhost:5173/?error=no_state')
        
        # Verify state parameter
        received_state = request.args.get('state')
        expected_state = session.get('state')
        
        if not expected_state:
            logger.error("No state found in session")
            return redirect('http://localhost:5173/?error=no_session_state')
        
        if received_state != expected_state:
            logger.error(f"State mismatch: expected {expected_state}, got {received_state}")
            return redirect('http://localhost:5173/?error=state_mismatch')
        
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
            ],
            state=expected_state
        )
        flow.redirect_uri = url_for('auth_callback', _external=True)
        
        # Get authorization code and exchange for token
        authorization_response = request.url
        logger.info(f"Authorization response URL: {authorization_response}")
        
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        
        logger.info("Successfully obtained credentials from Google")
        
        # Store encrypted refresh token in session
        session['user_id'] = credentials.token
        if credentials.refresh_token:
            session['refresh_token'] = encrypt_token(credentials.refresh_token)
            logger.info("Refresh token stored successfully")
        else:
            logger.warning("No refresh token received from Google")
        
        # Clear the state from session
        session.pop('state', None)
        
        # Redirect to frontend dashboard
        return redirect('http://localhost:5173/dashboard')
        
    except Exception as e:
        logger.error(f"Error in auth callback: {e}")
        logger.error(f"Request args: {dict(request.args)}")
        logger.error(f"Session contents: {dict(session)}")
        return redirect('http://localhost:5173/?error=auth_failed')
