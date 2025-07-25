import asyncio
import csv
import logging
import time
from playwright.async_api import async_playwright
import json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MAIN_URL = "https://www.xbox.com/en-US/games/all-games/console?PlayWith=XboxSeriesX%7CS%2CXboxOne&xr=shellnav"

class XboxScraper:
    def __init__(self, headless=True, max_concurrent=5):
        self.headless = headless
        self.max_concurrent = max_concurrent
        self.games_data = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def create_browser_context(self, playwright):
        """Create browser context with optimized settings"""
        browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-extensions',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Block images, stylesheets, and fonts for faster loading
        await context.route("**/*.{png,jpg,jpeg,gif,webp,svg,css,woff,woff2,ttf}", lambda route: route.abort())
        
        return browser, context
    
    async def get_game_links(self, page, limit=None):
        """Get game links from the main page"""
        logging.info("Loading Xbox games page...")
        
        try:
            await page.goto(MAIN_URL, timeout=30000, wait_until='networkidle')
        except Exception as e:
            logging.error(f"Failed to load main page: {e}")
            return []
        
        # Wait for game cards to load
        try:
            await page.wait_for_selector('[class*="ProductCard"], a[href*="/games/store/"]', timeout=20000)
        except Exception as e:
            logging.error(f"Game cards failed to load: {e}")
            return []
        
        # Load more games by scrolling and clicking load more
        await self.load_more_games(page)
        
        # Extract game links using multiple selectors
        selectors = [
            'a[href*="/games/store/"]',
            '[class*="ProductCard"] a',
            'a[data-m*="productCard"]'
        ]
        
        all_links = set()
        
        for selector in selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    href = await element.get_attribute('href')
                    if href and '/games/store/' in href:
                        # Get title from various attributes
                        title = (await element.get_attribute('aria-label') or 
                                await element.get_attribute('title') or '')
                        
                        # Clean title (remove price info)
                        if title and ',' in title and ('$' in title or 'Free' in title):
                            title = title.split(',')[0].strip()
                        
                        if not title:
                            # Try to get title from nested elements
                            try:
                                title_elem = await element.query_selector('[class*="title"]')
                                if title_elem:
                                    title = await title_elem.text_content()
                                    title = title.strip() if title else ''
                            except:
                                continue
                        
                        if title and href:
                            all_links.add((title.strip(), href))
                            
                            if limit and len(all_links) >= limit:
                                break
                                
            except Exception as e:
                logging.warning(f"Error with selector {selector}: {e}")
                continue
        
        links = list(all_links)
        logging.info(f"Found {len(links)} game links")
        return links
    
    async def load_more_games(self, page, max_attempts=10):
        """Scroll and click load more buttons to get additional games"""
        for attempt in range(max_attempts):
            try:
                # Scroll to bottom
                await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                await page.wait_for_timeout(1500)
                
                # Look for and click load more button
                load_more_selectors = [
                    'button:has-text("Load more")',
                    'button:has-text("Show more")',
                    '[aria-label*="Load more"]'
                ]
                
                clicked = False
                for selector in load_more_selectors:
                    try:
                        button = await page.query_selector(selector)
                        if button and await button.is_visible() and await button.is_enabled():
                            await button.click()
                            await page.wait_for_timeout(2000)
                            clicked = True
                            logging.info(f"Loaded more games (attempt {attempt + 1})")
                            break
                    except:
                        continue
                
                if not clicked:
                    break
                    
            except Exception as e:
                logging.warning(f"Error loading more games: {e}")
                break
    
    async def get_game_details(self, context, title, link):
        """Extract game details from individual game page"""
        async with self.semaphore:  # Limit concurrent requests
            try:
                page = await context.new_page()
                
                try:
                    await page.goto(link, timeout=15000, wait_until='domcontentloaded')
                    
                    # Wait for main content
                    await page.wait_for_selector('h1, [class*="title"]', timeout=10000)
                    
                    # Extract data using multiple selectors with fallbacks
                    game_data = {
                        'title': await self.safe_extract_text(page, [
                            'h1',
                            '[class*="title"]',
                            'h2, h3'
                        ]) or title,
                        
                        'link': link,
                        
                        'price': await self.safe_extract_text(page, [
                            'span[class*="Price"][class*="bold"]',
                            '[class*="price"]',
                            'span[class*="boldText"]',
                            '*:has-text("$")',
                            '*:has-text("Free")'
                        ]),
                        
                        'description': await self.safe_extract_text(page, [
                            'section[aria-label="Description"] p',
                            '[class*="description"] p',
                            'p[class*="description"]',
                            '.game-description p',
                            'p:near(h1)'
                        ]),
                        
                        'publisher': await self.safe_extract_text(page, [
                            '*:has-text("Published by") + *',
                            '*:has-text("Publisher") + *',
                            '[class*="publisher"]'
                        ]),
                        
                        'release_date': await self.safe_extract_text(page, [
                            '*:has-text("Release date") + *',
                            '*:has-text("Released") + *',
                            '[class*="release"]'
                        ]),
                        
                        'platforms': await self.safe_extract_text(page, [
                            '*:has-text("Play with") + *',
                            '*:has-text("Platform") + *',
                            '[class*="platform"]'
                        ])
                    }
                    
                    return game_data
                    
                finally:
                    await page.close()
                    
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
    
    async def safe_extract_text(self, page, selectors):
        """Safely extract text using multiple selector fallbacks"""
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return ''
    
    async def scrape_games_batch(self, context, game_links_batch):
        """Scrape a batch of games concurrently"""
        tasks = []
        for title, link in game_links_batch:
            task = self.get_game_details(context, title, link)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                title, link = game_links_batch[i]
                logging.error(f"Failed to scrape {title}: {result}")
                # Add minimal data for failed games
                valid_results.append({
                    'title': title,
                    'link': link,
                    'price': '',
                    'description': '',
                    'publisher': '',
                    'release_date': '',
                    'platforms': ''
                })
            else:
                valid_results.append(result)
        
        return valid_results
    
    def create_batches(self, items, batch_size):
        """Split items into batches for processing"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    async def scrape_xbox_games(self, limit=50, batch_size=10):
        """Main scraping function"""
        async with async_playwright() as playwright:
            browser, context = await self.create_browser_context(playwright)
            
            try:
                # Get main page for game links
                page = await context.new_page()
                game_links = await self.get_game_links(page, limit)
                await page.close()
                
                if not game_links:
                    logging.error("No game links found!")
                    return []
                
                logging.info(f"Starting to scrape {len(game_links)} games in batches of {batch_size}")
                
                all_games = []
                
                # Process games in batches for better performance
                batches = list(self.create_batches(game_links, batch_size))
                
                for i, batch in enumerate(batches, 1):
                    logging.info(f"Processing batch {i}/{len(batches)} ({len(batch)} games)")
                    
                    batch_results = await self.scrape_games_batch(context, batch)
                    all_games.extend(batch_results)
                    
                    # Small delay between batches to be respectful
                    if i < len(batches):
                        await asyncio.sleep(1)
                
                logging.info(f"Successfully scraped {len(all_games)} games")
                return all_games
                
            finally:
                await browser.close()

def save_to_csv(data, filename="xbox_games_playwright.csv"):
    """Save games data to CSV file"""
    if not data:
        logging.warning("No data to save")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        if data:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
    
    logging.info(f"Saved {len(data)} games to {filename}")

async def scrape_xbox_games_async(limit=50, headless=True, batch_size=10, max_concurrent=5):
    """Async function to scrape Xbox games - can be called from other async code"""
    scraper = XboxScraper(headless=headless, max_concurrent=max_concurrent)
    games = await scraper.scrape_xbox_games(limit=limit, batch_size=batch_size)
    
    # Save to CSV
    save_to_csv(games)
    
    return games

def scrape_xbox_games(limit=50, headless=True, batch_size=10, max_concurrent=5):
    """Synchronous wrapper function - returns list of games"""
    return asyncio.run(scrape_xbox_games_async(limit, headless, batch_size, max_concurrent))

async def main():
    """Main function for direct execution"""
    start_time = time.time()
    
    # Configuration
    LIMIT = 50
    BATCH_SIZE = 10  # Process 10 games concurrently
    MAX_CONCURRENT = 5  # Max concurrent page requests
    
    logging.info(f"Starting Xbox games scraper with Playwright")
    logging.info(f"Limit: {LIMIT}, Batch size: {BATCH_SIZE}, Max concurrent: {MAX_CONCURRENT}")
    
    try:
        games = await scrape_xbox_games_async(
            limit=LIMIT,
            headless=True,
            batch_size=BATCH_SIZE,
            max_concurrent=MAX_CONCURRENT
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if games:
            print(f"\n🎮 Successfully scraped {len(games)} Xbox games in {duration:.2f} seconds!")
            print(f"📊 Average: {duration/len(games):.2f} seconds per game")
            
            print(f"\n📋 First 5 games:")
            for i, game in enumerate(games[:5], 1):
                print(f"{i}. {game['title']} - {game['price']}")
            
            # Show some statistics
            free_games = [g for g in games if 'Free' in g.get('price', '')]
            paid_games = [g for g in games if '$' in g.get('price', '')]
            
            print(f"\n📈 Statistics:")
            print(f"Free games: {len(free_games)}")
            print(f"Paid games: {len(paid_games)}")
            print(f"Games with descriptions: {len([g for g in games if g.get('description')])}")
            
        else:
            print("❌ No games were scraped")
            
    except Exception as e:
        logging.error(f"Scraping failed: {e}")
        print(f"❌ Scraping failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())