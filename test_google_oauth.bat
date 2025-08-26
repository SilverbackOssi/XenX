@echo off
echo Testing Google OAuth Configuration...
echo.
echo Using the following configuration:
echo -----------------------------------
echo Client ID: %GOOGLE_CLIENT_ID%
echo Redirect URI: %GOOGLE_REDIRECT_URI%
echo.

echo Generating an OAuth URL...
python -c "from app.auth.services.google_oauth_service import GoogleOAuthService; s = GoogleOAuthService(client_id='%GOOGLE_CLIENT_ID%', client_secret='%GOOGLE_CLIENT_SECRET%', redirect_uri='%GOOGLE_REDIRECT_URI%'); print(s.get_auth_url())"
echo.
echo If you see a valid URL above, your configuration is correct.
echo Try visiting this URL in your browser to test Google Sign-In.
echo.
echo NOTE: Make sure the redirect URI is registered in Google Cloud Console.
