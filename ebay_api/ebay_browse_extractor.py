"""
eBay Browse API Parts Extractor - Production Version
Modern replacement for Finding API with OAuth Client Credentials
Extracts Acura AC compressor parts for Parts Matrix database
"""

import os
import requests
import json
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

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
class EbayBrowsePart:
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

class EbayBrowseExtractor:
    """Production eBay Browse API extractor for automotive parts"""
    
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = None
        
        # eBay Browse API endpoints
        self.auth_url = "https://api.ebay.com/identity/v1/oauth2/token"
        self.browse_url = "https://api.ebay.com/buy/browse/v1"
        
        # Set up logging (without emoji for Windows compatibility)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ebay_browse_extractor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Part extraction patterns (same as your Finding API version)
        self.part_name_patterns = [
            r'(AC\s+Compressor(?:\s+&\s+Clutch(?:\s+Assembly)?)?)',
            r'(A/C\s+Compressor(?:\s+&\s+Clutch(?:\s+Assembly)?)?)',
            r'(Air\s+Conditioning\s+Compressor)',
            r'(Compressor\s+&\s+Clutch(?:\s+Assembly)?)',
        ]
        
        self.part_number_patterns = [
            r'\(([0-9A-Z-]{8,})\)',
            r'Part\s+#:?\s*([0-9A-Z-]+)',
            r'Part\s+Number:?\s*([0-9A-Z-]+)',
            r'OEM:?\s*([0-9A-Z-]+)',
            r'([0-9A-Z]{5,}-[0-9A-Z]{3,}-[0-9A-Z]{3,})',
            r'([0-9A-Z]{8,})',
        ]
        
        self.manufacturer_mapping = {
            'acura': 'Acura', 'honda': 'Honda', 'denso': 'Denso', 'sanden': 'Sanden',
            'delphi': 'Delphi', 'valeo': 'Valeo', 'bosch': 'Bosch', 'four seasons': 'Four Seasons',
            'uac': 'UAC', 'ryc': 'RYC', 'gpd': 'GPD',
        }

    def get_access_token(self) -> str:
        """Get OAuth access token using client credentials flow"""
        
        if (self.access_token and self.token_expires_at and 
            datetime.now() < self.token_expires_at):
            return self.access_token
        
        self.logger.info("Getting new OAuth access token...")
        
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {encoded}'
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
            expires_in = token_data.get('expires_in', 7200)
            
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            self.logger.info("OAuth token obtained successfully")
            return self.access_token
            
        except Exception as e:
            self.logger.error(f"OAuth token request failed: {e}")
            raise

    def search_acura_ac_compressors(self, max_results: int = 100) -> List[EbayBrowsePart]:
        """Search specifically for Acura AC compressors over $50"""
        
        search_terms = [
            "Acura AC Compressor",
            "Acura A/C Compressor", 
            "Acura Air Conditioning Compressor",
            "Acura Compressor Clutch"
        ]
        
        all_parts = []
        
        for search_term in search_terms:
            self.logger.info(f"Searching for: {search_term}")
            
            items = self.search_items(
                query=search_term,
                category_id="33654",
                limit=max_results // len(search_terms)
            )
            
            for item in items:
                browse_part = self.parse_browse_item(item)
                if browse_part:
                    # Filter for Acura-related items
                    title_lower = browse_part.title.lower()
                    if 'acura' in title_lower or browse_part.manufacturer == 'Acura':
                        all_parts.append(browse_part)
            
            time.sleep(1)  # Respectful rate limiting
        
        # Remove duplicates
        unique_parts = {}
        for part in all_parts:
            if part.ebay_item_id not in unique_parts:
                unique_parts[part.ebay_item_id] = part
        
        result = list(unique_parts.values())
        self.logger.info(f"Found {len(result)} unique Acura AC compressor parts")
        return result

    def search_items(self, 
                    query: str,
                    category_id: str = "33654",
                    limit: int = 50) -> List[Dict]:
        """Search for items using Browse API"""
        
        token = self.get_access_token()
        
        headers = {
            'Authorization': f'Bearer {token}',
            'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
            'Content-Type': 'application/json'
        }
        
        params = {
            'q': query,
            'limit': min(limit, 200),
            'category_ids': category_id,
            'filter': 'buyingOptions:{FIXED_PRICE},price:[50..],conditions:{NEW,USED}'
        }
        
        url = f"{self.browse_url}/item_summary/search"
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('itemSummaries', [])
            
            self.logger.info(f"Found {len(items)} items")
            return items
            
        except Exception as e:
            self.logger.error(f"Browse API search failed: {e}")
            return []

    def parse_browse_item(self, item: Dict) -> Optional[EbayBrowsePart]:
        """Parse Browse API item into EbayBrowsePart object"""
        
        try:
            item_id = item.get('itemId', '')
            title = item.get('title', '')
            
            # Price information
            price_info = item.get('price', {})
            price = float(price_info.get('value', 0))
            
            # Shipping
            shipping_options = item.get('shippingOptions', [])
            shipping_cost = None
            if shipping_options:
                shipping_info = shipping_options[0].get('shippingCost', {})
                shipping_cost = float(shipping_info.get('value', 0))
            
            # Seller information
            seller = item.get('seller', {})
            seller_username = seller.get('username', '')
            seller_feedback = seller.get('feedbackScore', 0)
            
            # Item details
            item_url = item.get('itemWebUrl', '')
            condition = item.get('condition', '')
            location = item.get('itemLocation', {}).get('country', '')
            
            # Images
            image = item.get('image', {})
            image_url = image.get('imageUrl') if image else None
            
            # Create part object
            browse_part = EbayBrowsePart(
                ebay_item_id=item_id,
                title=title,
                price=price,
                shipping_cost=shipping_cost,
                seller_username=seller_username,
                seller_feedback_score=seller_feedback,
                item_url=item_url,
                image_url=image_url,
                condition=condition,
                location=location
            )
            
            # Extract part information
            browse_part.part_name = self.extract_part_name(title)
            browse_part.part_number = self.extract_part_number(title)
            browse_part.manufacturer = self.extract_manufacturer(title)
            browse_part.fitments = self.extract_fitments("", title)
            browse_part.description = title
            
            return browse_part
            
        except Exception as e:
            self.logger.error(f"Error parsing Browse API item: {e}")
            return None

    def extract_part_name(self, text: str) -> Optional[str]:
        """Extract part name from listing text"""
        for pattern in self.part_name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def extract_part_number(self, text: str) -> Optional[str]:
        """Extract part number from listing text"""
        for pattern in self.part_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                part_num = match.group(1).strip().upper()
                if len(part_num) >= 5:
                    return part_num
        return None

    def extract_manufacturer(self, text: str) -> Optional[str]:
        """Extract manufacturer from listing text"""
        text_lower = text.lower()
        
        # Check parts manufacturers first
        parts_manufacturers = ['denso', 'sanden', 'delphi', 'valeo', 'bosch']
        for mfg in parts_manufacturers:
            if mfg in text_lower:
                return self.manufacturer_mapping[mfg]
        
        # Then vehicle manufacturers
        for key, value in self.manufacturer_mapping.items():
            if key in text_lower:
                return value
        
        return None

    def extract_fitments(self, text: str, title: str) -> List[Dict]:
        """Extract vehicle fitment information"""
        fitments = []
        full_text = title
        
        # Year range patterns
        patterns = [
            r'(\d{4})-(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)',
            r'(?:For|Fits)?\s*(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                if len(groups) == 4 and groups[0].isdigit():
                    start_year = int(groups[0])
                    end_year = int(groups[1])
                    make = groups[2].title()
                    model = groups[3].upper()
                    
                    for year in range(start_year, min(end_year + 1, start_year + 15)):
                        if 1990 <= year <= 2030:
                            fitments.append({
                                'year': year,
                                'make': make,
                                'model': model,
                                'trim': 'Base',
                                'engine': ''
                            })
                elif len(groups) == 3:
                    year = int(groups[0])
                    make = groups[1].title()
                    model = groups[2].upper()
                    
                    if 1990 <= year <= 2030:
                        fitments.append({
                            'year': year,
                            'make': make,
                            'model': model,
                            'trim': 'Base',
                            'engine': ''
                        })
            
            if fitments:
                break
        
        return fitments

    def save_to_json(self, parts: List[EbayBrowsePart], filename: str = None) -> str:
        """Save parts data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ebay_browse_acura_ac_parts_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        parts_data = [asdict(part) for part in parts]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(parts_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved {len(parts)} parts to {filepath}")
        return filepath

    def save_to_csv(self, parts: List[EbayBrowsePart], filename: str = None) -> str:
        """Save parts data to CSV file"""
        import csv
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ebay_browse_acura_ac_parts_{timestamp}.csv"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if not parts:
            return filepath
        
        headers = [
            'ebay_item_id', 'title', 'price', 'shipping_cost', 'seller_username',
            'seller_feedback_score', 'item_url', 'condition', 'location',
            'part_name', 'part_number', 'manufacturer', 'description',
            'fitments_count', 'category', 'availability_status'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for part in parts:
                row = [
                    part.ebay_item_id, part.title, part.price, part.shipping_cost,
                    part.seller_username, part.seller_feedback_score, part.item_url,
                    part.condition, part.location, part.part_name, part.part_number,
                    part.manufacturer, part.description, len(part.fitments),
                    part.category, part.availability_status
                ]
                writer.writerow(row)
        
        self.logger.info(f"Saved {len(parts)} parts to {filepath}")
        return filepath

def main():
    """Main function to run the Browse API parts extractor"""
    
    client_id = os.getenv('EBAY_APP_ID')
    client_secret = os.getenv('EBAY_CERT_ID')
    
    if not client_id or not client_secret:
        print("Error: eBay credentials not found")
        print("Need: EBAY_APP_ID and EBAY_CERT_ID")
        return
    
    extractor = EbayBrowseExtractor(client_id, client_secret)
    
    print("Starting eBay Browse API Acura AC Compressor search...")
    print("Parameters:")
    print("- Modern Browse API (OAuth)")
    print("- Brand: Acura")
    print("- Category: AC Compressors & Clutches")
    print("- Minimum Price: $50")
    print("-" * 50)
    
    parts = extractor.search_acura_ac_compressors(max_results=100)
    
    if parts:
        print(f"\nFound {len(parts)} matching parts:")
        print("-" * 50)
        
        for i, part in enumerate(parts[:10], 1):
            print(f"{i}. {part.title}")
            print(f"   Price: ${part.price:.2f}")
            if part.shipping_cost:
                print(f"   Shipping: ${part.shipping_cost:.2f}")
            print(f"   Condition: {part.condition}")
            print(f"   Part Name: {part.part_name or 'Not extracted'}")
            print(f"   Part Number: {part.part_number or 'Not extracted'}")
            print(f"   Manufacturer: {part.manufacturer or 'Not extracted'}")
            print(f"   Fitments: {len(part.fitments)} found")
            print()
        
        if len(parts) > 10:
            print(f"... and {len(parts) - 10} more parts")
        
        # Save results
        json_file = extractor.save_to_json(parts)
        csv_file = extractor.save_to_csv(parts)
        
        print(f"\nResults saved to:")
        print(f"- JSON: {json_file}")
        print(f"- CSV: {csv_file}")
        
    else:
        print("No matching parts found.")

if __name__ == "__main__":
    main()
