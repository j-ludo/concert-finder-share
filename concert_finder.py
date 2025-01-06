import os
import sys
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
from concert_apis import SeatGeekAPI, BandsInTownAPI, SongkickAPI
from typing import List, Dict
import itertools

class ConcertFinder:
    def __init__(self, selected_apis=None):
        """Initialize the concert finder with user-selected APIs."""
        # Check if config exists and run setup if needed
        if not os.path.exists('config.py'):
            print("\nConfiguration file not found. Running setup...")
            self.run_setup()
            
        # Import configuration
        try:
            from config import (
                HOME_LOCATION,
                SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
                SEATGEEK_CLIENT_ID, SEATGEEK_CLIENT_SECRET,
                BANDSINTOWN_APP_ID,
                SONGKICK_API_KEY
            )
            self.home_location = HOME_LOCATION
            self.enabled_apis = []
            
            # Available APIs and their initialization functions
            self.available_apis = {
                'seatgeek': lambda: SeatGeekAPI(SEATGEEK_CLIENT_ID, SEATGEEK_CLIENT_SECRET),
                'bandsintown': lambda: BandsInTownAPI(BANDSINTOWN_APP_ID),
                'songkick': lambda: SongkickAPI(SONGKICK_API_KEY)
            }
            
            # Initialize selected APIs
            if selected_apis is None:
                selected_apis = self.prompt_api_selection()
            
            for api_name in selected_apis:
                if api_name in self.available_apis:
                    try:
                        api = self.available_apis[api_name]()
                        self.enabled_apis.append(api)
                        print(f"{api_name.title()} API enabled")
                    except Exception as e:
                        print(f"Error initializing {api_name.title()} API: {e}")
            
            if not self.enabled_apis:
                raise ValueError("No concert APIs were successfully enabled")
            
            if not self.enabled_apis:
                raise ValueError("No concert APIs enabled. Enable at least one in config.py")
            
            self.spotify_client_id = SPOTIFY_CLIENT_ID
            self.spotify_client_secret = SPOTIFY_CLIENT_SECRET
            
        except ImportError:
            print("\nError: config.py not found!")
            print("Please run 'python setup_config.py' first to create your configuration.")
            sys.exit(1)
            
        print(f"\nUsing {self.home_location} as home location")
        self.setup_apis()
        
    def setup_apis(self):
        """Initialize Spotify and Google Calendar APIs."""
        try:
            self.setup_spotify()
            self.setup_google_calendar()
        except Exception as e:
            print(f"\nError setting up APIs: {e}")
            print("Try running 'python setup_test.py' to diagnose the issue.")
            sys.exit(1)
        
    def setup_spotify(self):
        """Initialize Spotify client."""
        try:
            # Clear any existing cache
            cache_files = [f for f in os.listdir('.') if f.startswith('.cache')]
            for f in cache_files:
                os.remove(f)
                
            self.auth_manager = SpotifyOAuth(
                client_id=self.spotify_client_id,
                client_secret=self.spotify_client_secret,
                redirect_uri="http://localhost:8888/callback",
                scope="user-follow-read user-top-read",
                show_dialog=True,
                open_browser=True
            )
            self.spotify = spotipy.Spotify(auth_manager=self.auth_manager)
            
            # Test connection
            user = self.spotify.current_user()
            print(f"Connected to Spotify as: {user['display_name']}")
            
        except Exception as e:
            print(f"Error connecting to Spotify: {e}")
            raise
    
    def setup_google_calendar(self):
        """Initialize Google Calendar API client."""
        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    print("\nError: credentials.json not found!")
                    print("Please download your Google Calendar API credentials")
                    print("and save them as 'credentials.json'")
                    sys.exit(1)
                    
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.calendar = build('calendar', 'v3', credentials=creds)
        print("Connected to Google Calendar")
        
    def get_favorite_artists(self) -> List[str]:
        """Get user's followed and top artists from Spotify."""
        print("\nFetching artists from Spotify...")
        
        # Get followed artists
        followed_artists = []
        results = self.spotify.current_user_followed_artists()
        
        while results:
            for item in results['artists']['items']:
                followed_artists.append(item['name'])
            if results['artists']['next']:
                results = self.spotify.next(results['artists'])
            else:
                results = None
                
        # Get top artists
        top_artists = self.spotify.current_user_top_artists(limit=50, time_range='long_term')
        for artist in top_artists['items']:
            if artist['name'] not in followed_artists:
                followed_artists.append(artist['name'])
                
        print(f"Found {len(followed_artists)} artists to search for")
        return followed_artists
        
    def get_travel_periods(self) -> List[Dict]:
        """Get periods of time and their locations from calendar."""
        print("\nFetching travel dates from Google Calendar...")
        
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=365)  # Look ahead one year
        
        events_result = self.calendar.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        travel_periods = []
        for event in events_result.get('items', []):
            if 'location' in event and event['location'] != self.home_location:
                travel_periods.append({
                    'location': event['location'],
                    'start': event['start'].get('dateTime', event['start'].get('date')),
                    'end': event['end'].get('dateTime', event['end'].get('date'))
                })
        
        print(f"Found {len(travel_periods)} travel periods")
        return travel_periods
        
    def search_concerts(self, artist: str, location: str, start_date: str, end_date: str) -> List[Dict]:
        """Search for concerts across all enabled APIs."""
        all_concerts = []
        
        for api in self.enabled_apis:
            try:
                concerts = api.search_concerts(artist, location, start_date, end_date)
                all_concerts.extend(concerts)
            except Exception as e:
                print(f"Error searching concerts with {api.__class__.__name__}: {e}")
        
        return all_concerts
            
    def find_concerts(self) -> List[Dict]:
        """Main method to find concerts matching travel schedule."""
        print("\nStarting concert search...")
        
        artists = self.get_favorite_artists()
        travel_periods = self.get_travel_periods()
        
        if not travel_periods:
            print("\nNo travel periods found in calendar.")
            return []
            
        matching_concerts = []
        total_searches = len(artists) * len(travel_periods) * len(self.enabled_apis)
        searches_completed = 0
        
        for period in travel_periods:
            print(f"\nSearching concerts in {period['location']}")
            print(f"From {period['start']} to {period['end']}")
            
            for artist in artists:
                concerts = self.search_concerts(
                    artist,
                    period['location'],
                    period['start'],
                    period['end']
                )
                matching_concerts.extend(concerts)
                
                searches_completed += 1
                progress = (searches_completed / total_searches) * 100
                print(f"Search progress: {progress:.1f}%", end='\r')
        
        # Remove duplicates (same artist, venue, and date)
        unique_concerts = []
        seen = set()
        
        for concert in matching_concerts:
            key = (concert['artist'], concert['venue'], concert['date'])
            if key not in seen:
                seen.add(key)
                unique_concerts.append(concert)
        
        print("\nSearch completed!")
        return unique_concerts

    def run_setup(self):
        """Run the configuration setup."""
        try:
            import setup_config
            setup_config.create_config()
            print("\nSetup completed. Continuing with program...")
        except Exception as e:
            print(f"\nError during setup: {e}")
            print("Please run 'python setup_config.py' manually to configure the program.")
            sys.exit(1)
            
    def check_api_credentials(self, api_name: str) -> bool:
        """Check if required credentials are available for an API."""
        try:
            from config import (
                SEATGEEK_CLIENT_ID, SEATGEEK_CLIENT_SECRET,
                BANDSINTOWN_APP_ID,
                SONGKICK_API_KEY
            )
            
            if api_name == 'seatgeek':
                return bool(SEATGEEK_CLIENT_ID and SEATGEEK_CLIENT_SECRET)
            elif api_name == 'bandsintown':
                return bool(BANDSINTOWN_APP_ID)
            elif api_name == 'songkick':
                return bool(SONGKICK_API_KEY)
            return False
            
        except ImportError:
            return False
        except AttributeError:
            return False

    def prompt_api_selection(self) -> List[str]:
        """Prompt user to select which concert APIs to use."""
        print("\nAvailable Concert APIs:")
        apis = list(self.available_apis.keys())
        
        # Check credentials before showing options
        available_apis = []
        for i, api in enumerate(apis, 1):
            has_credentials = self.check_api_credentials(api)
            status = "✓" if has_credentials else "✗"
            print(f"{i}. {api.title()} {status}")
            if has_credentials:
                available_apis.append(api)
        
        if not available_apis:
            print("\nNo APIs are currently available. Please check your credentials in config.py")
            sys.exit(1)
        
        print("\nNote: ✓ = configured, ✗ = missing credentials")
        
        while True:
            try:
                selection = input("\nEnter numbers for APIs to use (separated by spaces, or 'all'): ").strip().lower()
                
                if selection == 'all':
                    return available_apis
                
                # Convert input to list of API names
                numbers = [int(x) for x in selection.split()]
                selected_apis = []
                
                for num in numbers:
                    if 1 <= num <= len(apis):
                        api_name = apis[num-1]
                        if api_name in available_apis:
                            selected_apis.append(api_name)
                        else:
                            print(f"Cannot use {api_name.title()}: missing credentials")
                    else:
                        print(f"Invalid number: {num}. Please use numbers 1-{len(apis)}")
                        break
                else:
                    if selected_apis:
                        return selected_apis
                    
                print("Please select at least one available API")
                
            except ValueError:
                print("Please enter valid numbers separated by spaces, or 'all'")
            except KeyboardInterrupt:
                print("\nSetup cancelled by user")
                sys.exit(0)

    def init_api(self, api_name: str):
        """Initialize a single API with error handling."""
        try:
            api = self.available_apis[api_name]()
            # Test API connection
            if hasattr(api, 'test_connection'):
                api.test_connection()
            return api
        except Exception as e:
            print(f"\nError initializing {api_name.title()} API:")
            print(f"  → {str(e)}")
            return None

def format_concert_output(concert: Dict) -> str:
    """Format a concert dictionary into a readable string."""
    output = [
        f"\n{concert['artist']} ({concert['source']})",
        f"Venue: {concert['venue']}",
        f"Date: {concert['date']}"
    ]
    
    if concert['lowest_price'] != 'N/A':
        output.append(f"Price Range: ${concert['lowest_price']} - ${concert['highest_price']}")
    
    output.append(f"Tickets: {concert['tickets_url']}")
    return "\n".join(output)

def main():
    try:
        print("\nWelcome to Concert Finder!")
        finder = ConcertFinder()
        
        if not finder.enabled_apis:
            print("\nNo APIs were successfully enabled. Please check your configuration and try again.")
            return
            
        concerts = finder.find_concerts()
        
        if concerts:
            print("\nFound concerts during your travels!")
            # Sort concerts by date
            concerts.sort(key=lambda x: x['date'])
            
            # Group concerts by location
            from itertools import groupby
            by_location = {}
            
            for concert in concerts:
                location = concert['venue'].split(' - ')[1]
                if location not in by_location:
                    by_location[location] = []
                by_location[location].append(concert)
            
            # Print concerts grouped by location
            for location, location_concerts in by_location.items():
                print(f"\n=== Concerts in {location} ===")
                for concert in location_concerts:
                    print(format_concert_output(concert))
                
            print(f"\nTotal concerts found: {len(concerts)}")
            print(f"Total locations: {len(by_location)}")
        else:
            print("\nNo matching concerts found for your favorite artists during your travels.")
            
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("\nIf you're seeing authentication errors, try:")
        print("1. Run 'python cleanup.py' to clear cached credentials")
        print("2. Run 'python setup_test.py' to verify your setup")
        print("3. Try running the program again")

if __name__ == "__main__":
    main()
