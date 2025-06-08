#!/usr/bin/env python3
"""
Keep Render database warm by pinging the API regularly
Run this script on your local machine or use a service like UptimeRobot
"""

import requests
import time
import sys
from datetime import datetime

def ping_api(base_url):
    """Ping the API to keep the database connection warm"""
    endpoints = [
        '/api/stats/',
        '/api/manufacturers/',
        '/api/makes/',
    ]
    
    for endpoint in endpoints:
        try:
            url = f"{base_url.rstrip('/')}{endpoint}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {datetime.now().strftime('%H:%M:%S')} - {endpoint} - OK")
                break  # One successful ping is enough
            else:
                print(f"⚠️ {datetime.now().strftime('%H:%M:%S')} - {endpoint} - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ {datetime.now().strftime('%H:%M:%S')} - {endpoint} - Error: {e}")
    
    # Also warm the cache
    try:
        warm_url = f"{base_url.rstrip('/')}/api/stats/"
        requests.get(warm_url, timeout=30)
    except:
        pass  # Silent fail for cache warming

def main():
    if len(sys.argv) != 2:
        print("Usage: python keep_warm.py <YOUR_RENDER_URL>")
        print("Example: python keep_warm.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    print(f"🔥 Starting database keep-warm for: {base_url}")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        while True:
            ping_api(base_url)
            time.sleep(600)  # Wait 10 minutes between pings
            
    except KeyboardInterrupt:
        print("\n👋 Stopping keep-warm service")

if __name__ == "__main__":
    main()
