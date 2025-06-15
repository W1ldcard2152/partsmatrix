"""
eBay Browse API Implementation
Modern replacement for deprecated Finding API
Uses OAuth Client Credentials for application-only access
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Load environment variables
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / '.env'

if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

@dataclass
class BrowseApiPart:
    """Data structure for eBay Browse API part information"""
    ebay_item_id: str
    title: str
    price: float
    shipping_cost: Optional[float]
    seller_username: str
    seller_feedback_score: int
    item_url: str
    image_url: Optional[str]
    condition: str
    location: str
    
    # Extracted part data
    part_name: Optional[str] = None
    part_number: Optional[str] = None
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    fitments: List[Dict] = None
    category: str = "HVAC & Climate Control"
    
    # Browse API specific data
    listing_marketplace_id: str = "EBAY_US"
    availability_status: str = "AVAILABLE"
    
    def __post_init__(self):
        if self.fitments is None:
            self.fitments = []

class EbayBrowseApiClient:
    """eBay Browse API client with OAuth Client Credentials"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        
        # eBay Browse API endpoints
        self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        self.browse_url = "https://api.ebay.com/buy/browse/v1"
        
        # Set up logging
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ebay_browse_api.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def get_access_token(self) -> str:
        """Get OAuth access token using client credentials flow"""
        
        # Check if we have a valid token
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        self.logger.info("Getting new OAuth access token...")
        
        # Prepare OAuth request
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self._get_auth_header()}'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'scope': 'https://api.ebay.com/oauth/api_scope'
        }
        
        try:
            response = requests.post(self.auth_url, headers=headers, data=data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 7200)  # Default 2 hours
            
            # Set expiration with 5-minute buffer
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            self.logger.info("✅ OAuth token obtained successfully")
            return self.access_token
            
        except requests.RequestException as e:
            self.logger.error(f"❌ OAuth token request failed: {e}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ OAuth token response invalid: {e}")
            raise

    def _get_auth_header(self) -> str:
        """Create Basic auth header for OAuth"""
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return encoded

    def search_items(self, 
                    query: str = "Acura AC Compressor",
                    category_id: str = "33654",
                    limit: int = 50,
                    marketplace_id: str = "EBAY_US") -> List[Dict]:
        """Search for items using Browse API"""
        
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-EBAY-C-MARKETPLACE-ID': marketplace_id,
            'Content-Type': 'application/json'
        }
        
        # Build search parameters
        params = {
            'q': query,
            'limit': min(limit, 200),  # eBay max per request
            'category_ids': category_id,
            'filter': 'buyingOptions:{FIXED_PRICE},price:[50..],conditions:{NEW,USED}'
        }
        
        url = f"{self.browse_url}/item_summary/search"
        
        try:
            self.logger.info(f"Searching for: {query}")
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract items from response
            items = data.get('itemSummaries', [])
            total = data.get('total', 0)
            
            self.logger.info(f"Found {len(items)} items (total: {total})")
            return items
            
        except requests.RequestException as e:
            self.logger.error(f"❌ Browse API search failed: {e}")
            if hasattr(e, 'response') and e.response:
                self.logger.error(f"Response: {e.response.text}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Browse API response invalid: {e}")
            return []

    def get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get detailed item information"""
        
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.browse_url}/item/{item_id}"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            self.logger.error(f"❌ Failed to get item details for {item_id}: {e}")
            return None

def test_browse_api_setup():
    """Test Browse API with OAuth"""
    
    # Get credentials from environment
    client_id = os.getenv('EBAY_APP_ID')  # Your current App ID
    client_secret = os.getenv('EBAY_CERT_ID')  # Your Cert ID acts as client secret
    
    if not client_id or not client_secret:
        print("❌ Missing eBay credentials")
        print("Need: EBAY_APP_ID and EBAY_CERT_ID")
        return False
    
    print("Testing eBay Browse API with OAuth...")
    print(f"Client ID: {client_id[:15]}...")
    print(f"Client Secret: {client_secret[:15]}...")
    
    try:
        # Create client
        client = EbayBrowseApiClient(client_id, client_secret)
        
        # Test OAuth
        token = client.get_access_token()
        print(f"✅ OAuth successful, token: {token[:20]}...")
        
        # Test search
        items = client.search_items("compressor", limit=3)
        
        if items:
            print(f"✅ Browse API search successful! Found {len(items)} items")
            
            # Show sample item
            item = items[0]
            print(f"Sample: {item.get('title', 'No title')[:50]}...")
            print(f"Price: {item.get('price', {}).get('value', 'N/A')}")
            
            return True
        else:
            print("❌ No items found")
            return False
            
    except Exception as e:
        print(f"❌ Browse API test failed: {e}")
        return False

if __name__ == "__main__":
    print("eBay Browse API Test")
    print("=" * 40)
    test_browse_api_setup()
