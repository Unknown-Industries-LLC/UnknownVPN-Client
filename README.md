# Xbox Games Scraper - Fixed Version

This is a fixed and improved version of the Xbox games scraper that properly returns a list of games from the Xbox store.

## Key Fixes Made

### 1. Updated CSS Selectors
The original scraper used outdated selectors that didn't work with the modern Xbox website. The fixed version uses multiple fallback selectors:
- `a[href*="/games/store/"]` - Main game store links
- `[class*="ProductCard"] a` - Product card links
- `a[data-m*="productCard"]` - Data attribute-based links

### 2. Proper Content Loading
- **Wait for games to load**: Added explicit waits for game cards to appear
- **Handle dynamic content**: Implemented scrolling and "Load more" button clicking
- **Pagination handling**: Automatically loads additional games

### 3. Robust Data Extraction
- **Multiple fallback selectors**: Each data field has multiple selector options
- **Error handling**: Safe text extraction that doesn't crash on missing elements
- **Data cleaning**: Removes price information from game titles

### 4. Main Function Returns Data
The fixed scraper includes a `scrape_xbox_games()` function that:
- Returns a list of dictionaries containing game data
- Can be imported and used in other scripts
- Configurable options for limit and headless mode

### 5. Bot Detection Evasion
Added options to avoid detection:
- `--disable-blink-features=AutomationControlled`
- `--disable-automation`
- User agent rotation capabilities

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Chrome browser (if not already installed)

## Usage

### Basic Usage
```python
from xbox_scraper import scrape_xbox_games

# Get 50 games
games = scrape_xbox_games(limit=50)

# Print results
for game in games:
    print(f"{game['title']} - {game['price']}")
```

### Advanced Usage
```python
# Get more games with visible browser
games = scrape_xbox_games(limit=100, headless=False)

# Filter games by price
free_games = [g for g in games if 'Free' in g['price']]
paid_games = [g for g in games if '$' in g['price']]

# Save to custom CSV file
save_to_csv(games, "my_xbox_games.csv")
```

### Running the Script
```bash
python3 xbox_scraper.py
```

## Data Structure

Each game in the returned list contains:
```python
{
    "title": "Game Title",
    "link": "https://www.xbox.com/en-US/games/store/...",
    "description": "Game description...",
    "price": "$29.99" or "Free",
    "publisher": "Publisher Name",
    "release_date": "MM/DD/YYYY",
    "platforms": "Xbox One, Xbox Series X|S"
}
```

## Output

The scraper will:
1. Create an `xbox_games.csv` file with all scraped data
2. Return a list of dictionaries for programmatic use
3. Log progress and any errors encountered

## Error Handling

The fixed version includes comprehensive error handling:
- Graceful handling of failed page loads
- Fallback data for missing information
- Detailed logging for debugging
- Continues scraping even if individual games fail

## Performance

- Disables image loading for faster scraping
- Configurable delays to be respectful to the server
- Efficient scrolling and pagination handling
- Memory-conscious operation

## Troubleshooting

If you encounter issues:

1. **Chrome driver issues**: The script auto-downloads the correct ChromeDriver
2. **Timeout errors**: Increase wait times in the `WebDriverWait` calls
3. **No games found**: Check if Xbox changed their website structure
4. **Rate limiting**: Add longer delays between requests

## Legal Notice

This scraper is for educational purposes only. Please respect Xbox's robots.txt and terms of service. Use responsibly and don't overload their servers.
