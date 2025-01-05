# Concert Finder

**ask claude.ai for help with any of these steps and feed back in errors you get for corrections**
**also make sure you let claude know the names and directories you are using as you go, any info you don't want to manually change it'll keep track of**


A program that finds concerts by your favorite Spotify artists in cities you'll be visiting, based on your Google Calendar events.

## Quick Start

1. Install required packages:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client spotipy requests
```

2. Run the interactive setup:
```bash
python setup_config.py
```

3. Set up Google Calendar API (see detailed instructions below)

4. Verify your setup:
```bash
python setup_test.py
```

5. Run the program:
```bash
python concert_finder.py
```

## Detailed Setup Instructions

### 1. Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"
4. Set up OAuth consent screen:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External"
   - Fill in required information (App name, user support email, developer contact email)
5. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop application"
   - Download the JSON file
   - Save it as `credentials.json` in your project folder

### 2. Spotify API Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in and create a new app
3. Fill in:
   - App name (e.g., "Concert Finder")
   - Description
   - Redirect URI: `http://localhost:8888/callback`
4. Note down your Client ID and Client Secret

### 3. SeatGeek API Setup

1. Go to [SeatGeek Developer](https://seatgeek.com/account/develop)
2. Create a new application
3. Note down your Client ID and Client Secret

## Configuration

Run the interactive setup script:
```bash
python setup_config.py
```

This will prompt you for:
- Your home location (e.g., "New York, USA")
- Spotify credentials
- SeatGeek credentials

## Testing Your Setup

Run the test script to verify everything is working:
```bash
python setup_test.py
```

This will check:
- Configuration file
- Google Calendar connection
- Spotify connection
- SeatGeek API access

## Usage

1. Add events with locations to your Google Calendar for your travels
2. Run the program:
```bash
python concert_finder.py
```

The program will:
- Get your favorite artists from Spotify
- Check your travel dates from Google Calendar
- Find concerts in cities you're visiting
- Show details including venue, date, and ticket links

## Troubleshooting

If you encounter issues:

1. Run the cleanup script to reset all credentials:
```bash
python cleanup.py
```

2. Verify your setup:
```bash
python setup_test.py
```

3. Common issues:
   - Authentication errors: Run cleanup.py and try again
   - "Invalid client" error: Check your API credentials
   - Calendar errors: Verify credentials.json is in the project folder

## Available Scripts

- `concert_finder.py` - Main program
- `setup_config.py` - Interactive configuration setup
- `setup_test.py` - Test your configuration and API connections
- `cleanup.py` - Reset authentication and cached data

Extra options:
- `python cleanup.py --force` - Skip confirmation prompt
- `python setup_test.py --clean` - Run cleanup through test script

## Privacy Note

This is a personal tool that runs locally on your computer. Your credentials and data remain private and are only used to access the respective APIs.

## Notes

- The program looks for concerts during any calendar event with a location different from your home location
- It combines both your followed artists and top artists from Spotify
- Concerts are sorted by date
- Prices are shown when available through SeatGeek
