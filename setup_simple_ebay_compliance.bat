@echo off
echo ================================================================
echo eBay Compliance - Simple Website Setup
echo ================================================================
echo.
echo This script will help you configure eBay compliance for your actual website
echo (much simpler than the ngrok approach!)
echo.

echo Step 1: Configure Django settings
echo ==================================
echo.
echo You need to add your domain to ALLOWED_HOSTS in your Django settings.
echo.
set /p domain="Enter your domain (e.g., yourdomain.com): "
if "%domain%"=="" (
    echo ERROR: Domain cannot be empty
    pause
    exit /b 1
)

echo.
echo Add this to your .env file or Django settings:
echo ALLOWED_HOSTS=%domain%,www.%domain%,localhost,127.0.0.1
echo.
pause

echo Step 2: Configure eBay endpoint
echo ================================
echo.
set endpoint_url=https://%domain%/ebay/marketplace-account-deletion/
echo Your endpoint URL will be: %endpoint_url%
echo.

choice /c YN /m "Configure eBay notifications now? (Y/N)"
if %errorlevel%==2 goto manual_config

python manage.py setup_ebay_notifications --endpoint-url %endpoint_url% --generate-token
if %errorlevel% neq 0 (
    echo ERROR: Failed to configure eBay notifications
    pause
    exit /b 1
)

echo.
echo Step 3: Test the configuration
echo ==============================
echo.
python manage.py test_ebay_endpoint --challenge-code test123

echo.
echo Step 4: Deploy to your website
echo ===============================
echo.
echo 1. Deploy your Django app to your hosting provider
echo 2. Make sure the apps/ebay_notifications app is included
echo 3. Run migrations on your production server
echo 4. Test the endpoint: curl "https://%domain%/ebay/marketplace-account-deletion/?challenge_code=test"
echo.

echo Step 5: Configure eBay Developer Portal
echo ========================================
echo.
echo 1. Go to: https://developer.ebay.com/my/keys
echo 2. Click "Notifications" next to your App ID
echo 3. Select "Marketplace Account Deletion"
echo 4. Enter an alert email and save
echo 5. Enter endpoint URL: %endpoint_url%
echo 6. Enter the verification token shown above
echo 7. Click Save - eBay will test your endpoint
echo.

echo ================================================================
echo SETUP COMPLETE!
echo ================================================================
echo.
echo Your eBay compliance endpoint: %endpoint_url%
echo Django admin: https://%domain%/admin/ebay_notifications/
echo.
echo This approach is much simpler and more reliable than ngrok!
echo.

pause
goto end

:manual_config
echo.
echo Manual configuration:
echo =====================
echo.
echo Run this command after deploying:
echo python manage.py setup_ebay_notifications --endpoint-url %endpoint_url% --generate-token
echo.

:end
