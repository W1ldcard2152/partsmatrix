@echo off
echo eBay Marketplace Account Deletion Compliance Setup
echo ================================================

echo.
echo This script will help you set up eBay marketplace account deletion compliance.
echo.

echo Step 1: Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ERROR: Failed to run migrations
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up eBay notification configuration...
echo.

set /p domain="Enter your domain (e.g., yourdomain.com): "
if "%domain%"=="" (
    echo ERROR: Domain cannot be empty
    pause
    exit /b 1
)

set endpoint_url=https://%domain%/ebay/marketplace-account-deletion/

echo.
echo Your endpoint URL will be: %endpoint_url%
echo.

choice /c YN /m "Generate a random verification token? (Y/N)"
if %errorlevel%==1 (
    python manage.py setup_ebay_notifications --endpoint-url %endpoint_url% --generate-token
) else (
    set /p token="Enter your verification token (32-80 characters): "
    if "%token%"=="" (
        echo ERROR: Token cannot be empty
        pause
        exit /b 1
    )
    python manage.py setup_ebay_notifications --endpoint-url %endpoint_url% --verification-token %token%
)

if %errorlevel% neq 0 (
    echo ERROR: Failed to set up configuration
    pause
    exit /b 1
)

echo.
echo Step 3: Testing the endpoint...
echo.

choice /c YN /m "Test the endpoint now? (Y/N)"
if %errorlevel%==1 (
    echo Testing challenge verification...
    python manage.py test_ebay_endpoint --challenge-code test123
    
    echo.
    echo Testing deletion notification...
    python manage.py test_ebay_endpoint --send-notification
)

echo.
echo =======================================================
echo Setup Complete!
echo =======================================================
echo.
echo Next steps:
echo 1. Make sure your server is running and accessible
echo 2. Go to https://developer.ebay.com/my/keys
echo 3. Click "Notifications" next to your App ID
echo 4. Select "Marketplace Account Deletion"
echo 5. Enter an alert email and save
echo 6. Enter your endpoint URL: %endpoint_url%
echo 7. Enter your verification token (shown above)
echo 8. Click Save - eBay will verify your endpoint
echo.
echo Check the Django admin to monitor notifications:
echo /admin/ebay_notifications/
echo.

pause
