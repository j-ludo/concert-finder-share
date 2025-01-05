import os
import sys
from datetime import datetime, timedelta
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle

class ConcertFinder:
    def __init__(self):
        # Import configuration
        try:
            from config import (
                HOME_LOCATION,
                SPOTIFY_CLIENT_ID,
                SPOTIFY_CLIENT_SECRET,
                SEATGEEK_CLIENT_ID,
                SEATGEEK_CLIENT_SECRET
            )
            self.home_location = HOME_LOCATION
            self.spotify_client_id = SPOTIFY_CLIENT_ID
            self.spotify_client_secret = SPOTIFY_CLIENT_SECRET
            self.seatgeek_client_id = SEATGEEK_CLIENT_ID
            self.seatgeek_client_secret = SEATGEEK_CLIENT_SECRET
            
        except ImportError:
            print("\nError: config.py not found!")
            print("Please run 'python setup_config.py' first to create your configuration.")
            sys.exit(1)
            
        print(f"\nUsing {self.home_location} as home location")
        self.setup_apis()
        
    def setup_apis(self):
        """Initialize all API connections."""
        try:
            self.setup_spotify()
            self.setup_google_calendar()
            self.setup_seatgeek()
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
        
    def setup_seatgeek(self):
        """Set up SeatGeek API credentials."""
        self.seatgeek_base_url = "https://api.seatgeek.com/2"
        print("SeatGeek API configured")
        
    def get_favorite_artists(self):
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
        
    def get_travel_periods(self):
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
        
    def search_concerts(self, artist, location, start_date, end_date):
        """Search for concerts using SeatGeek API."""
        # Format dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Extract city from location
        city = location.split(',')[0].strip()
        
        params = {
            'client_id': self.seatgeek_client_id,
            'client_secret': self.seatgeek_client_secret,
            'q': artist,
            'type': 'concert',
            'datetime_local.gte': start.strftime('%Y-%m-%d'),
            'datetime_local.lte': end.strftime('%Y-%m-%d'),
            'venue.city': city,
            'per_page': 100
        }
        
        try:
            response = requests.get(f"{self.seatgeek_base_url}/events", params=params)
            response.raise_for_status()
            events = response.json()
            
            matching_events = []
            for event in events.get('events', []):
                if any(performer['name'].lower() == artist.lower() 
                      for performer in event['performers']):
                    matching_events.append({
                        "artist": artist,
                        "venue": f"{event['venue']['name']} - {event['venue']['city']}, {event['venue']['state']}",
                        "date": event['datetime_local'],
                        "tickets_url": event['url'],
                        "lowest_price": event.get('stats', {}).get('lowest_price', 'N/A'),
                        "highest_price": event.get('stats', {}).get('highest_price', 'N/A')
                    })
            
            return matching_events
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching concerts for {artist}: {e}")
            return []
            
    def find_concerts(self):
        """Main method to find concerts matching travel schedule."""
        print("\nStarting concert search...")
        
        artists = self.get_favorite_artists()
        travel_periods = self.get_travel_periods()
        
        if not travel_periods:
            print("\nNo travel periods found in calendar.")
            return []
            
        matching_concerts = []
        total_searches = len(artists) * len(travel_periods)
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
        
        print("\nSearch completed!")
        return matching_concerts

def main():
    try:
        finder = ConcertFinder()
        concerts = finder.find_concerts()
        
        if concerts:
            print("\nFound concerts during your travels!")
            concerts.sort(key=lambda x: x['date'])
            
            for concert in concerts:
                print(f"\n{concert['artist']}")
                print(f"Venue: {concert['venue']}")
                print(f"Date: {concert['date']}")
                if concert['lowest_price'] != 'N/A':
                    print(f"Price Range: ${concert['lowest_price']} - ${concert['highest_price']}")
                print(f"Tickets: {concert['tickets_url']}")
                
            print(f"\nTotal concerts found: {len(concerts)}")
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
