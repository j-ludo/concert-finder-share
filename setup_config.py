    """Interactive configuration file creation."""
    print("\nWelcome to Concert Finder Setup!")

    # Google Calendar Setup
    print("\n=== Google Calendar Setup ===")
    print("Google Calendar is required for finding your travel dates.")
    print("\nTo set up Google Calendar:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a project or select your existing one")
    print("3. Enable the Google Calendar API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Google Calendar API'")
    print("   - Click 'Enable'")
    print("4. Set up credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - Choose 'Desktop application'")
    print("   - Download the JSON file")
    print("   - Save it as 'credentials.json' in this folder")

    while not os.path.exists('credentials.json'):
        input("\nPress Enter after you've saved credentials.json in this folder...")
        if not os.path.exists('credentials.json'):
            if not get_yes_no_input("credentials.json not found. Would you like to try again?"):
                print("You'll need Google Calendar credentials to use this program.")
                sys.exit(1)
    
    print("\nGoogimport os
import sys

def get_yes_no_input(prompt: str) -> bool:
    """Get a yes/no answer from the user."""
    while True:
        response = input(f"{prompt} (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        if response in ['no', 'n']:
            return False
        print("Please answer 'yes' or 'no'")

def create_config():
    """Interactive configuration file creation."""
    print("\nWelcome to Concert Finder Setup!")
    
    if os.path.exists('config.py'):
        if not get_yes_no_input("\nconfig.py already exists. Do you want to recreate it?"):
            print("Setup cancelled. Your existing config.py was kept.")
            return
    
    config_content = []
    
    # Get home location
    print("\nWhat is your home location?")
    print("Format: City, Country (e.g., 'New York, USA' or 'London, UK')")
    home_location = input("Home Location: ").strip()
    config_content.append(f'HOME_LOCATION = "{home_location}"')
    
    # Spotify setup
    print("\nSpotify is required for finding your favorite artists.")
    if get_yes_no_input("Do you have Spotify API credentials?"):
        print("\nGet these from https://developer.spotify.com/dashboard")
        spotify_client_id = input("Spotify Client ID: ").strip()
        spotify_client_secret = input("Spotify Client Secret: ").strip()
    else:
        print("You'll need Spotify credentials to use this program.")
        print("Please visit https://developer.spotify.com/dashboard to set them up.")
        spotify_client_id = ""
        spotify_client_secret = ""
    
    config_content.extend([
        f'SPOTIFY_CLIENT_ID = "{spotify_client_id}"',
        f'SPOTIFY_CLIENT_SECRET = "{spotify_client_secret}"'
    ])
    
    # SeatGeek setup
    if get_yes_no_input("\nWould you like to use SeatGeek for concert searches?"):
        print("\nGet these from https://seatgeek.com/account/develop")
        seatgeek_client_id = input("SeatGeek Client ID: ").strip()
        seatgeek_client_secret = input("SeatGeek Client Secret: ").strip()
    else:
        seatgeek_client_id = ""
        seatgeek_client_secret = ""
    
    config_content.extend([
        f'SEATGEEK_CLIENT_ID = "{seatgeek_client_id}"',
        f'SEATGEEK_CLIENT_SECRET = "{seatgeek_client_secret}"'
    ])
    
    # Bandsintown setup
    if get_yes_no_input("\nWould you like to use Bandsintown for concert searches?"):
        print("\nGet this from https://www.bandsintown.com/api")
        bandsintown_app_id = input("Bandsintown App ID: ").strip()
    else:
        bandsintown_app_id = ""
    
    config_content.append(f'BANDSINTOWN_APP_ID = "{bandsintown_app_id}"')
    
    # Songkick setup
    if get_yes_no_input("\nWould you like to use Songkick for concert searches?"):
        print("\nGet this from https://www.songkick.com/developer")
        songkick_api_key = input("Songkick API Key: ").strip()
    else:
        songkick_api_key = ""
    
    config_content.append(f'SONGKICK_API_KEY = "{songkick_api_key}"')
    
    # Write the config file
    try:
        with open('config.py', 'w') as f:
            f.write('\n'.join(config_content))
        print("\nConfiguration file (config.py) has been created successfully!")
        
        # Check if any concert APIs were configured
        if not any([seatgeek_client_id, bandsintown_app_id, songkick_api_key]):
            print("\nWARNING: No concert APIs were configured.")
            print("You'll need at least one concert API to search for shows.")
            print("You can run this setup again later to add API credentials.")
        
        if not spotify_client_id:
            print("\nWARNING: Spotify credentials are required for this program to work.")
            print("Please set up Spotify credentials and run setup again.")
        
    except Exception as e:
        print(f"\nError creating config file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_config()
