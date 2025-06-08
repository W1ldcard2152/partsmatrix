#!/bin/bash

# Performance Optimization Deployment Script
# Run this after making the code changes to apply all optimizations

echo "🚀 Applying Performance Optimizations to Parts Matrix..."
echo "================================================"

# Change to the Django project directory
cd parts_interchange

# 1. Run database migrations (including the new performance indexes)
echo "📊 Applying database migrations..."
python manage.py migrate

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# 2. Collect static files (for production)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

if [ $? -eq 0 ]; then
    echo "✅ Static files collected successfully"
else
    echo "⚠️ Static files collection failed (may not be needed in development)"
fi

# 3. Warm up the cache
echo "🔥 Warming up caches..."
python manage.py warm_cache --full

if [ $? -eq 0 ]; then
    echo "✅ Cache warming completed successfully"
else
    echo "❌ Cache warming failed"
fi

# 4. Test the optimizations
echo "🧪 Testing optimizations..."

# Test cache functionality
echo "Testing cache..."
python manage.py shell -c "
from django.core.cache import cache
import time
test_key = 'optimization_test'
test_value = 'working'
cache.set(test_key, test_value, 60)
cached_value = cache.get(test_key)
if cached_value == test_value:
    print('✅ Cache is working properly')
else:
    print('❌ Cache is not working')
cache.delete(test_key)
"

# Test database connection
echo "Testing database connection..."
python manage.py shell -c "
from django.db import connection
from apps.parts.models import Part
try:
    count = Part.objects.count()
    print(f'✅ Database connection working - {count} parts found')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"

echo ""
echo "🎉 Performance optimization deployment completed!"
echo ""
echo "📈 EXPECTED IMPROVEMENTS:"
echo "• Admin interface: 2-5x faster loading"
echo "• API responses: 3-10x faster with caching"
echo "• Search queries: 5-20x faster with indexes"
echo "• Reduced cold starts from 10-30s to 2-5s"
echo ""
echo "📋 NEXT STEPS:"
echo "1. Test your admin interface - it should load much faster"
echo "2. Test API endpoints - they should respond quicker"
echo "3. Run cache warming every 10-15 minutes:"
echo "   python manage.py warm_cache"
echo "4. For Render free tier, use the keep_warm.py script:"
echo "   python ../keep_warm.py https://your-app.onrender.com"
echo ""
echo "💡 MONITORING:"
echo "• Watch your Render logs for any errors"
echo "• Monitor response times in your browser dev tools"
echo "• Check that cache hits are working in Django logs"
echo ""
echo "🆙 UPGRADE RECOMMENDATION:"
echo "Consider upgrading to Render's Starter plan (\$7/month) for:"
echo "• No cold starts"
echo "• Dedicated resources"
echo "• Better overall performance"
