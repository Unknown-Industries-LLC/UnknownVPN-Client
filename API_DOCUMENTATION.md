# Xbox Games Scraper API 🎮⚡

A high-performance Flask API that uses Playwright to scrape Xbox games data and return it as JSON. **5-10x faster than Selenium** with concurrent processing and intelligent caching.

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install flask playwright

# Install browser engines
playwright install chromium
```

### Start the API
```bash
python xbox_api.py
```

The API will be available at `http://localhost:5000`

## 📡 API Endpoints

### 1. Main Games Endpoint
**`GET /api/xbox/games`**

Scrape Xbox games with full details including price, description, publisher, etc.

#### Parameters
| Parameter   | Type    | Default | Max | Description |
|-------------|---------|---------|-----|-------------|
| `limit`     | integer | 50      | 200 | Number of games to scrape |
| `concurrent`| integer | 8       | 15  | Number of concurrent workers |
| `format`    | string  | "json"  | -   | Response format: "json" or "simple" |

#### Example Requests
```bash
# Basic request (50 games, full details)
curl "http://localhost:5000/api/xbox/games"

# Fast request (20 games, simple format)
curl "http://localhost:5000/api/xbox/games?limit=20&format=simple&concurrent=10"

# Detailed request (100 games, slower but more data)
curl "http://localhost:5000/api/xbox/games?limit=100&concurrent=5"
```

#### Response Format (Full JSON)
```json
{
  "success": true,
  "count": 50,
  "scraping_time": 25.4,
  "average_time_per_game": 0.51,
  "timestamp": "2024-01-15T10:30:00",
  "cached": false,
  "games": [
    {
      "title": "Grand Theft Auto V",
      "link": "https://www.xbox.com/en-US/games/store/...",
      "price": "$29.99",
      "description": "When a young street hustler...",
      "publisher": "Rockstar Games",
      "release_date": "11/18/2014",
      "platforms": "Xbox One, Xbox Series X|S"
    }
  ]
}
```

#### Response Format (Simple)
```json
{
  "games": [
    {
      "title": "Grand Theft Auto V",
      "price": "$29.99",
      "link": "https://www.xbox.com/en-US/games/store/..."
    }
  ],
  "count": 20,
  "scraping_time": 12.3
}
```

### 2. Fast Titles Endpoint
**`GET /api/xbox/games/titles`**

Super fast endpoint that returns only game titles and links (no detailed scraping).

#### Parameters
| Parameter | Type    | Default | Max | Description |
|-----------|---------|---------|-----|-------------|
| `limit`   | integer | 30      | 100 | Number of game titles |

#### Example Request
```bash
curl "http://localhost:5000/api/xbox/games/titles?limit=50"
```

#### Response Format
```json
{
  "success": true,
  "count": 50,
  "timestamp": "2024-01-15T10:30:00",
  "games": [
    {
      "title": "Grand Theft Auto V",
      "link": "https://www.xbox.com/en-US/games/store/..."
    }
  ]
}
```

### 3. Health Check
**`GET /api/health`**

Check if the API is running and get status information.

#### Example Request
```bash
curl "http://localhost:5000/api/health"
```

#### Response Format
```json
{
  "status": "healthy",
  "service": "Xbox Games Scraper API",
  "timestamp": "2024-01-15T10:30:00",
  "cache_size": 3
}
```

### 4. Cache Management
**`POST /api/cache/clear`**

Clear the internal cache to force fresh data on next requests.

#### Example Request
```bash
curl -X POST "http://localhost:5000/api/cache/clear"
```

### 5. API Documentation
**`GET /`**

Get interactive API documentation in JSON format.

## ⚡ Performance Features

### Concurrent Processing
- Process multiple games simultaneously
- Configurable worker limits (1-15 concurrent)
- Automatic semaphore-based rate limiting

### Resource Optimization
- Blocks images, CSS, fonts for 3x faster loading
- Optimized browser settings
- Shared browser context

### Smart Caching
- 5-minute cache for identical requests
- Reduces server load and improves response times
- Cache status included in responses

### Fast Extraction
- JavaScript-based DOM extraction
- Multiple fallback selectors
- Minimal page wait times

## 🎯 Usage Examples

### Python Client
```python
import requests

# Get 30 games quickly
response = requests.get(
    "http://localhost:5000/api/xbox/games",
    params={"limit": 30, "format": "simple", "concurrent": 8}
)

games = response.json()
for game in games["games"]:
    print(f"{game['title']} - {game['price']}")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

async function getXboxGames() {
    try {
        const response = await axios.get('http://localhost:5000/api/xbox/games', {
            params: {
                limit: 25,
                format: 'simple',
                concurrent: 6
            }
        });
        
        console.log(`Found ${response.data.count} games`);
        response.data.games.forEach(game => {
            console.log(`${game.title} - ${game.price}`);
        });
    } catch (error) {
        console.error('Error:', error.message);
    }
}

getXboxGames();
```

### cURL Examples
```bash
# Quick test (titles only)
curl "http://localhost:5000/api/xbox/games/titles?limit=20"

# Production scraping (balanced)
curl "http://localhost:5000/api/xbox/games?limit=50&concurrent=8&format=json"

# Fast scraping (simple data)
curl "http://localhost:5000/api/xbox/games?limit=100&concurrent=12&format=simple"

# Clear cache
curl -X POST "http://localhost:5000/api/cache/clear"
```

## 🔧 Configuration Guide

### Performance Tuning

**Conservative (slow connection)**:
```
limit=25, concurrent=3
```

**Balanced (recommended)**:
```
limit=50, concurrent=8
```

**Aggressive (fast connection)**:
```
limit=100, concurrent=12
```

### Response Time Expectations

| Games | Concurrent | Expected Time | Use Case |
|-------|------------|---------------|----------|
| 10    | 5          | 8-12s        | Quick test |
| 50    | 8          | 20-35s       | Regular use |
| 100   | 10         | 35-60s       | Bulk data |
| 200   | 15         | 60-120s      | Full catalog |

## 🛠️ Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad request (invalid parameters)
- `408` - Request timeout (>120s)
- `500` - Internal server error

### Error Response Format
```json
{
  "error": "Invalid parameter: limit must be <= 200",
  "success": false
}
```

### Common Issues

**Timeout Errors**:
- Reduce `limit` or `concurrent` parameters
- Check internet connection
- Try again later

**Invalid Parameters**:
- `limit` must be 1-200
- `concurrent` must be 1-15
- `format` must be "json" or "simple"

**No Games Found**:
- Xbox website might be down
- Check health endpoint
- Clear cache and retry

## 📊 Monitoring & Logging

### Built-in Metrics
Every response includes performance metrics:
```json
{
  "scraping_time": 25.4,
  "average_time_per_game": 0.51,
  "count": 50,
  "cached": false
}
```

### Server Logs
The API provides detailed logging:
```
INFO Loading Xbox games page...
INFO Found 150 game links
INFO Starting to scrape 50 games with 8 concurrent workers
INFO Completed 10/50 games
INFO Completed 20/50 games
INFO Scraped 50 games in 25.40 seconds
```

## 🚦 Rate Limiting & Ethics

### Built-in Protections
- Maximum 15 concurrent workers
- Automatic delays between requests
- Resource blocking reduces server load
- Timeout limits prevent hanging requests

### Best Practices
- Use appropriate `concurrent` values for your connection
- Don't exceed 200 games per request
- Use caching when possible
- Be respectful to Xbox's servers

## 🔄 Deployment

### Production Deployment
```bash
# Using Gunicorn (recommended)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 xbox_api:app

# Using uWSGI
pip install uwsgi
uwsgi --http 0.0.0.0:5000 --module xbox_api:app
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install flask playwright
RUN playwright install chromium

EXPOSE 5000
CMD ["python", "xbox_api.py"]
```

### Environment Variables
```bash
export FLASK_ENV=production
export FLASK_DEBUG=false
export PORT=5000
```

## 🧪 Testing

Run the test client to verify everything works:
```bash
python test_api_client.py
```

This will test all endpoints and provide performance metrics.

## 🎉 Migration from Direct Scraping

If you're currently using the direct scraper:

**Before (direct scraping)**:
```python
from xbox_scraper_playwright import scrape_xbox_games
games = scrape_xbox_games(limit=50)
```

**After (API)**:
```python
import requests
response = requests.get("http://localhost:5000/api/xbox/games?limit=50")
games = response.json()["games"]
```

## 📈 Performance Comparison

| Method | 50 Games | 100 Games | Concurrent | Caching |
|--------|----------|-----------|------------|---------|
| Selenium | 225s | 450s | No | No |
| Playwright Direct | 35s | 65s | Yes | No |
| **API (This)** | **25s** | **45s** | **Yes** | **Yes** |

## ⚖️ Legal & Ethics

- Use responsibly and respect Xbox's terms of service
- Don't overload their servers
- Intended for research and personal use
- Consider rate limiting for large requests

---

**Ready to get Xbox games data at lightning speed? Start the API and enjoy! 🎮⚡**