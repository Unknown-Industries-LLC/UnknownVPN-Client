#!/usr/bin/env python3
"""
Xbox Games Scraper - Fixed Version Demo
========================================

This demonstrates the key improvements made to the Xbox games scraper.

Key Fixes Made:
1. Updated CSS selectors for modern Xbox website
2. Added proper waiting for content to load
3. Implemented "Load more" button clicking
4. Added fallback selectors for robust data extraction
5. Created a main function that returns the games list
6. Improved error handling and logging
7. Added bot detection evasion techniques
"""

def demonstrate_fixes():
    """Show the key improvements made to the scraper"""
    
    print("=== XBOX GAMES SCRAPER - FIXES DEMONSTRATED ===\n")
    
    print("1. UPDATED SELECTORS FOR MODERN WEBSITE:")
    print("   Old: 'a[aria-label][href*=\"/en-us/games/\"]'")
    print("   New: Multiple selectors including:")
    print("        - 'a[href*=\"/games/store/\"]'")
    print("        - '[class*=\"ProductCard\"] a'")
    print("        - 'a[data-m*=\"productCard\"]'")
    print()
    
    print("2. PROPER CONTENT LOADING:")
    print("   - Wait for game cards to load")
    print("   - Handle dynamic content loading")
    print("   - Click 'Load more' buttons automatically")
    print()
    
    print("3. ROBUST DATA EXTRACTION:")
    print("   - Multiple fallback selectors for each field")
    print("   - Safe text extraction with error handling")
    print("   - Clean title extraction (remove pricing info)")
    print()
    
    print("4. MAIN FUNCTION THAT RETURNS DATA:")
    print("   - scrape_xbox_games() function returns list of games")
    print("   - Can be imported and used in other scripts")
    print("   - Configurable limit and headless options")
    print()
    
    print("5. IMPROVED ERROR HANDLING:")
    print("   - Graceful handling of failed page loads")
    print("   - Fallback data for missing information")
    print("   - Detailed logging for debugging")
    print()

def show_example_usage():
    """Show how to use the fixed scraper"""
    
    print("=== EXAMPLE USAGE ===\n")
    
    print("Basic usage:")
    print("```python")
    print("from xbox_scraper import scrape_xbox_games")
    print()
    print("# Get 50 games")
    print("games = scrape_xbox_games(limit=50)")
    print()
    print("# Process the results")
    print("for game in games:")
    print("    print(f\"{game['title']} - {game['price']}\")")
    print("```")
    print()
    
    print("Advanced usage:")
    print("```python")
    print("# Get more games with visible browser")
    print("games = scrape_xbox_games(limit=100, headless=False)")
    print()
    print("# Filter games by price")
    print("free_games = [g for g in games if 'Free' in g['price']]")
    print("paid_games = [g for g in games if '$' in g['price']]")
    print("```")

def show_sample_output():
    """Show what the scraper output would look like"""
    
    print("=== SAMPLE OUTPUT ===\n")
    
    sample_games = [
        {
            "title": "Grand Theft Auto V",
            "link": "https://www.xbox.com/en-US/games/store/grand-theft-auto-v/BPQKM67S...",
            "description": "When a young street hustler, a retired bank robber...",
            "price": "$29.99",
            "publisher": "Rockstar Games",
            "release_date": "11/18/2014",
            "platforms": "Xbox One, Xbox Series X|S"
        },
        {
            "title": "Call of Duty: Black Ops 6",
            "link": "https://www.xbox.com/en-US/games/store/call-of-duty-black-ops-6/...",
            "description": "Call of Duty: Black Ops 6 is signature Black Ops...",
            "price": "$69.99",
            "publisher": "Activision",
            "release_date": "10/25/2024",
            "platforms": "Xbox One, Xbox Series X|S"
        },
        {
            "title": "Rocket League",
            "link": "https://www.xbox.com/en-US/games/store/rocket-league/...",
            "description": "Soccer meets driving in this physics-based multiplayer...",
            "price": "Free",
            "publisher": "Psyonix LLC",
            "release_date": "7/7/2015",
            "platforms": "Xbox One, Xbox Series X|S"
        }
    ]
    
    print("Successfully scraped 3 games!")
    print("\nFirst few games:")
    for i, game in enumerate(sample_games, 1):
        print(f"{i}. {game['title']} - {game['price']}")
    
    print(f"\nDetailed info for first game:")
    print(f"Title: {sample_games[0]['title']}")
    print(f"Price: {sample_games[0]['price']}")
    print(f"Publisher: {sample_games[0]['publisher']}")
    print(f"Release Date: {sample_games[0]['release_date']}")
    print(f"Platforms: {sample_games[0]['platforms']}")
    print(f"Description: {sample_games[0]['description'][:100]}...")

if __name__ == "__main__":
    demonstrate_fixes()
    print()
    show_example_usage()
    print()
    show_sample_output()