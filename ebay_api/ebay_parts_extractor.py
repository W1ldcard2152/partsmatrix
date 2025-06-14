"""
eBay Parts Extractor
Extracts parts data from eBay Motors listings using the eBay API
Focuses on AC Compressors and Clutches for Acura vehicles over $50

Extracts the same data fields as the smart parser:
- part_name
- part_number
- manufacturer
- description
- fitments (year, make, model, trim, engine)
- category
"""

import os
import sys
import json
import requests
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# Load environment variables from .env file in project root
project_root = Path(__file__).resolve().parent.parent
env_path = project_root / '.env'

# Load environment variables using python-dotenv or manual parsing
try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from {env_path}")
    else:
        print(f"⚠️  .env file not found at {env_path}")
except ImportError:
    # Fallback: manually parse .env file
    print("python-dotenv not installed, manually loading .env file...")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Manually loaded environment variables from {env_path}")
    else:
        print(f"❌ .env file not found at {env_path}")

# Add the Django project to the path so we can import Django models
# Follow the same pattern as manage.py

# Get the project root (Parts Matrix directory)
project_root = Path(__file__).resolve().parent.parent
parts_interchange_dir = project_root / 'parts_interchange'
apps_dir = parts_interchange_dir / 'apps'

# Add paths in the same order as manage.py
sys.path.insert(0, str(apps_dir))  # Add apps directory to path
sys.path.insert(0, str(parts_interchange_dir))  # Add parts_interchange directory to path

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parts_interchange.settings')

import django
django.setup()

# Now we can import Django models
from apps.parts.models import Part, Manufacturer, PartCategory
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment


@dataclass
class EbayPart:
    """Data structure for eBay part information"""
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
    
    # Extracted part data (similar to smart parser)
    part_name: Optional[str] = None
    part_number: Optional[str] = None
    manufacturer: Optional[str] = None
    description: Optional[str] = None
    fitments: List[Dict] = None
    category: str = "HVAC & Climate Control"
    
    # eBay specific data
    listing_type: str = "FixedPrice"
    time_left: Optional[str] = None
    watch_count: Optional[int] = None
    
    def __post_init__(self):
        if self.fitments is None:
            self.fitments = []


class EbayPartsExtractor:
    """eBay API client for extracting automotive parts data"""
    
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.base_url = "https://svcs.ebay.com/services/search/FindingService/v1"
        
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ebay_extractor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Improved part name extraction patterns
        self.part_name_patterns = [
            # Look for AC/A/C compressor patterns first (most specific)
            r'(AC\s+Compressor(?:\s+&\s+Clutch(?:\s+Assembly)?)?)',
            r'(A/C\s+Compressor(?:\s+&\s+Clutch(?:\s+Assembly)?)?)',
            r'(Air\s+Conditioning\s+Compressor)',
            r'(Compressor\s+&\s+Clutch(?:\s+Assembly)?)',
            # General patterns
            r'(?:For\s+)?\d{4}[- ]\d{4}\s+\w+\s+\w+\s+([A-Za-z/\s&]+?)\s*(?:-|\(|Part|OEM)',
            r'\w+\s+\w+\s+\d{4}-\d{4}\s+([A-Za-z/\s&]+?)\s*(?:-|\(|Part)',
            r'^([A-Za-z/\s&]+?)\s*-\s*(?:Denso|Sanden|Valeo|Delphi)',
        ]
        
        self.part_number_patterns = [
            r'\(([0-9A-Z-]{8,})\)',
            r'Part\s+#:?\s*([0-9A-Z-]+)',
            r'Part\s+Number:?\s*([0-9A-Z-]+)',
            r'SKU:?\s*([0-9A-Z-]+)',
            r'OEM:?\s*([0-9A-Z-]+)',
            r'([0-9A-Z]{5,}-[0-9A-Z]{3,}-[0-9A-Z]{3,})',
            r'([0-9A-Z]{8,})',
        ]
        
        self.manufacturer_mapping = {
            # Vehicle manufacturers
            'acura': 'Acura', 'honda': 'Honda', 'toyota': 'Toyota', 'lexus': 'Lexus',
            'ford': 'Ford', 'chevrolet': 'Chevrolet', 'gm': 'GM', 'dodge': 'Dodge',
            'chrysler': 'Chrysler', 'jeep': 'Jeep', 'ram': 'Ram', 'bmw': 'BMW',
            'mercedes': 'Mercedes-Benz', 'audi': 'Audi', 'volkswagen': 'Volkswagen',
            'vw': 'Volkswagen', 'nissan': 'Nissan', 'infiniti': 'Infiniti',
            'mazda': 'Mazda', 'subaru': 'Subaru', 'mitsubishi': 'Mitsubishi',
            'hyundai': 'Hyundai', 'kia': 'Kia', 'volvo': 'Volvo', 'porsche': 'Porsche',
            # Parts manufacturers (prioritize these for AC compressors)
            'denso': 'Denso', 'sanden': 'Sanden', 'delphi': 'Delphi', 'valeo': 'Valeo',
            'bosch': 'Bosch', 'mahle': 'Mahle', 'behr': 'Behr', 'four seasons': 'Four Seasons',
            'uac': 'UAC', 'ryc': 'RYC', 'gpd': 'GPD',
        }

    def extract_part_name(self, text: str) -> Optional[str]:
        """Extract part name from listing text"""
        for pattern in self.part_name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'\s+', ' ', name)
                return name.title()
        
        # Fallback: look for AC/A/C Compressor patterns
        ac_patterns = [
            r'(AC\s+Compressor)',
            r'(A/C\s+Compressor)',
            r'(Air\s+Conditioning\s+Compressor)',
            r'(Compressor\s+&\s+Clutch)',
        ]
        
        for pattern in ac_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

    def extract_part_number(self, text: str) -> Optional[str]:
        """Extract part number from listing text"""
        for pattern in self.part_number_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                part_num = match.group(1).strip().upper()
                if len(part_num) >= 5 and any(c.isdigit() for c in part_num):
                    return part_num
        return None

    def extract_manufacturer(self, text: str) -> Optional[str]:
        """Extract manufacturer from listing text"""
        # First try explicit manufacturer patterns
        patterns = [
            r'Manufacturer:?\s*([A-Za-z\s]+)',
            r'Brand:?\s*([A-Za-z\s]+)',
            r'Made\s+by:?\s*([A-Za-z\s]+)',
            r'OEM:?\s*([A-Za-z\s]+)',
            r'([A-Za-z\s]+)\s+OEM',
            r'Genuine\s+([A-Za-z\s]+?)\s+',
            r'Original\s+([A-Za-z\s]+?)\s+',
            # Look for manufacturer names in titles like "Brand - Model"
            r'-\s*([A-Za-z\s]+?)\s*\(',
            r'-\s*([A-Za-z\s]+?)\s*(?:Part|OEM|SKU)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                mfg = match.group(1).strip().lower()
                if mfg in self.manufacturer_mapping:
                    return self.manufacturer_mapping[mfg]
        
        # Check for parts manufacturers first (they're more relevant for parts)
        parts_manufacturers = ['denso', 'sanden', 'delphi', 'valeo', 'bosch', 'mahle', 'four seasons', 'uac']
        text_lower = text.lower()
        
        for mfg in parts_manufacturers:
            if mfg in text_lower:
                return self.manufacturer_mapping[mfg]
        
        # Then check vehicle manufacturers
        for key, value in self.manufacturer_mapping.items():
            if key not in parts_manufacturers and key in text_lower:
                return value
        
        return None

    def extract_fitments(self, text: str, title: str) -> List[Dict]:
        """Extract vehicle fitment information from listing"""
        fitments = []
        
        # Use only title for now (description parsing can be noisy)
        full_text = title
        
        # More precise patterns for year ranges and models (ORDER MATTERS!)
        year_model_patterns = [
            # Pattern: "Acura MDX 2007-2013" (make model year-year) - MUST BE FIRST!
            r'^([A-Za-z]+)\s+([A-Za-z0-9]+)\s+(\d{4})-(\d{4})\s+',
            # Pattern: "For 2006 2007 2008 Acura TSX" (For year year year make model)
            r'(?:For|Fits)\s+(\d{4})\s+(\d{4})\s+(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)',
            # Pattern: "2005-2008 Acura TL AC Compressor" (year-year make model)
            r'(\d{4})-(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)(?:\s+[A-Z/]+)?',
            # Pattern: "2008 Acura TSX" (year make model)
            r'(?:For|Fits)?\s*(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9]+)(?:\s+[A-Z/]+)?',
        ]
        
        for pattern in year_model_patterns:
            matches = re.finditer(pattern, full_text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                
                # Handle different pattern types based on group content
                if len(groups) == 4 and groups[2].isdigit() and groups[3].isdigit():  # make, model, year1, year2 (FIRST PATTERN)
                    make = groups[0].title()
                    model = groups[1].upper()
                    start_year = int(groups[2])
                    end_year = int(groups[3])
                elif len(groups) == 4 and groups[0].isdigit() and groups[1].isdigit():  # year1, year2, make, model
                    start_year = int(groups[0])
                    end_year = int(groups[1])
                    make = groups[2].title()
                    model = groups[3].upper()  # Models are often uppercase (TL, TSX, MDX)
                elif len(groups) == 5:  # For pattern with three years
                    years = [int(groups[0]), int(groups[1]), int(groups[2])]
                    make = groups[3].title()
                    model = groups[4].upper()
                    for year in years:
                        if 1990 <= year <= 2030:
                            fitments.append({
                                'year': year,
                                'make': make,
                                'model': model,
                                'trim': 'Base',
                                'engine': ''
                            })
                    continue
                elif len(groups) == 3:  # year, make, model
                    start_year = end_year = int(groups[0])
                    make = groups[1].title()
                    model = groups[2].upper()
                else:
                    continue
                
                # Generate fitments for year range
                for year in range(start_year, min(end_year + 1, start_year + 20)):  # Limit range
                    if 1990 <= year <= 2030:  # Reasonable year range
                        fitments.append({
                            'year': year,
                            'make': make,
                            'model': model,
                            'trim': 'Base',  # Default trim
                            'engine': ''     # Engine info not always available
                        })
            
            # Stop after first successful pattern match to avoid conflicts
            if fitments:
                break
        
        return fitments

    def search_parts(self, 
                    keywords: str = "AC Compressor",
                    category_id: str = "33654",  # eBay Motors > Parts & Accessories > Car & Truck Parts > AC & Heating > AC Compressors & Clutches
                    min_price: float = 50.0,
                    max_results: int = 100) -> List[Dict]:
        """Search eBay for automotive parts"""
        
        params = {
            'OPERATION-NAME': 'findItemsAdvanced',
            'SERVICE-VERSION': '1.0.0',
            'SECURITY-APPNAME': self.app_id,
            'RESPONSE-DATA-FORMAT': 'JSON',
            'REST-PAYLOAD': '',
            'keywords': keywords,
            'categoryId': category_id,
            'paginationInput.entriesPerPage': min(max_results, 100),
            'itemFilter(0).name': 'MinPrice',
            'itemFilter(0).value': str(min_price),
            'itemFilter(1).name': 'Condition',
            'itemFilter(1).value(0)': 'Used',
            'itemFilter(1).value(1)': 'New',
            'itemFilter(2).name': 'ListingType',
            'itemFilter(2).value': 'FixedPrice',
            'sortOrder': 'PricePlusShippingLowest'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'errorMessage' in data:
                error_msg = data['errorMessage']
                if isinstance(error_msg, list) and len(error_msg) > 0:
                    error_detail = error_msg[0].get('error', {}).get('message', 'Unknown error')
                    self.logger.error(f"eBay API Error: {error_detail}")
                else:
                    self.logger.error(f"eBay API Error: {error_msg}")
                return []
            
            # Extract search results
            search_result = data.get('findItemsAdvancedResponse', [{}])[0]
            search_results = search_result.get('searchResult', [{}])[0]
            items = search_results.get('item', [])
            
            self.logger.info(f"Found {len(items)} items for keywords: {keywords}")
            return items
            
        except requests.RequestException as e:
            self.logger.error(f"Request error: {e}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return []

    def parse_item(self, item: Dict) -> Optional[EbayPart]:
        """Parse a single eBay item into EbayPart object"""
        try:
            # Extract basic item information
            item_id = item.get('itemId', [''])[0]
            title = item.get('title', [''])[0]
            
            # Price information
            price_info = item.get('sellingStatus', [{}])[0]
            current_price = price_info.get('currentPrice', [{}])[0]
            price = float(current_price.get('@currencyId') == 'USD' and current_price.get('__value__', 0) or 0)
            
            # Shipping information
            shipping_info = item.get('shippingInfo', [{}])[0]
            shipping_cost_info = shipping_info.get('shippingServiceCost', [{}])[0]
            shipping_cost = None
            if shipping_cost_info:
                shipping_cost = float(shipping_cost_info.get('__value__', 0))
            
            # Seller information
            seller_info = item.get('sellerInfo', [{}])[0]
            seller_username = seller_info.get('sellerUserName', [''])[0]
            seller_feedback = int(seller_info.get('feedbackScore', ['0'])[0])
            
            # Item details
            item_url = item.get('viewItemURL', [''])[0]
            condition = item.get('condition', [{}])[0].get('conditionDisplayName', [''])[0]
            location = item.get('location', [''])[0]
            
            # Images
            gallery_url = item.get('galleryURL', [''])
            image_url = gallery_url[0] if gallery_url and gallery_url[0] else None
            
            # Additional info
            listing_info = item.get('listingInfo', [{}])[0]
            listing_type = listing_info.get('listingType', [''])[0]
            time_left = listing_info.get('timeLeft', [''])[0]
            watch_count = listing_info.get('watchCount', [None])[0]
            if watch_count:
                watch_count = int(watch_count)
            
            # Create EbayPart object
            ebay_part = EbayPart(
                ebay_item_id=item_id,
                title=title,
                price=price,
                shipping_cost=shipping_cost,
                seller_username=seller_username,
                seller_feedback_score=seller_feedback,
                item_url=item_url,
                image_url=image_url,
                condition=condition,
                location=location,
                listing_type=listing_type,
                time_left=time_left,
                watch_count=watch_count
            )
            
            # Extract part-specific information from title
            ebay_part.part_name = self.extract_part_name(title)
            ebay_part.part_number = self.extract_part_number(title)
            ebay_part.manufacturer = self.extract_manufacturer(title)
            ebay_part.fitments = self.extract_fitments("", title)  # Only using title for now
            ebay_part.description = title  # Use title as description for now
            
            return ebay_part
            
        except Exception as e:
            self.logger.error(f"Error parsing item: {e}")
            return None

    def get_item_details(self, item_id: str) -> Optional[Dict]:
        """Get detailed item information including description (requires different API)"""
        # This would require the eBay Shopping API or Trading API
        # For now, we'll work with what we have from the Finding API
        self.logger.info(f"Detailed item lookup not implemented for item {item_id}")
        return None

    def search_acura_ac_compressors(self, max_results: int = 100) -> List[EbayPart]:
        """Search specifically for Acura AC compressors over $50"""
        
        # Search terms optimized for Acura AC compressors
        search_terms = [
            "Acura AC Compressor",
            "Acura A/C Compressor", 
            "Acura Air Conditioning Compressor",
            "Acura Compressor Clutch"
        ]
        
        all_parts = []
        
        for search_term in search_terms:
            self.logger.info(f"Searching for: {search_term}")
            
            items = self.search_parts(
                keywords=search_term,
                category_id="33654",  # AC Compressors & Clutches
                min_price=50.0,
                max_results=max_results // len(search_terms)
            )
            
            for item in items:
                ebay_part = self.parse_item(item)
                if ebay_part:
                    # Filter for Acura-related items
                    title_lower = ebay_part.title.lower()
                    if 'acura' in title_lower or ebay_part.manufacturer == 'Acura':
                        all_parts.append(ebay_part)
            
            # Be respectful to eBay's rate limits
            time.sleep(1)
        
        # Remove duplicates based on item ID
        unique_parts = {}
        for part in all_parts:
            if part.ebay_item_id not in unique_parts:
                unique_parts[part.ebay_item_id] = part
        
        result = list(unique_parts.values())
        self.logger.info(f"Found {len(result)} unique Acura AC compressor parts")
        return result

    def save_to_json(self, parts: List[EbayPart], filename: str = None) -> str:
        """Save parts data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ebay_acura_ac_parts_{timestamp}.json"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Convert EbayPart objects to dictionaries
        parts_data = []
        for part in parts:
            part_dict = asdict(part)
            parts_data.append(part_dict)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(parts_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved {len(parts)} parts to {filepath}")
        return filepath

    def save_to_csv(self, parts: List[EbayPart], filename: str = None) -> str:
        """Save parts data to CSV file"""
        import csv
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ebay_acura_ac_parts_{timestamp}.csv"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        if not parts:
            self.logger.warning("No parts to save to CSV")
            return filepath
        
        # Define CSV headers
        headers = [
            'ebay_item_id', 'title', 'price', 'shipping_cost', 'seller_username',
            'seller_feedback_score', 'item_url', 'condition', 'location',
            'part_name', 'part_number', 'manufacturer', 'description',
            'fitments_count', 'category', 'listing_type', 'time_left', 'watch_count'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for part in parts:
                row = [
                    part.ebay_item_id,
                    part.title,
                    part.price,
                    part.shipping_cost,
                    part.seller_username,
                    part.seller_feedback_score,
                    part.item_url,
                    part.condition,
                    part.location,
                    part.part_name,
                    part.part_number,
                    part.manufacturer,
                    part.description,
                    len(part.fitments) if part.fitments else 0,
                    part.category,
                    part.listing_type,
                    part.time_left,
                    part.watch_count
                ]
                writer.writerow(row)
        
        self.logger.info(f"Saved {len(parts)} parts to {filepath}")
        return filepath


def main():
    """Main function to run the eBay parts extractor"""
    
    # Check for eBay App ID in environment variables
    ebay_app_id = os.getenv('EBAY_APP_ID')
    if not ebay_app_id:
        print("Error: EBAY_APP_ID environment variable not set")
        print("Please set your eBay App ID:")
        print("export EBAY_APP_ID='your-app-id-here'")
        print("\nOr create a .env file in the ebay_api directory with:")
        print("EBAY_APP_ID=your-app-id-here")
        return
    
    # Initialize extractor
    extractor = EbayPartsExtractor(ebay_app_id)
    
    print("Starting eBay Acura AC Compressor search...")
    print("Parameters:")
    print("- Brand: Acura")
    print("- Category: AC Compressors & Clutches")
    print("- Minimum Price: $50")
    print("-" * 50)
    
    # Search for parts
    parts = extractor.search_acura_ac_compressors(max_results=100)
    
    if parts:
        print(f"\nFound {len(parts)} matching parts:")
        print("-" * 50)
        
        for i, part in enumerate(parts[:10], 1):  # Show first 10
            print(f"{i}. {part.title}")
            print(f"   Price: ${part.price:.2f}")
            if part.shipping_cost:
                print(f"   Shipping: ${part.shipping_cost:.2f}")
            print(f"   Condition: {part.condition}")
            print(f"   Part Name: {part.part_name or 'Not extracted'}")
            print(f"   Part Number: {part.part_number or 'Not extracted'}")
            print(f"   Manufacturer: {part.manufacturer or 'Not extracted'}")
            print(f"   Fitments: {len(part.fitments)} found")
            print(f"   URL: {part.item_url}")
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
        print("This could be due to:")
        print("- Invalid eBay App ID")
        print("- Network connectivity issues")
        print("- No current listings matching the criteria")


if __name__ == "__main__":
    main()
