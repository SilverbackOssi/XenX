# Google OAuth Setup Guide

This document provides detailed instructions for setting up Google OAuth for your local development environment.

## Prerequisites

1. A Google account
2. Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a project" at the top and then "New Project"
3. Enter a project name (e.g., "XenToba Development") and click "Create"
4. Select your new project from the project selector

## Step 2: Configure OAuth Consent Screen

1. In the left sidebar, navigate to "APIs & Services" > "OAuth consent screen"
2. Select "External" as the user type and click "Create"
3. Fill in the required fields:
   - App name: "XenToba Testing"
   - User support email: Your email
   - Developer contact information: Your email
4. Click "Save and Continue"
5. Skip the "Scopes" section by clicking "Save and Continue"
6. Add your email as a test user in the "Test users" section
7. Click "Save and Continue"

## Step 3: Create OAuth Credentials

1. In the left sidebar, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "OAuth client ID"
3. For "Application type", select "Web application"
4. Name: "XenToba Local Development"
5. Add the following to "Authorized JavaScript origins":
   ```
   http://localhost:8000
   ```
6. Add the following to "Authorized redirect URIs":
   ```
   http://localhost:8000/auth/google/callback
   ```
7. Click "Create"
8. A popup will display your Client ID and Client Secret - save these

## Step 4: Update Your .env File

1. Open your `.env` file
2. Update the following values with your new credentials:
   ```
   GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET="your-client-secret"
   GOOGLE_REDIRECT_URI="http://localhost:8000/auth/google/callback"
   ```

## Step 5: Test Your Configuration

1. Run the application: `uvicorn main:app --reload`
2. Go to http://localhost:8000/auth
3. Click "Sign in with Google"
4. You should be redirected to Google's authentication screen
5. After authenticating, you should be redirected back to your application

## Troubleshooting

### Error: redirect_uri_mismatch
- Make sure the redirect URI in your code exactly matches what you've configured in the Google Cloud Console
- Check for any typos, including http vs. https, trailing slashes, etc.
- The URI in your .env file must match what's registered in Google Cloud Console

### Error: invalid_client
- Double-check your client ID and client secret
- Make sure you're using the credentials from the correct project

### Other Issues
- Check the application logs for detailed error messages
- Make sure the Google Cloud API is properly configured
- Ensure your Google account is added as a test user in the OAuth consent screen

## Additional Resources

- [Google OAuth Documentation](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google Cloud Console](https://console.cloud.google.com/)
