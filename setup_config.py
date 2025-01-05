import os
import sys

def create_config():
    """Interactive configuration file creation."""
    print("\nWelcome to Concert Finder Setup!")
    print("This script will help you create your configuration file.")
    
    if os.path.exists('config.py'):
        response = input("\nconfig.py already exists. Do you want to recreate it? (yes/no): ").lower()
        if response != 'yes':
            print("Setup cancelled. Your existing config.py was kept.")
            return
    
    print("\nPlease provide the following information:")
    
    # Get home location
    print("\nWhat is your home location?")
    print("Format: City, Country (e.g., 'New York, USA' or 'London, UK')")
    home_location = input("Home Location: ").strip()
    
    # Get Spotify credentials
    print("\nSpotify API Credentials")
    print("(Get these from https://developer.spotify.com/dashboard)")
    spotify_client_id = input("Spotify Client ID: ").strip()
    spotify_client_secret = input("Spotify Client Secret: ").strip()
    
    # Get SeatGeek credentials
    print("\nSeatGeek API Credentials")
    print("(Get these from https://seatgeek.com/account/develop)")
    seatgeek_client_id = input("SeatGeek Client ID: ").strip()
    seatgeek_client_secret = input("SeatGeek Client Secret: ").strip()
    
    # Create config file
    config_content = f'''# Home location setting
HOME_LOCATION = "{home_location}"

# Spotify API credentials
SPOTIFY_CLIENT_ID = "{spotify_client_id}"
SPOTIFY_CLIENT_SECRET = "{spotify_client_secret}"

# SeatGeek API credentials
SEATGEEK_CLIENT_ID = "{seatgeek_client_id}"
SEATGEEK_CLIENT_SECRET = "{seatgeek_client_secret}"
'''
    
    try:
        with open('config.py', 'w') as f:
            f.write(config_content)
        print("\nConfiguration file (config.py) has been created successfully!")
        print("\nNext steps:")
        print("1. Set up Google Calendar API and download credentials.json")
        print("2. Run setup_test.py to verify everything is working")
        print("3. Run concert_finder.py to start finding concerts!")
        
    except Exception as e:
        print(f"\nError creating config file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_config()
