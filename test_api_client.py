#!/usr/bin/env python3
"""
Xbox Games API Test Client
=========================

Simple client to test the Flask API endpoints
"""

import requests
import json
import time

API_BASE = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy: {data['service']}")
            print(f"   Cache size: {data['cache_size']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_titles_endpoint():
    """Test the fast titles-only endpoint"""
    print("\n📋 Testing titles endpoint (fast)...")
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE}/api/xbox/games/titles?limit=10")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {data['count']} game titles in {end_time - start_time:.2f} seconds")
            
            print("\n📝 Sample titles:")
            for i, game in enumerate(data['games'][:5], 1):
                print(f"   {i}. {game['title']}")
            
            return True
        else:
            print(f"❌ Titles endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Titles endpoint error: {e}")
        return False

def test_simple_games_endpoint():
    """Test the simple games endpoint"""
    print("\n🎮 Testing simple games endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE}/api/xbox/games?limit=5&format=simple&concurrent=3")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {data['count']} games in {end_time - start_time:.2f} seconds")
            print(f"   Scraping time: {data['scraping_time']} seconds")
            
            print("\n🎯 Sample games:")
            for i, game in enumerate(data['games'], 1):
                print(f"   {i}. {game['title']} - {game['price']}")
            
            return True
        else:
            print(f"❌ Simple games endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Simple games endpoint error: {e}")
        return False

def test_full_games_endpoint():
    """Test the full games endpoint with detailed data"""
    print("\n🔍 Testing full games endpoint...")
    try:
        start_time = time.time()
        response = requests.get(f"{API_BASE}/api/xbox/games?limit=3&concurrent=2")
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {data['count']} detailed games in {end_time - start_time:.2f} seconds")
            print(f"   Scraping time: {data['scraping_time']} seconds")
            print(f"   Average per game: {data['average_time_per_game']} seconds")
            
            if data['games']:
                game = data['games'][0]
                print(f"\n📊 Sample detailed game:")
                print(f"   Title: {game['title']}")
                print(f"   Price: {game['price']}")
                print(f"   Publisher: {game['publisher']}")
                print(f"   Release Date: {game['release_date']}")
                print(f"   Platforms: {game['platforms']}")
                if game['description']:
                    print(f"   Description: {game['description'][:100]}...")
            
            return True
        else:
            print(f"❌ Full games endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Full games endpoint error: {e}")
        return False

def test_cache_functionality():
    """Test caching by making the same request twice"""
    print("\n💾 Testing cache functionality...")
    try:
        # First request
        start_time = time.time()
        response1 = requests.get(f"{API_BASE}/api/xbox/games/titles?limit=15")
        time1 = time.time() - start_time
        
        # Second request (should be cached)
        start_time = time.time()
        response2 = requests.get(f"{API_BASE}/api/xbox/games/titles?limit=15")
        time2 = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            print(f"✅ First request: {time1:.2f} seconds")
            print(f"✅ Second request: {time2:.2f} seconds")
            
            if time2 < time1 * 0.1:  # Second request should be much faster
                print("✅ Caching is working! Second request was much faster.")
            else:
                print("⚠️  Caching might not be working as expected.")
            
            return True
        else:
            print("❌ Cache test failed")
            return False
    except Exception as e:
        print(f"❌ Cache test error: {e}")
        return False

def show_api_documentation():
    """Get and display API documentation"""
    print("\n📚 API Documentation:")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            docs = response.json()
            print(json.dumps(docs, indent=2))
        else:
            print(f"❌ Failed to get documentation: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentation error: {e}")

def performance_test():
    """Run performance tests with different configurations"""
    print("\n⚡ Performance Testing:")
    
    test_configs = [
        {"limit": 5, "concurrent": 2, "name": "Small (5 games, 2 workers)"},
        {"limit": 10, "concurrent": 5, "name": "Medium (10 games, 5 workers)"},
        {"limit": 20, "concurrent": 8, "name": "Large (20 games, 8 workers)"},
    ]
    
    for config in test_configs:
        print(f"\n🔄 Testing {config['name']}...")
        try:
            start_time = time.time()
            response = requests.get(
                f"{API_BASE}/api/xbox/games",
                params={
                    "limit": config["limit"],
                    "concurrent": config["concurrent"],
                    "format": "simple"
                },
                timeout=120
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                total_time = end_time - start_time
                scraping_time = data.get('scraping_time', 0)
                
                print(f"   ✅ Total time: {total_time:.2f}s")
                print(f"   ✅ Scraping time: {scraping_time:.2f}s")
                print(f"   ✅ Games retrieved: {data['count']}")
                print(f"   ✅ Games per second: {data['count'] / scraping_time:.2f}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Xbox Games API Test Client\n")
    
    # Check if API is running
    if not test_health_check():
        print("\n❌ API is not running! Start it with: python xbox_api.py")
        return
    
    # Run tests
    test_titles_endpoint()
    test_simple_games_endpoint()
    test_full_games_endpoint()
    test_cache_functionality()
    
    # Performance tests
    performance_test()
    
    # Show documentation
    show_api_documentation()
    
    print("\n🎉 All tests completed!")
    print("\n💡 Try these commands yourself:")
    print(f"   curl '{API_BASE}/api/xbox/games/titles?limit=20'")
    print(f"   curl '{API_BASE}/api/xbox/games?limit=10&format=simple'")
    print(f"   curl '{API_BASE}/api/health'")

if __name__ == "__main__":
    main()