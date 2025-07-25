import time
import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

MAIN_URL = "https://www.xbox.com/en-US/games/all-games/console?PlayWith=XboxSeriesX%7CS%2CXboxOne&xr=shellnav"

def init_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option('useAutomationExtension', False)
    # disable images for speed
    opts.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def wait_for_games_to_load(driver, timeout=30):
    """Wait for game cards to load on the page"""
    wait = WebDriverWait(driver, timeout)
    try:
        # Wait for game cards to appear - updated selectors for Xbox site
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[class*="ProductCard"]')
        ))
        return True
    except:
        try:
            # Alternative selector
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'a[href*="/games/store/"]')
            ))
            return True
        except:
            logging.error("Games failed to load")
            return False

def click_load_more_button(driver):
    """Click the 'Load more' button if it exists"""
    try:
        load_more_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load more')]")
        if load_more_button.is_displayed() and load_more_button.is_enabled():
            driver.execute_script("arguments[0].click();", load_more_button)
            time.sleep(2)
            return True
    except:
        pass
    return False

def scroll_and_load_more(driver, max_attempts=10):
    """Scroll to bottom and click load more buttons to get more games"""
    for attempt in range(max_attempts):
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # Try to click load more button
        if not click_load_more_button(driver):
            # If no load more button, we've likely reached the end
            break
        
        logging.info(f"Loaded more games (attempt {attempt + 1})")
        time.sleep(3)  # Wait for new content to load

def get_game_links(driver, limit=None):
    driver.get(MAIN_URL)
    
    if not wait_for_games_to_load(driver):
        return []
    
    # Scroll and load more games
    scroll_and_load_more(driver)
    
    # Find all game links with multiple possible selectors
    selectors = [
        'a[href*="/games/store/"]',
        'a[aria-label][href*="/en-us/games/"]',
        '[class*="ProductCard"] a',
        'a[data-m*="productCard"]'
    ]
    
    all_elements = []
    for selector in selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        all_elements.extend(elements)
    
    seen = set()
    links = []
    
    for element in all_elements:
        try:
            href = element.get_attribute("href")
            if not href or "/games/store/" not in href:
                continue
                
            # Get title from aria-label or title attribute
            title = (element.get_attribute("aria-label") or 
                    element.get_attribute("title") or "")
            
            # Clean up title (remove price info, etc.)
            if title:
                # Remove price information from aria-label
                if "," in title and ("$" in title or "Free" in title):
                    title = title.split(",")[0].strip()
            
            if not title:
                # Try to get title from nested elements
                try:
                    title_elem = element.find_element(By.CSS_SELECTOR, '[class*="title"]')
                    title = title_elem.text.strip()
                except:
                    continue
            
            if href in seen or not title:
                continue
                
            seen.add(href)
            links.append((title.strip(), href))
            
            if limit and len(links) >= limit:
                break
                
        except Exception as e:
            continue
    
    logging.info(f"Discovered {len(links)} game links")
    return links

def get_game_details(driver, title, link):
    """Extract game details from individual game page"""
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 15)
        
        # Wait for page to load
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1")))
        except:
            logging.warning(f"Page failed to load for {title}")
        
        def safe_text(by, selector):
            try:
                element = driver.find_element(by, selector)
                return element.text.strip()
            except:
                return ""
        
        def safe_text_multiple(selectors):
            for by, selector in selectors:
                try:
                    element = driver.find_element(by, selector)
                    text = element.text.strip()
                    if text:
                        return text
                except:
                    continue
            return ""
        
        # Get game title
        game_title = safe_text_multiple([
            (By.TAG_NAME, "h1"),
            (By.CSS_SELECTOR, "[class*='title']"),
            (By.CSS_SELECTOR, "h1, h2, h3")
        ]) or title
        
        # Get price with multiple selectors
        price = safe_text_multiple([
            (By.CSS_SELECTOR, "span[class*='Price'][class*='bold']"),
            (By.CSS_SELECTOR, "[class*='price']"),
            (By.CSS_SELECTOR, "span[class*='boldText']"),
            (By.XPATH, "//*[contains(text(), '$') or contains(text(), 'Free')]")
        ])
        
        # Get description
        description = safe_text_multiple([
            (By.CSS_SELECTOR, "section[aria-label='Description'] p"),
            (By.CSS_SELECTOR, "[class*='description'] p"),
            (By.CSS_SELECTOR, "p[class*='description']"),
            (By.CSS_SELECTOR, ".game-description p")
        ])
        
        # Get publisher
        publisher = safe_text_multiple([
            (By.XPATH, "//div[contains(text(),'Published by')]/following-sibling::div"),
            (By.XPATH, "//*[contains(text(),'Publisher')]/following-sibling::*"),
            (By.CSS_SELECTOR, "[class*='publisher']")
        ])
        
        # Get release date
        release_date = safe_text_multiple([
            (By.XPATH, "//div[contains(text(),'Release date')]/following-sibling::div"),
            (By.XPATH, "//*[contains(text(),'Release')]/following-sibling::*"),
            (By.CSS_SELECTOR, "[class*='release']")
        ])
        
        # Get platforms
        platforms = safe_text_multiple([
            (By.XPATH, "//div[contains(text(),'Play with')]/following-sibling::div"),
            (By.XPATH, "//*[contains(text(),'Platform')]/following-sibling::*"),
            (By.CSS_SELECTOR, "[class*='platform']")
        ])
        
        return {
            "title": game_title,
            "link": link,
            "description": description,
            "price": price,
            "publisher": publisher,
            "release_date": release_date,
            "platforms": platforms,
        }
        
    except Exception as e:
        logging.error(f"Error getting details for {title}: {e}")
        return {
            "title": title,
            "link": link,
            "description": "",
            "price": "",
            "publisher": "",
            "release_date": "",
            "platforms": "",
        }

def save_to_csv(data, filename="xbox_games.csv"):
    if not data:
        logging.warning("No data to write.")
        return
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Saved {len(data)} records to {filename}")

def scrape_xbox_games(limit=50, headless=True):
    """Main function that returns the list of games"""
    driver = init_driver(headless=headless)
    try:
        # Step 1: Get game links
        game_links = get_game_links(driver, limit=limit)
        
        if not game_links:
            logging.error("No games found!")
            return []
        
        # Step 2: Get details for each game
        games_data = []
        for idx, (title, link) in enumerate(game_links, 1):
            logging.info(f"[{idx}/{len(game_links)}] Processing: {title}")
            game_details = get_game_details(driver, title, link)
            games_data.append(game_details)
            
            # Small delay to be respectful
            time.sleep(1)
        
        # Step 3: Save to CSV
        save_to_csv(games_data)
        
        return games_data
        
    except Exception as e:
        logging.error(f"Error during scraping: {e}")
        return []
    finally:
        driver.quit()

if __name__ == "__main__":
    # Run the scraper and get the list of games
    games = scrape_xbox_games(limit=50, headless=True)
    
    if games:
        print(f"\nSuccessfully scraped {len(games)} games!")
        print("\nFirst few games:")
        for i, game in enumerate(games[:5]):
            print(f"{i+1}. {game['title']} - {game['price']}")
    else:
        print("No games were scraped.")