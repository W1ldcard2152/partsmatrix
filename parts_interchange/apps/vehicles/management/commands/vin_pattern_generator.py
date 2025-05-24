"""
VIN Pattern Generator for NHTSA API
Generates VIN patterns for make/model/year combinations to get detailed specs
"""

import requests
import time
from typing import List, Dict, Optional


class VINPatternGenerator:
    """Generate VIN patterns for make/model/year combinations"""
    
    def __init__(self):
        self.base_url = 'https://vpic.nhtsa.dot.gov/api'
        
        # Common WMI (World Manufacturer Identifier) patterns for major manufacturers
        self.wmi_patterns = {
            # Domestic makes
            'FORD': ['1FT', '1FA', '1FB', '1FC', '1FD', '1FE', '1FF', '1FG', '1FH', '1FM', '1FN', '1FP', '1FR', '1FS', '1FU', '1FV', '1FW', '1FX', '1FY', '1FZ'],
            'CHEVROLET': ['1G1', '1G2', '1G3', '1G4', '1G6', '1GC', '1GN', '1GY', '1GZ'],
            'GMC': ['1GT', '1GK'],
            'DODGE': ['1B3', '1B4', '1B7', '1D3', '1D4', '1D7', '1D8'],
            'CHRYSLER': ['1C3', '1C4', '1C6', '1C8'],
            'JEEP': ['1J4', '1J8'],
            'RAM': ['1C6', '3C6'],
            'CADILLAC': ['1G6'],
            'BUICK': ['1G4'],
            'LINCOLN': ['1LN', '1MH'],
            
            # Foreign makes
            'TOYOTA': ['4T1', '4T3', '4T4', '5TD', '5TE', '5TF', 'JTD', 'JTE', 'JTG', 'JTH', 'JTJ', 'JTK', 'JTM'],
            'HONDA': ['1HG', '1HF', '2HG', '2HF', '19X', 'JHM'],
            'NISSAN': ['1N4', '1N6', '3N1', '3N6', 'JN1', 'JN6', 'JN8'],
            'HYUNDAI': ['KMH', 'KMF', 'KME'],
            'KIA': ['KNA', 'KND', 'KNE', 'KNM'],
            'BMW': ['WBA', 'WBS', 'WBY', '4US', '5UX', '5UM'],
            'MERCEDES-BENZ': ['WDD', 'WDC', '4JG', '4JH'],
            'AUDI': ['WAU', 'WA1'],
            'VOLKSWAGEN': ['WVW', '3VW', '1VW'],
            'SUBARU': ['4S3', '4S4', 'JF1', 'JF2'],
            'MAZDA': ['JM1', 'JM3', '3MZ'],
            'VOLVO': ['YV1', 'YV4'],
            'LEXUS': ['JTH', 'JTJ', '2T2', '5TD'],
            'ACURA': ['19U', 'JH4'],
            'INFINITI': ['JN1', 'JNK'],
            'TESLA': ['5YJ'],
        }
    
    def get_wmi_for_make(self, make_name: str) -> List[str]:
        """Get WMI patterns for a make"""
        make_upper = make_name.upper()
        
        # Direct match
        if make_upper in self.wmi_patterns:
            return self.wmi_patterns[make_upper]
        
        # Partial matches
        patterns = []
        for make_key, wmis in self.wmi_patterns.items():
            if make_key in make_upper or make_upper in make_key:
                patterns.extend(wmis)
        
        return patterns if patterns else ['1G1']  # Default fallback
    
    def generate_vin_patterns(self, make_name: str, model_name: str, year: int, count: int = 5) -> List[str]:
        """Generate VIN patterns for a make/model/year combination"""
        wmis = self.get_wmi_for_make(make_name)
        patterns = []
        
        year_code = self.get_year_code(year)
        if not year_code:
            return []
        
        for wmi in wmis[:3]:  # Use first 3 WMI patterns
            # Generate sequential patterns
            for i in range(count):
                # Basic VIN structure: WMI + VDS(6) + Check + Year + Plant + Sequential(6)
                # We'll use wildcards/patterns for the unknown parts
                base_vin = f"{wmi}XXXXXX{year_code}X"
                
                # Add sequential numbers
                sequential = f"{100000 + i:06d}"
                full_vin = base_vin + sequential
                
                patterns.append(full_vin)
        
        return patterns[:count]
    
    def get_year_code(self, year: int) -> Optional[str]:
        """Get VIN year code for a given year"""
        # VIN year codes cycle every 30 years
        year_codes = {
            2024: 'P', 2023: 'N', 2022: 'M', 2021: 'L', 2020: 'K',
            2019: 'J', 2018: 'H', 2017: 'G', 2016: 'F', 2015: 'E',
            2014: 'D', 2013: 'C', 2012: 'B', 2011: 'A', 2010: '9',
            2009: '8', 2008: '7', 2007: '6', 2006: '5', 2005: '4',
            2004: '3', 2003: '2', 2002: '1', 2001: 'Y', 2000: 'X',
            1999: 'W', 1998: 'V', 1997: 'T', 1996: 'S', 1995: 'R',
            1994: 'P', 1993: 'N', 1992: 'M', 1991: 'L', 1990: 'K',
            1989: 'J', 1988: 'H', 1987: 'G', 1986: 'F', 1985: 'E',
            1984: 'D', 1983: 'C', 1982: 'B', 1981: 'A'
        }
        return year_codes.get(year)
    
    def find_real_vins_from_patterns(self, patterns: List[str]) -> List[Dict]:
        """Try to find real VINs by testing patterns against NHTSA API"""
        real_vins = []
        
        for pattern in patterns:
            try:
                # Test with wildcard VIN decode
                decoded = self.decode_vin_pattern(pattern)
                if decoded and self.is_valid_decode(decoded):
                    real_vins.append({
                        'vin': pattern,
                        'specs': decoded
                    })
                
                # Rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Error testing pattern {pattern}: {e}")
                continue
        
        return real_vins
    
    def decode_vin_pattern(self, vin_pattern: str) -> Optional[Dict]:
        """Decode a VIN pattern using NHTSA API"""
        url = f'{self.base_url}/vehicles/DecodeVinValues/{vin_pattern}?format=json'
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('Results') and len(data['Results']) > 0:
                return data['Results'][0]
        except Exception:
            pass
        
        return None
    
    def is_valid_decode(self, decoded_data: Dict) -> bool:
        """Check if decoded data represents a valid vehicle"""
        # Check for key fields
        required_fields = ['Make', 'Model', 'ModelYear']
        for field in required_fields:
            value = decoded_data.get(field)
            if not value or value in ['', 'Not Applicable', 'N/A']:
                return False
        
        # Check error codes
        error_code = decoded_data.get('ErrorCode', '0')
        if error_code != '0':
            return False
        
        return True
    
    def get_known_vins_for_make_model_year(self, make_name: str, model_name: str, year: int) -> List[str]:
        """Get known VINs for testing (this would be populated from a database in practice)"""
        # This is a placeholder - in practice you'd have a database of known VINs
        # or use pattern matching with actual VIN databases
        
        sample_vins = {
            ('FORD', 'F-150', 2021): ['1FTMW1T88MFA12345'],
            ('HONDA', 'CIVIC', 2020): ['2HGFE2F50LH123456'],
            ('TOYOTA', 'CAMRY', 2019): ['4T1B11HK5KU123456'],
            ('CHEVROLET', 'CORVETTE', 2020): ['1G1YB2D40L5123456'],
            ('BMW', '3 SERIES', 2021): ['WBA8E9C50M7123456'],
            ('TESLA', 'MODEL 3', 2021): ['5YJ3E1EA4MF123456'],
        }
        
        key = (make_name.upper(), model_name.upper(), year)
        return sample_vins.get(key, [])


def main():
    """Example usage of VIN pattern generator"""
    generator = VINPatternGenerator()
    
    # Test with some common vehicles
    test_cases = [
        ('Ford', 'F-150', 2021),
        ('Honda', 'Civic', 2020),
        ('Toyota', 'Camry', 2019),
        ('Chevrolet', 'Silverado', 2020),
    ]
    
    for make, model, year in test_cases:
        print(f"\nTesting {make} {model} {year}:")
        print("-" * 40)
        
        # Get WMI patterns
        wmis = generator.get_wmi_for_make(make)
        print(f"WMI patterns: {wmis[:3]}")
        
        # Generate VIN patterns
        patterns = generator.generate_vin_patterns(make, model, year, 3)
        print(f"Generated patterns: {patterns}")
        
        # Test patterns (commented out to avoid API calls in example)
        # real_vins = generator.find_real_vins_from_patterns(patterns)
        # print(f"Valid VINs found: {len(real_vins)}")


if __name__ == "__main__":
    main()
