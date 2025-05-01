# Testing Guide

This document provides instructions for verifying that your deployment is working correctly and performing tests on the application.

## Verifying Deployment Status

### 1. Verify Supabase

1. Log in to your [Supabase Dashboard](https://app.supabase.com/)
2. Select your project
3. Check the following:
   - **Database**: Go to "Table Editor" and verify that your tables are created
   - **Storage**: Go to "Storage" and verify that the "uploads" bucket exists
   - **API**: Go to "API" and verify that your API keys are active

### 2. Verify Railway

1. Log in to your [Railway Dashboard](https://railway.app/)
2. Select your project
3. Check the following for each service:
   - **API Service**:
     - Status should be "Deployed" (green)
     - Check logs for any errors
     - Verify the service URL is accessible by opening it in a browser (you should see the API welcome message)
   - **Worker Service**:
     - Status should be "Deployed" (green)
     - Check logs for any errors
   - **Redis**:
     - Status should be "Deployed" (green)

### 3. Verify Vercel

1. Log in to your [Vercel Dashboard](https://vercel.com/)
2. Select your project
3. Check the following:
   - Deployment status should be "Ready"
   - Check build logs for any errors
   - Verify the deployment URL is accessible by opening it in a browser

## Testing the Application

### 1. Frontend Tests

1. **Access the Application**:
   - Open your Vercel deployment URL in a browser
   - Verify that the login page loads correctly

2. **User Authentication**:
   - Create a new account or log in with an existing account
   - Verify that you can log in successfully
   - Check that you're redirected to the dashboard

3. **Navigation**:
   - Navigate through different pages (Dashboard, Upload, Historical, etc.)
   - Verify that all pages load correctly
   - Check that the navigation menu works

4. **Responsive Design**:
   - Test the application on different devices (desktop, tablet, mobile)
   - Verify that the layout adjusts correctly

### 2. Backend API Tests

1. **API Endpoints**:
   - While logged in to the frontend, open your browser's developer tools
   - Go to the Network tab
   - Navigate through different pages and verify that API requests are successful (status 200)

2. **Authentication**:
   - Log out and try to access a protected page
   - Verify that you're redirected to the login page

### 3. File Upload Tests

1. **Upload a File**:
   - Go to the Upload page
   - Select a CSV file with Shopify order data
   - Click the upload button
   - Verify that the upload progress is displayed
   - Wait for the upload to complete
   - Verify that you're redirected to the appropriate page

2. **Verify Storage**:
   - Log in to your Supabase Dashboard
   - Go to "Storage" → "uploads"
   - Verify that your uploaded file appears in the bucket

3. **Verify Processing**:
   - Go to the Historical page
   - Verify that your uploaded file appears in the list
   - Check that the status is "completed"

4. **Verify Analytics**:
   - Go to the Dashboard page
   - Verify that the data from your uploaded file is displayed in the charts and tables

### 4. End-to-End Test Scenario

Here's a complete test scenario to verify all components are working together:

1. Log in to the application
2. Upload a CSV file with Shopify order data
3. Monitor the upload progress
4. Once complete, navigate to the Dashboard
5. Verify that the data is displayed correctly
6. Go to the Historical page and check that the upload is listed
7. Go to the Projections page and verify that forecasts are generated
8. Log out and verify that you're redirected to the login page

## Monitoring and Logs

### 1. Railway Logs

1. Go to your Railway Dashboard
2. Select your project
3. Click on the API service
4. Go to the "Logs" tab
5. Monitor for any errors or warnings

### 2. Vercel Logs

1. Go to your Vercel Dashboard
2. Select your project
3. Go to the "Deployments" tab
4. Click on the latest deployment
5. Go to the "Logs" tab
6. Monitor for any errors or warnings

### 3. Supabase Logs

1. Go to your Supabase Dashboard
2. Select your project
3. Go to "Database" → "API"
4. Check the "Realtime" tab for live database activity
5. Go to "Storage" → "Logs" to monitor file operations

## Troubleshooting Common Issues

### 1. Frontend Issues

- **Blank Page**: Check browser console for JavaScript errors
- **API Connection Errors**: Verify that `NEXT_PUBLIC_BACKEND_URL` is set correctly
- **Authentication Errors**: Verify that `NEXTAUTH_SECRET` and `NEXTAUTH_URL` are set correctly

### 2. Backend Issues

- **Database Connection Errors**: Verify that `DATABASE_URL` is correct
- **Supabase Connection Errors**: Verify that `SUPABASE_URL` and `SUPABASE_KEY` are correct
- **Redis Connection Errors**: Verify that Redis environment variables are set correctly

### 3. File Upload Issues

- **Upload Fails**: Check Railway logs for errors
- **Processing Fails**: Verify that the worker service is running
- **File Not Found**: Check Supabase Storage permissions

## Performance Testing

To test the performance of your application:

1. **Upload Large Files**:
   - Test with files of different sizes (1MB, 5MB, 10MB)
   - Monitor the processing time
   - Check Railway logs for any performance issues

2. **Concurrent Users**:
   - Have multiple users access the application simultaneously
   - Monitor Railway and Vercel dashboards for resource usage
   - Check for any performance degradation

## Security Testing

1. **Authentication**:
   - Try accessing protected routes without logging in
   - Verify that authentication tokens expire correctly
   - Test password reset functionality

2. **API Security**:
   - Verify that API endpoints require authentication
   - Check that users can only access their own data

3. **Storage Security**:
   - Verify that users can only access their own files
   - Check that file URLs are signed and expire

## Continuous Monitoring

Once your application is live, set up continuous monitoring:

1. **Set Up Alerts**:
   - Configure Railway alerts for service downtime
   - Set up Vercel alerts for deployment failures
   - Configure Supabase alerts for database issues

2. **Regular Backups**:
   - Verify that Supabase automatic backups are enabled
   - Consider setting up additional backup solutions

3. **Usage Monitoring**:
   - Regularly check Railway, Vercel, and Supabase dashboards for usage metrics
   - Monitor for approaching free tier limits
