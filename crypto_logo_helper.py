import json
from pathlib import Path
import requests
import time
import os
import re

class CryptoLogoManager:
    def __init__(self):
        self.logos_dir = Path("coin_logos")
        self.metadata_file = self.logos_dir / "top100_metadata.json"
        self.logos_dir.mkdir(exist_ok=True)  # Ensure directory exists
        self.metadata = self._load_metadata()
        self.api_base_url = "https://api.coingecko.com/api/v3"
        self.headers = {
            'accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }
        
        # Define coin relationships
        self.coin_relationships = {
            'pol': {
                'primary_symbol': 'matic',
                'coingecko_id': 'matic-network',  # Important: Add CoinGecko IDs
                'aliases': ['polygon', 'matic', 'pol'],
                'historical': ['matic']
            },
            'matic': {
                'primary_symbol': 'matic',
                'coingecko_id': 'matic-network',
                'aliases': ['polygon', 'matic', 'pol'],
                'historical': ['matic']
            },
            # Add more mappings as needed
        }

    def _load_metadata(self):
        """Load metadata from JSON file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return {}

    def _save_metadata(self):
        """Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def _get_coin_info(self, symbol):
        """Get coin info from CoinGecko API"""
        try:
            # First try direct symbol lookup
            response = requests.get(
                f"{self.api_base_url}/search",
                params={'query': symbol},
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                coins = data.get('coins', [])
                
                # First, try to find an exact symbol match
                for coin in coins:
                    if coin['symbol'].lower() == symbol.lower():
                        return coin['id']
                
                # If no exact match, return the first result if available
                if coins:
                    return coins[0]['id']
                
            return None
        except Exception as e:
            print(f"Error getting coin info: {e}")
            return None

    def _fetch_and_save_logo(self, coin_id):
        """Fetch logo from CoinGecko and save locally"""
        try:
            response = requests.get(
                f"{self.api_base_url}/coins/{coin_id}",
                params={
                    'localization': 'false',
                    'tickers': 'false',
                    'market_data': 'false',
                    'community_data': 'false',
                    'developer_data': 'false',
                    'sparkline': 'false'
                },
                headers=self.headers
            )
            
            if response.status_code == 200:
                coin_data = response.json()
                if 'image' in coin_data and 'small' in coin_data['image']:
                    # Download the logo
                    logo_url = coin_data['image']['small']
                    logo_response = requests.get(logo_url, headers=self.headers)
                    
                    if logo_response.status_code == 200:
                        # Determine file extension from content type
                        content_type = logo_response.headers.get('content-type', '')
                        ext = '.png' if 'png' in content_type else '.jpg'
                        
                        # Save the logo
                        logo_path = self.logos_dir / f"{coin_id}{ext}"
                        with open(logo_path, 'wb') as f:
                            f.write(logo_response.content)
                        
                        # Update metadata
                        self.metadata[coin_id] = {
                            'name': coin_data['name'],
                            'symbol': coin_data['symbol'].upper(),
                            'logo_path': str(logo_path)
                        }
                        self._save_metadata()
                        
                        return str(logo_path)
            
            return None
        except Exception as e:
            print(f"Error fetching logo: {e}")
            return None

    def _extract_name_and_symbol(self, coin_string):
        """Extract both name and symbol from string"""
        match = re.match(r'^(.*?)\s*(?:\((?:ex-)?([^)]+)\))?\s*(?:\(([^)]+)\))?$', coin_string)
        if match:
            name = match.group(1).strip().lower()
            old_symbol = match.group(2).lower() if match.group(2) else None
            current_symbol = match.group(3).lower() if match.group(3) else None
            return name, old_symbol, current_symbol
        return coin_string.lower(), None, None

    def get_logo_path(self, coin_string):
        """Get logo path for a given coin name, fetching from API if needed"""
        name, old_symbol, current_symbol = self._extract_name_and_symbol(coin_string)
        
        # Try to get symbol from relationships
        for symbol in [current_symbol, old_symbol, name]:
            if symbol in self.coin_relationships:
                relationship = self.coin_relationships[symbol]
                coin_id = relationship.get('coingecko_id')
                if coin_id:
                    # Check if we have it locally
                    if coin_id in self.metadata:
                        logo_path = self.metadata[coin_id]['logo_path']
                        if os.path.exists(logo_path):
                            return logo_path
                    
                    # If not found locally, fetch from API
                    logo_path = self._fetch_and_save_logo(coin_id)
                    if logo_path:
                        return logo_path
        
        # If not in relationships, try to find by symbol
        search_symbols = [s for s in [current_symbol, old_symbol, name] if s]
        for symbol in search_symbols:
            coin_id = self._get_coin_info(symbol)
            if coin_id:
                # Check if we have it locally
                if coin_id in self.metadata:
                    logo_path = self.metadata[coin_id]['logo_path']
                    if os.path.exists(logo_path):
                        return logo_path
                
                # If not found locally, fetch from API
                logo_path = self._fetch_and_save_logo(coin_id)
                if logo_path:
                    return logo_path
        
        return None

def get_crypto_logo(coin_name):
    """
    Get logo path for a cryptocurrency, fetching from API if needed.
    Args:
        coin_name (str): Name or symbol of the cryptocurrency
    Returns:
        str: Path to the logo file or None if not found
    """
    logo_manager = CryptoLogoManager()
    return logo_manager.get_logo_path(coin_name)

# Example usage
if __name__ == "__main__":
    test_coins = [
        'Polygon (MATIC)',
        'POL (ex-MATIC) (POL)',
        'Bitcoin (BTC)',
        'Ethereum (ETH)',
        'LayerZero (ZRO)'
    ]
    
    for coin in test_coins:
        print(f"\nTesting: {coin}")
        logo_path = get_crypto_logo(coin)
        if logo_path:
            print(f"Found logo: {logo_path}")
        else:
            print("No logo found")