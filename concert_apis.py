from abc import ABC, abstractmethod
from datetime import datetime
import requests
from typing import List, Dict, Optional

class ConcertAPI(ABC):
    """Base class for concert API providers"""
    
    @abstractmethod
    def search_concerts(self, artist: str, location: str, start_date: str, end_date: str) -> List[Dict]:
        """Search for concerts by artist and location within date range"""
        pass

class SeatGeekAPI(ConcertAPI):
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.seatgeek.com/2"
    
    def search_concerts(self, artist: str, location: str, start_date: str, end_date: str) -> List[Dict]:
        """Search concerts using SeatGeek API"""
        # Format dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Extract city from location
        city = location.split(',')[0].strip()
        
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'q': artist,
            'type': 'concert',
            'datetime_local.gte': start.strftime('%Y-%m-%d'),
            'datetime_local.lte': end.strftime('%Y-%m-%d'),
            'venue.city': city,
            'per_page': 100
        }
        
        try:
            response = requests.get(f"{self.base_url}/events", params=params)
            response.raise_for_status()
            events = response.json()
            
            matching_events = []
            for event in events.get('events', []):
                if any(performer['name'].lower() == artist.lower() 
                      for performer in event['performers']):
                    matching_events.append({
                        "source": "SeatGeek",
                        "artist": artist,
                        "venue": f"{event['venue']['name']} - {event['venue']['city']}, {event['venue']['state']}",
                        "date": event['datetime_local'],
                        "tickets_url": event['url'],
                        "lowest_price": event.get('stats', {}).get('lowest_price', 'N/A'),
                        "highest_price": event.get('stats', {}).get('highest_price', 'N/A')
                    })
            
            return matching_events
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching SeatGeek for {artist}: {e}")
            return []

class BandsInTownAPI(ConcertAPI):
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.base_url = "https://rest.bandsintown.com/artists"
    
    def search_concerts(self, artist: str, location: str, start_date: str, end_date: str) -> List[Dict]:
        """Search concerts using Bandsintown API"""
        # Format dates for Bandsintown API
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        url = f"{self.base_url}/{artist}/events"
        params = {
            "app_id": self.app_id,
            "date": f"{start.strftime('%Y-%m-%d')},{end.strftime('%Y-%m-%d')}"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            events = response.json()
            
            # Filter events by location
            city = location.split(',')[0].strip().lower()
            matching_events = []
            
            for event in events:
                event_city = event['venue']['city'].lower()
                if city in event_city:
                    matching_events.append({
                        "source": "Bandsintown",
                        "artist": artist,
                        "venue": f"{event['venue']['name']} - {event['venue']['city']}, {event['venue']['country']}",
                        "date": event['datetime'],
                        "tickets_url": event.get('url', 'N/A'),
                        "lowest_price": 'N/A',  # Bandsintown doesn't provide pricing
                        "highest_price": 'N/A'
                    })
            
            return matching_events
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching Bandsintown for {artist}: {e}")
            return []

class SongkickAPI(ConcertAPI):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.songkick.com/api/3.0"
    
    def search_concerts(self, artist: str, location: str, start_date: str, end_date: str) -> List[Dict]:
        """Search concerts using Songkick API"""
        # First get location ID
        city = location.split(',')[0].strip()
        location_id = self._get_location_id(city)
        
        if not location_id:
            return []
        
        # Format dates
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        params = {
            'apikey': self.api_key,
            'location': f'sk:{location_id}',
            'min_date': start.strftime('%Y-%m-%d'),
            'max_date': end.strftime('%Y-%m-%d')
        }
        
        try:
            response = requests.get(f"{self.base_url}/events.json", params=params)
            response.raise_for_status()
            data = response.json()
            
            matching_events = []
            for event in data.get('resultsPage', {}).get('results', {}).get('event', []):
                if any(performer['displayName'].lower() == artist.lower() 
                      for performer in event['performance']):
                    matching_events.append({
                        "source": "Songkick",
                        "artist": artist,
                        "venue": f"{event['venue']['displayName']} - {event['location']['city']}",
                        "date": event['start']['datetime'] or event['start']['date'],
                        "tickets_url": event.get('uri', 'N/A'),
                        "lowest_price": 'N/A',  # Songkick doesn't provide pricing
                        "highest_price": 'N/A'
                    })
            
            return matching_events
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching Songkick for {artist}: {e}")
            return []
    
    def _get_location_id(self, city: str) -> Optional[str]:
        """Get Songkick location ID for a city"""
        params = {
            'apikey': self.api_key,
            'query': city
        }
        
        try:
            response = requests.get(f"{self.base_url}/search/locations.json", params=params)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('resultsPage', {}).get('results', {}).get('location', [])
            if results:
                return str(results[0]['metroArea']['id'])
                
        except requests.exceptions.RequestException as e:
            print(f"Error getting Songkick location ID for {city}: {e}")
        
        return None
