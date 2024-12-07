import os
import requests
import time
from pathlib import Path
import json

class CryptoLogoDownloader:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.logos_dir = Path("coin_logos")
        self.metadata_file = self.logos_dir / "top100_metadata.json"
        self.headers = {
            'accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }

    def setup_directory(self):
        """Create logos directory if it doesn't exist"""
        self.logos_dir.mkdir(exist_ok=True)

    def get_top_100_coins(self):
        """Fetch top 100 coins by market cap from CoinGecko"""
        try:
            response = requests.get(
                f"{self.base_url}/coins/markets",
                params={
                    'vs_currency': 'usd',
                    'order': 'market_cap_desc',
                    'per_page': 100,
                    'page': 1,
                    'sparkline': 'false'
                },
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to fetch top coins. Status code: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching top coins: {e}")
            return []

    def download_logo(self, url, coin_id):
        """Download logo from URL"""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                # Get file extension from content type
                content_type = response.headers.get('content-type', '')
                ext = '.png' if 'png' in content_type else '.jpg'
                
                # Save the image
                file_path = self.logos_dir / f"{coin_id}{ext}"
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return str(file_path)
            else:
                print(f"Failed to download logo for {coin_id}. Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error downloading logo for {coin_id}: {e}")
            return None

    def save_metadata(self, metadata_dict):
        """Save metadata to JSON file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
            print(f"Metadata saved to {self.metadata_file}")
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def download_top_100_logos(self):
        """Main function to download top 100 logos"""
        self.setup_directory()
        coins = self.get_top_100_coins()
        
        if not coins:
            print("No coins found.")
            return
        
        print(f"Found {len(coins)} top coins. Starting download...")
        metadata_dict = {}
        
        for i, coin in enumerate(coins):
            coin_id = coin['id']
            print(f"\nProcessing {i+1}/100: {coin['name']} ({coin['symbol'].upper()})")
            
            # Rate limiting
            time.sleep(1)  # Respect API rate limits
            
            # Download logo
            logo_path = self.download_logo(coin['image'], coin_id)
            if not logo_path:
                continue
            
            # Store metadata
            metadata_dict[coin_id] = {
                'name': coin['name'],
                'symbol': coin['symbol'].upper(),
                'logo_path': logo_path,
                'market_cap_rank': coin['market_cap_rank'],
                'current_price': coin['current_price'],
                'market_cap': coin['market_cap'],
                'total_volume': coin['total_volume']
            }
            
            # Save metadata periodically
            if (i + 1) % 10 == 0:
                self.save_metadata(metadata_dict)
                print(f"Progress: {i+1}/100 coins processed")
        
        # Final save of metadata
        self.save_metadata(metadata_dict)
        print("\nDownload complete!")
        
        # Print summary
        print("\nSummary of downloaded coins:")
        print(f"Total coins processed: {len(metadata_dict)}")
        print(f"Logos directory: {self.logos_dir.absolute()}")
        print(f"Metadata file: {self.metadata_file.absolute()}")




def main():
    downloader = CryptoLogoDownloader()
    downloader.download_top_100_logos()

if __name__ == "__main__":
    main()