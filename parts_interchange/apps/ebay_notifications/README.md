# eBay Marketplace Account Deletion Compliance

This Django app implements eBay's required Marketplace Account Deletion notification system for legal compliance. When eBay users request their data to be deleted, eBay sends notifications to all connected developer applications that must acknowledge and process these deletion requests.

## Overview

All eBay Developers Program applications are **required** to:
1. Subscribe to eBay marketplace account deletion notifications, OR
2. Apply for exemption if they don't store any eBay user data

This implementation provides:
- ✅ Challenge code verification endpoint for eBay subscription setup
- ✅ Account deletion notification receiver
- ✅ Automatic logging of all deletion requests
- ✅ Django admin interface for monitoring
- ✅ Management commands for easy setup and testing

## Quick Setup

### 1. Run Migrations

```bash
python manage.py migrate
```

### 2. Configure Your Endpoint

```bash
# Generate a configuration with a random verification token
python manage.py setup_ebay_notifications \
    --endpoint-url https://yourdomain.com/ebay/marketplace-account-deletion/ \
    --generate-token

# Or provide your own token (32-80 chars, alphanumeric + underscore + hyphen only)
python manage.py setup_ebay_notifications \
    --endpoint-url https://yourdomain.com/ebay/marketplace-account-deletion/ \
    --verification-token your-secure-token-here-32-to-80-chars
```

### 3. Test Your Endpoint (Optional)

```bash
# Test challenge code verification
python manage.py test_ebay_endpoint --challenge-code test123

# Test account deletion notification
python manage.py test_ebay_endpoint --send-notification
```

### 4. Subscribe on eBay Developer Portal

1. Go to [eBay Application Keys](https://developer.ebay.com/my/keys)
2. Click **"Notifications"** next to your App ID
3. Select **"Marketplace Account Deletion"** radio button
4. Enter an alert email address and click **Save**
5. Enter your endpoint URL: `https://yourdomain.com/ebay/marketplace-account-deletion/`
6. Enter the verification token from step 2
7. Click **Save** - eBay will immediately send a challenge code to verify your endpoint

## Endpoint Details

### URL Pattern
```
/ebay/marketplace-account-deletion/
```

### Challenge Verification (GET)
When you save your endpoint in the eBay portal, eBay sends a GET request:
```
GET /ebay/marketplace-account-deletion/?challenge_code=abc123
```

The endpoint responds with:
```json
{
  "challengeResponse": "52161ff4651cb71888801b47bae62f44d7f6d0aab17e70d00f64fc84368ca38f"
}
```

### Account Deletion Notifications (POST)
eBay sends POST requests with JSON payloads like:
```json
{
  "metadata": {
    "topic": "MARKETPLACE_ACCOUNT_DELETION",
    "schemaVersion": "1.0",
    "deprecated": false
  },
  "notification": {
    "notificationId": "49feeaeb-4982-42d9-a377-9645b8479411_33f7e043-fed8-442b-9d44-791923bd9a6d",
    "eventDate": "2021-03-19T20:43:59.462Z",
    "publishDate": "2021-03-19T20:43:59.679Z",
    "publishAttemptCount": 1,
    "data": {
      "username": "test_user",
      "userId": "ma8vp1jySJC",
      "eiasToken": "nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wJnY+gAZGEpwmdj6x9nY+seQ=="
    }
  }
}
```

The endpoint:
1. ✅ Immediately responds with HTTP 200 to acknowledge receipt
2. ✅ Logs the notification in the database
3. ✅ Processes any data deletion (if applicable)
4. ✅ Marks the notification as processed

## Database Models

### EbayNotificationConfig
Stores your endpoint configuration:
- `verification_token`: The 32-80 character token for eBay verification
- `endpoint_url`: Your notification endpoint URL
- `is_active`: Whether this configuration is active

### EbayAccountDeletionLog
Logs every deletion notification received:
- `notification_id`: Unique eBay notification ID
- `username`: eBay username requesting deletion
- `user_id`: eBay user ID (immutable identifier)
- `eias_token`: eBay EIAS token
- `event_date`: When the user requested deletion
- `publish_date`: When eBay sent the notification
- `received_date`: When we received it
- `processed`: Whether we've processed the deletion
- `deleted_data_summary`: Summary of what data was deleted

## Admin Interface

Access the Django admin at `/admin/` to:
- View all deletion notifications received
- Monitor processing status
- Search and filter by username, user ID, or dates
- View configuration settings

The admin interface provides:
- 📊 List view with key information
- 🔍 Search by notification ID, username, user ID
- 📅 Date hierarchy for browsing by date
- 📝 Detailed view of each notification

## Data Processing

Currently, this implementation:
1. ✅ Logs all deletion requests for compliance
2. ✅ Acknowledges receipt to eBay immediately
3. ℹ️ Performs minimal data deletion (since this is a parts database)

### Customizing Data Deletion

To customize what data gets deleted, edit the `_process_account_deletion()` method in `views.py`:

```python
def _process_account_deletion(self, username, user_id, eias_token):
    """
    Process the account deletion by removing any stored eBay user data.
    """
    deleted_items = []
    
    # Add your custom deletion logic here
    # Example:
    # MyModel.objects.filter(ebay_user_id=user_id).delete()
    # deleted_items.append(f"Deleted {count} records from MyModel")
    
    return "; ".join(deleted_items)
```

## Compliance Notes

### Required Response Times
- ✅ **Immediate acknowledgment**: Respond with HTTP 200 within seconds
- ✅ **Data deletion**: Complete within reasonable time (we do this immediately)
- ✅ **Logging**: Keep records of all deletion requests for audit purposes

### Error Handling
- ❌ If your endpoint doesn't respond, eBay will retry for 24 hours
- 📧 After 24 hours, eBay sends an alert email
- ⚠️ After 30 days of non-compliance, your API access may be terminated

### What We Store vs. What We Delete
Since this is primarily a **parts interchange database**, we typically don't store:
- ❌ eBay user personal information
- ❌ eBay user purchase history
- ❌ eBay user preferences or settings

We primarily store:
- ✅ Parts data (public information)
- ✅ Vehicle compatibility (public information)
- ✅ Manufacturer information (public information)

Therefore, our deletion process mainly involves:
- 📝 Logging the deletion request for compliance
- 🔍 Checking for any user-specific cached data
- 🗑️ Removing any accidentally stored user data

## Testing

### Test Challenge Verification
```bash
python manage.py test_ebay_endpoint --challenge-code abc123
```

### Test Deletion Notification
```bash
python manage.py test_ebay_endpoint --send-notification
```

### Manual Testing with curl

Challenge verification:
```bash
curl "https://yourdomain.com/ebay/marketplace-account-deletion/?challenge_code=test123"
```

Deletion notification:
```bash
curl -X POST https://yourdomain.com/ebay/marketplace-account-deletion/ \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {"topic": "MARKETPLACE_ACCOUNT_DELETION", "schemaVersion": "1.0", "deprecated": false},
    "notification": {
      "notificationId": "test-123",
      "eventDate": "2025-06-11T20:43:59.462Z",
      "publishDate": "2025-06-11T20:43:59.679Z",
      "publishAttemptCount": 1,
      "data": {"username": "test_user", "userId": "test123", "eiasToken": "dGVzdA=="}
    }
  }'
```

## Monitoring

### Django Admin
- Check `/admin/ebay_notifications/ebayaccountdeletionlog/` for all deletion requests
- Monitor processing status and any errors

### Logs
The app logs to Django's logging system:
- ✅ Successful challenge verifications
- ✅ Received deletion notifications
- ✅ Processing completion
- ❌ Errors and failures

### Expected Volume
According to eBay documentation, expect up to **1,500 notifications per day** during peak periods.

## Troubleshooting

### "Configuration not found" Error
```bash
python manage.py setup_ebay_notifications --endpoint-url https://yourdomain.com/ebay/marketplace-account-deletion/ --generate-token
```

### Challenge Verification Fails
1. Check that your verification token matches exactly
2. Ensure your endpoint URL is exactly what you configured
3. Verify HTTPS is working properly
4. Test locally with the management command

### Notifications Not Being Received
1. Check eBay Developer Portal subscription status
2. Verify your endpoint is publicly accessible
3. Check Django logs for errors
4. Test with the management command

### Performance Issues
If receiving high volumes of notifications:
1. Consider using a task queue (Celery) for processing
2. Optimize database queries in the deletion processing
3. Add monitoring and alerting

## Security Considerations

### HTTPS Required
- ✅ eBay requires HTTPS endpoints
- ✅ Endpoint validates token properly
- ✅ No authentication required (eBay signs requests)

### Token Security
- 🔐 Keep verification token secure
- 🔄 Rotate tokens periodically if needed
- 📝 Store in environment variables for production

### Input Validation
- ✅ Validates JSON payload structure
- ✅ Checks required fields
- ✅ Handles malformed requests gracefully

## Production Deployment

### Environment Variables
```bash
# Add to your .env file if needed
EBAY_NOTIFICATION_ENDPOINT=https://yourdomain.com/ebay/marketplace-account-deletion/
EBAY_VERIFICATION_TOKEN=your-secure-token-here
```

### Server Configuration
Ensure your web server (nginx, Apache, etc.) can handle:
- ✅ HTTPS traffic
- ✅ POST requests with JSON payloads
- ✅ Reasonable timeout settings
- ✅ Proper logging

### Monitoring
Set up alerts for:
- 📧 Failed deletion notification processing
- 📊 High volume of notifications
- ❌ Endpoint downtime
- 🔄 Processing delays

## Support

For eBay-specific issues:
- 📖 [eBay Developer Documentation](https://developer.ebay.com/marketplace-account-deletion)
- 💬 [eBay Developer Forums](https://community.ebay.com/t5/Developer-Support/bd-p/developer-support)

For technical implementation issues:
- 🐛 Check Django logs
- 🧪 Use the included test commands
- 📝 Review the admin interface for logged notifications
