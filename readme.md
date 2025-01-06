# Concert Finder 🎵

Find concerts by your favorite Spotify artists in cities you'll be visiting! This tool automatically:
- Gets your favorite artists from Spotify
- Checks your Google Calendar for travel dates
- Searches multiple concert APIs for shows

## 🌟 Features

- **Interactive Setup**: Guided setup process for all required APIs
- **Multiple Data Sources**: Choose from SeatGeek, Bandsintown, and Songkick
- **Smart Integration**: 
  - Automatically finds your Spotify favorites
  - Uses your actual travel dates from Google Calendar
  - Combines results from multiple concert sources
- **Smart Results**:
  - Automatic duplicate removal
  - Location-based grouping
  - Price comparisons (when available)
  - Direct ticket links

## 🚀 Quick Start

1. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Program**
   ```bash
   python concert_finder.py
   ```
   The program will guide you through:
   - Setting up Google Calendar access
   - Connecting your Spotify account
   - Choosing and configuring concert APIs

## 🔍 How It Works

1. **First Run Setup**
   - The program will guide you through setting up each service
   - Follow the prompts to configure each API you want to use
   - You can skip any concert APIs you don't want to use

2. **Running Searches**
   - Select which concert APIs to use for each search
   - The program shows which APIs are available based on your config
   - Results combine data from all selected sources

3. **View Results**
   - Concerts are grouped by location
   - Results show venue, date, and ticket information
   - Prices are shown when available

## ❗ Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Authentication errors | Run `python cleanup.py` to reset credentials |
| Invalid client error | Double-check your API credentials |
| Calendar errors | Follow the setup prompts to reconfigure |
| Missing results | Ensure calendar events have locations |

### Reset Everything
```bash
python cleanup.py --force
```

## 🔒 Privacy

- All data and credentials remain on your local machine
- No data is shared with external services beyond API calls
- API keys and tokens are stored only in your local config

## 🤝 Contributing

Found a bug or have an idea for improvement? Please:
1. Check existing issues
2. Test with the latest version
3. Open an issue with details
4. Feel free to submit pull requests

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.# Concert Finder 🎵

Find concerts by your favorite Spotify artists in cities you'll be visiting! This tool integrates with:
- Your Spotify library to know your favorite artists
- Your Google Calendar to know your travel dates
- Multiple concert APIs to find shows near you

## 🌟 Features

- **Multiple Data Sources**: Search across SeatGeek, Bandsintown, and Songkick simultaneously
- **Smart Integration**: Uses your actual Spotify favorites and travel dates
- **Interactive Selection**: Choose which concert APIs to use each time
- **Smart Results**:
  - Automatic duplicate removal
  - Location-based grouping
  - Price comparisons (when available)
  - Direct ticket links

## 🚀 Quick Start

1. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up Configuration**
   ```bash
   python setup_config.py
   ```

3. **Configure APIs** (see detailed instructions below)

4. **Verify Setup**
   ```bash
   python setup_test.py
   ```

5. **Run the Program**
   ```bash
   python concert_finder.py
   ```

## 🔧 API Setup

### Required APIs

#### 1. Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project & enable Google Calendar API
3. Set up OAuth consent screen
4. Create credentials (OAuth client ID)
5. Download and save as `credentials.json`

#### 2. Spotify API
1. Visit [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Set redirect URI to: `http://localhost:8888/callback`
4. Note your Client ID and Secret

### Optional APIs (Choose at least one)

#### SeatGeek API
- Register at [SeatGeek Developer](https://seatgeek.com/account/develop)
- Get your Client ID and Secret

#### Bandsintown API
- Apply at [Bandsintown for Partners](https://www.bandsintown.com/partners)
- Store your App ID when approved

#### Songkick API
- Request access at [Songkick API](https://www.songkick.com/developer)
- Save your API key when received

## 📝 Configuration

Run the setup wizard:
```bash
python setup_config.py
```

You'll need to provide:
- Your home location (e.g., "New York, USA")
- Credentials for your chosen APIs

## 🔍 Usage

1. **Prepare Your Calendar**
   - Add events with locations for your travels
   - Events without locations will be ignored

2. **Run the Program**
   ```bash
   python concert_finder.py
   ```

3. **Select APIs**
   - Choose which concert sources to use
   - The program shows which APIs are available based on your config

4. **View Results**
   - Concerts are grouped by location
   - Results show venue, date, and ticket information
   - Prices are shown when available

## ❗ Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| Authentication errors | Run `python cleanup.py` to reset credentials |
| Invalid client error | Double-check your API credentials |
| Calendar errors | Verify `credentials.json` is present |
| Missing results | Ensure calendar events have locations |

### Reset Everything
```bash
python cleanup.py --force
```

## 🔒 Privacy

- All data and credentials remain on your local machine
- No data is shared with external services beyond API calls
- API keys and tokens are stored only in your local config

## 🤝 Contributing

Found a bug or have an idea for improvement? Please:
1. Check existing issues
2. Test with the latest version
3. Open an issue with details
4. Feel free to submit pull requests

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.