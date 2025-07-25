from flask import Flask, jsonify, request
import asyncio
import logging
import time
from datetime import datetime
from playwright.async_api import async_playwright
import json
from threading import Thread
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)

# Global configuration
MAIN_URL = "https://www.xbox.com/en-US/games/all-games/console?PlayWith=XboxSeriesX%7CS%2CXboxOne&xr=shellnav"

class XboxScraperAPI:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes cache
    
    async def create_browser_context(self, playwright):
        """Create optimized browser context"""
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-web-security',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Block resources for faster loading
        await context.route("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf,ico}", 
                           lambda route: route.abort())
        
        return browser, context
    
    async def get_game_links_fast(self, page, limit=None):
        """Fast extraction of game links"""
        logging.info("Loading Xbox games page...")
        
        try:
            # Load page with faster settings
            await page.goto(MAIN_URL, timeout=20000, wait_until='domcontentloaded')
        except Exception as e:
            logging.error(f"Failed to load main page: {e}")
            return []
        
        # Wait for game cards with shorter timeout
        try:
            await page.wait_for_selector('[class*="ProductCard"], a[href*="/games/store/"]', timeout=10000)
        except Exception as e:
            logging.error(f"Game cards failed to load: {e}")
            return []
        
        # Quick scroll to load more content (faster than clicking load more)
        for _ in range(3):  # Limited scrolls for speed
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(800)  # Shorter wait
        
        # Fast extraction using JavaScript
        game_links_js = """
        () => {
            const links = new Set();
            const selectors = [
                'a[href*="/games/store/"]',
                '[class*="ProductCard"] a',
                'a[data-m*="productCard"]'
            ];
            
            selectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(element => {
                    const href = element.href;
                    if (href && href.includes('/games/store/')) {
                        let title = element.getAttribute('aria-label') || 
                                   element.getAttribute('title') || '';
                        
                        // Clean title
                        if (title && title.includes(',') && (title.includes('$') || title.includes('Free'))) {
                            title = title.split(',')[0].trim();
                        }
                        
                        if (!title) {
                            const titleElem = element.querySelector('[class*="title"]');
                            if (titleElem) title = titleElem.textContent.trim();
                        }
                        
                        if (title && href) {
                            links.add(JSON.stringify({title: title.trim(), href: href}));
                        }
                    }
                });
            });
            
            return Array.from(links).map(link => JSON.parse(link));
        }
        """
        
        try:
            game_links_data = await page.evaluate(game_links_js)
            links = [(item['title'], item['href']) for item in game_links_data]
            
            if limit:
                links = links[:limit]
            
            logging.info(f"Found {len(links)} game links")
            return links
        except Exception as e:
            logging.error(f"Error extracting game links: {e}")
            return []
    
    async def get_game_details_fast(self, page, title, link):
        """Fast game details extraction"""
        try:
            await page.goto(link, timeout=10000, wait_until='domcontentloaded')
            
            # Fast extraction using JavaScript
            details_js = """
            () => {
                const getData = (selectors) => {
                    for (const selector of selectors) {
                        try {
                            const element = document.querySelector(selector);
                            if (element && element.textContent.trim()) {
                                return element.textContent.trim();
                            }
                        } catch(e) {}
                    }
                    return '';
                };
                
                return {
                    title: getData(['h1', '[class*="title"]', 'h2, h3']) || arguments[0],
                    price: getData([
                        'span[class*="Price"][class*="bold"]',
                        '[class*="price"]',
                        'span[class*="boldText"]'
                    ]),
                    description: getData([
                        'section[aria-label="Description"] p',
                        '[class*="description"] p',
                        'p[class*="description"]'
                    ]),
                    publisher: getData([
                        '*:has-text("Published by") + *',
                        '*:has-text("Publisher") + *'
                    ]),
                    release_date: getData([
                        '*:has-text("Release date") + *',
                        '*:has-text("Released") + *'
                    ]),
                    platforms: getData([
                        '*:has-text("Play with") + *',
                        '*:has-text("Platform") + *'
                    ])
                };
            }
            """
            
            game_data = await page.evaluate(details_js, title)
            game_data['link'] = link
            
            return game_data
            
        except Exception as e:
            logging.error(f"Error getting details for {title}: {e}")
            return {
                'title': title,
                'link': link,
                'price': '',
                'description': '',
                'publisher': '',
                'release_date': '',
                'platforms': ''
            }
    
    async def scrape_games_concurrent(self, game_links, max_concurrent=8):
        """Scrape games with controlled concurrency"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_single_game(browser_context, title, link):
            async with semaphore:
                page = await browser_context.new_page()
                try:
                    return await self.get_game_details_fast(page, title, link)
                finally:
                    await page.close()
        
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            
            try:
                # Create tasks for all games
                tasks = [
                    scrape_single_game(context, title, link)
                    for title, link in game_links
                ]
                
                # Execute with progress logging
                results = []
                completed = 0
                
                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    results.append(result)
                    completed += 1
                    
                    if completed % 10 == 0:
                        logging.info(f"Completed {completed}/{len(tasks)} games")
                
                return results
                
            finally:
                await browser.close()
    
    async def scrape_xbox_games_api(self, limit=50, max_concurrent=8):
        """Main API scraping function"""
        start_time = time.time()
        
        # Check cache
        cache_key = f"games_{limit}_{max_concurrent}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if time.time() - cached_time < self.cache_timeout:
                logging.info("Returning cached data")
                return cached_data
        
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            
            try:
                # Get game links
                page = await context.new_page()
                game_links = await self.get_game_links_fast(page, limit)
                await page.close()
                
                if not game_links:
                    return {"error": "No games found", "games": [], "count": 0}
                
                logging.info(f"Starting to scrape {len(game_links)} games with {max_concurrent} concurrent workers")
                
            finally:
                await browser.close()
        
        # Scrape game details concurrently
        games_data = await self.scrape_games_concurrent(game_links, max_concurrent)
        
        end_time = time.time()
        duration = end_time - start_time
        
        result = {
            "success": True,
            "count": len(games_data),
            "games": games_data,
            "scraping_time": round(duration, 2),
            "average_time_per_game": round(duration / len(games_data), 2) if games_data else 0,
            "timestamp": datetime.now().isoformat(),
            "cached": False
        }
        
        # Cache the result
        self.cache[cache_key] = (result, time.time())
        
        logging.info(f"Scraped {len(games_data)} games in {duration:.2f} seconds")
        return result

# Initialize scraper
scraper = XboxScraperAPI()

@app.route('/api/xbox/games', methods=['GET'])
def get_xbox_games():
    """
    GET /api/xbox/games
    
    Query parameters:
    - limit: Number of games to scrape (default: 50, max: 200)
    - concurrent: Number of concurrent workers (default: 8, max: 15)
    - format: Response format ('json' or 'simple', default: 'json')
    """
    try:
        # Get parameters
        limit = min(int(request.args.get('limit', 50)), 200)
        concurrent = min(int(request.args.get('concurrent', 8)), 15)
        format_type = request.args.get('format', 'json').lower()
        
        # Run async scraping in thread
        def run_scraping():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    scraper.scrape_xbox_games_api(limit, concurrent)
                )
            finally:
                loop.close()
        
        # Execute with timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_scraping)
            try:
                result = future.result(timeout=120)  # 2 minute timeout
            except concurrent.futures.TimeoutError:
                return jsonify({
                    "error": "Scraping timeout (120s exceeded)",
                    "success": False
                }), 408
        
        # Format response
        if format_type == 'simple':
            # Simplified response for easier consumption
            simple_games = []
            for game in result.get('games', []):
                simple_games.append({
                    'title': game.get('title', ''),
                    'price': game.get('price', ''),
                    'link': game.get('link', '')
                })
            
            return jsonify({
                "games": simple_games,
                "count": len(simple_games),
                "scraping_time": result.get('scraping_time', 0)
            })
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({
            "error": f"Invalid parameter: {str(e)}",
            "success": False
        }), 400
    
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.route('/api/xbox/games/titles', methods=['GET'])
def get_game_titles_only():
    """
    GET /api/xbox/games/titles
    
    Fast endpoint that returns only game titles and prices
    """
    try:
        limit = min(int(request.args.get('limit', 30)), 100)
        
        async def get_titles_only():
            async with async_playwright() as playwright:
                browser, context = await scraper.create_browser_context(playwright)
                
                try:
                    page = await context.new_page()
                    game_links = await scraper.get_game_links_fast(page, limit)
                    
                    # Just return titles and links, no detailed scraping
                    titles_data = []
                    for title, link in game_links:
                        titles_data.append({
                            "title": title,
                            "link": link
                        })
                    
                    return titles_data
                    
                finally:
                    await browser.close()
        
        def run_titles_scraping():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(get_titles_only())
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_titles_scraping)
            titles = future.result(timeout=30)
        
        return jsonify({
            "success": True,
            "count": len(titles),
            "games": titles,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logging.error(f"Titles API error: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Xbox Games Scraper API",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(scraper.cache)
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear the cache"""
    scraper.cache.clear()
    return jsonify({
        "success": True,
        "message": "Cache cleared",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    docs = {
        "Xbox Games Scraper API": {
            "version": "1.0",
            "description": "Fast Playwright-based Xbox games scraper",
            "endpoints": {
                "GET /api/xbox/games": {
                    "description": "Scrape Xbox games with full details",
                    "parameters": {
                        "limit": "Number of games (default: 50, max: 200)",
                        "concurrent": "Concurrent workers (default: 8, max: 15)",
                        "format": "'json' for full data, 'simple' for basic data"
                    },
                    "example": "/api/xbox/games?limit=20&concurrent=5&format=simple"
                },
                "GET /api/xbox/games/titles": {
                    "description": "Fast endpoint for titles only",
                    "parameters": {
                        "limit": "Number of games (default: 30, max: 100)"
                    },
                    "example": "/api/xbox/games/titles?limit=50"
                },
                "GET /api/health": {
                    "description": "Health check endpoint"
                },
                "POST /api/cache/clear": {
                    "description": "Clear the cache"
                }
            },
            "performance": {
                "typical_response_time": "10-30 seconds for 50 games",
                "concurrent_processing": "Up to 15 parallel workers",
                "caching": "5 minute cache for identical requests"
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    print("🚀 Starting Xbox Games Scraper API with Playwright")
    print("📡 Available endpoints:")
    print("   GET  /api/xbox/games - Full game details")
    print("   GET  /api/xbox/games/titles - Titles only (fast)")
    print("   GET  /api/health - Health check")
    print("   POST /api/cache/clear - Clear cache")
    print("\n💡 Example usage:")
    print("   curl 'http://localhost:5000/api/xbox/games?limit=20&format=simple'")
    print("   curl 'http://localhost:5000/api/xbox/games/titles?limit=50'")
    
    app.run(debug=True, host='0.0.0.0', port=5000)