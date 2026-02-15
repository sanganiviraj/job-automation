"""
Test script to verify Playwright installation
"""
import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    print("Testing Playwright installation...")
    
    try:
        print("1. Starting Playwright...")
        playwright = await async_playwright().start()
        print("   [OK] Playwright started")
        
        print("2. Launching Chromium...")
        browser = await playwright.chromium.launch(headless=False)
        print("   [OK] Browser launched")
        
        print("3. Creating page...")
        page = await browser.new_page()
        print("   [OK] Page created")
        
        print("4. Navigating to Google...")
        await page.goto("https://www.google.com")
        print("   [OK] Navigation successful")
        
        print("5. Getting page title...")
        title = await page.title()
        print(f"   [OK] Page title: {title}")
        
        print("6. Closing browser...")
        await browser.close()
        await playwright.stop()
        print("   [OK] Browser closed")
        
        print("\n[SUCCESS] Playwright is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Playwright test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_playwright())
