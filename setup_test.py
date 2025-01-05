import os
import sys
from datetime import datetime, timedelta
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

def test_config_file():
    """Test if config file exists and is properly filled out."""
    print("\n1. Testing configuration file...")
    
    try:
        from config import (
            HOME_LOCATION,
            SPOTIFY_CLIENT_ID,
            SPOTIFY_CLIENT_SECRET,
            SEATGEEK_CLIENT_ID,
            SEATGEEK_CLIENT_SECRET
        )
        
        print("✓ Config file found")
        
        if HOME_LOCATION == "City, Country":
            print("✗ HOME_LOCATION needs to be set")
            return False
        else:
            print(f"✓ Home location set to: {HOME_LOCATION}")
            
        if "your_spotify_client_id" in [SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET]:
            print("✗ Spotify credentials need to be set")
            return False
        else:
            print("✓ Spotify credentials found")
            
        if "your_seatgeek_client_id" in [SEATGEEK_CLIENT_ID, SEATGEEK_CLIENT_SECRET]:
            print("✗ SeatGeek credentials need to be set")
            return False
        else:
            print("✓ SeatGeek credentials found")
            
        return True
        
    except ImportError:
        print("✗ Config file not found. Copy config_template.py to config.py and fill in your details")
        return False
    except Exception as e:
        print(f"✗ Error in config file: {e}")
        return False

def test_google_calendar():
    """Test Google Calendar API setup."""
    print("\n2. Testing Google Calendar connection...")
    
    if not os.path.exists('credentials.json'):
        print("✗ credentials.json not found")
        return False
        
    try:
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Test API by getting next week's events
        now = datetime.utcnow()
        next_week = now + timedelta(days=7)
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=next_week.isoformat() + 'Z',
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        print("✓ Successfully connected to Google Calendar")
        print(f"✓ Found {len(events_result.get('items', []))} events in the next week")
        return True
        
    except Exception as e:
        print(f"✗ Error connecting to Google Calendar: {e}")
        return False

def test_spotify():
    """Test Spotify API connection."""
    print("\n3. Testing Spotify connection...")
    
    try:
        from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
        
        # Clear any existing cache
        cache_files = [f for f in os.listdir('.') if f.startswith('.cache')]
        for f in cache_files:
            os.remove(f)
            
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri="http://localhost:8888/callback",
            scope="user-follow-read user-top-read",
            show_dialog=True
        )
        
        spotify = spotipy.Spotify(auth_manager=auth_manager)
        user = spotify.current_user()
        
        print(f"✓ Successfully connected to Spotify as: {user['display_name']}")
        
        # Test getting some artist data
        top_artists = spotify.current_user_top_artists(limit=1)
        if top_artists['items']:
            print(f"✓ Successfully retrieved artist data")
        
        return True
        
    except Exception as e:
        print(f"✗ Error connecting to Spotify: {e}")
        return False

def test_seatgeek():
    """Test SeatGeek API connection."""
    print("\n4. Testing SeatGeek connection...")
    
    try:
        from config import SEATGEEK_CLIENT_ID, SEATGEEK_CLIENT_SECRET
        
        # Test API with a simple search
        base_url = "https://api.seatgeek.com/2/events"
        params = {
            'client_id': SEATGEEK_CLIENT_ID,
            'client_secret': SEATGEEK_CLIENT_SECRET,
            'type': 'concert',
            'per_page': 1
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if 'events' in data:
            print("✓ Successfully connected to SeatGeek API")
            return True
            
    except Exception as e:
        print(f"✗ Error connecting to SeatGeek: {e}")
        return False

def print_help():
    """Print usage instructions."""
    print("\nUsage:")
    print("  python setup_test.py         - Run all tests")
    print("  python setup_test.py --clean - Clean up all cached credentials")
    print("  python setup_test.py --help  - Show this help message")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            print_help()
            return
        elif sys.argv[1] in ['--clean', '-c']:
            from cleanup import cleanup
            cleanup()
            return
            
    print("Running setup tests...")
    
    results = []
    results.append(("Configuration", test_config_file()))
    results.append(("Google Calendar", test_google_calendar()))
    results.append(("Spotify", test_spotify()))
    results.append(("SeatGeek", test_seatgeek()))
    
    print("\nTest Summary:")
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{name}: {status}")
        all_passed = all_passed and passed
    
    if all_passed:
        print("\nAll tests passed! You're ready to run concert_finder.py")
    else:
        print("\nSome tests failed. Please check the errors above and refer to README.md for setup instructions")
        
if __name__ == "__main__":
    main()
