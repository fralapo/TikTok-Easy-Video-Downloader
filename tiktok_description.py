from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import platform
import sys
from chromedriver_manager import ensure_compatible_chromedriver

def get_chromedriver_path():
    """
    Automatically detect the correct ChromeDriver based on the operating system
    """
    base_path = os.path.join(os.path.dirname(__file__), "chromedriver")
    system = platform.system().lower()
    architecture = platform.machine().lower()

    if system == "windows":
        return os.path.join(base_path, "chromedriver-win64", "chromedriver.exe")
    elif system == "linux":
        return os.path.join(base_path, "chromedriver-linux64", "chromedriver")
    elif system == "darwin":  # macOS
        if "arm" in architecture:
            return os.path.join(base_path, "chromedriver-mac-arm64", "chromedriver")
        else:
            return os.path.join(base_path, "chromedriver-mac-x64", "chromedriver")
    else:
        raise Exception(f"Unsupported operating system: {system}")

def load_cookies_from_file(driver, cookie_file, url):
    """
    Load cookies from file and add them to Selenium driver
    """
    driver.get(url)  # Necessary to set the domain
    with open(cookie_file, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("#") or not line.strip():
                continue  # Skip comments and empty lines
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookie = {
                    "domain": parts[0],
                    "httpOnly": parts[3].lower() == "true",
                    "secure": parts[3].lower() == "true",
                    "expiry": int(parts[4]) if parts[4].isdigit() else None,
                    "name": parts[5],
                    "value": parts[6],
                    "path": parts[2]
                }
                driver.add_cookie(cookie)

def get_tiktok_description_with_cookies(url, cookie_file):
    """
    Get TikTok video description using Selenium and cookies
    """
    # Ensure we have a compatible ChromeDriver
    ensure_compatible_chromedriver()
    
    # Configure Selenium with Chrome
    options = Options()
    options.add_argument("--headless")  # Headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Add flags to suppress WebGL errors
    options.add_argument("--enable-unsafe-swiftshader")
    options.add_argument("--ignore-gpu-blocklist")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-webgl")
    options.add_argument("--disable-webgl2")
    options.add_argument("--log-level=3")  # Suppress console logging
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    try:
        driver_path = get_chromedriver_path()
        if not os.path.exists(driver_path):
            print("ChromeDriver not found at path:", driver_path)
            return None
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        # Load cookies
        driver.get("https://www.tiktok.com")
        load_cookies_from_file(driver, cookie_file, "https://www.tiktok.com")

        # Navigate to the video
        print(f"Navigating to {url} to extract description")
        driver.get(url)
        time.sleep(8)  # Increased wait time for page to load

        # Try multiple selectors to find the description element
        selectors = [
            "h1[data-e2e='browse-video-desc']",  # Original selector
            "div[data-e2e='browse-video-desc']",  # Alternative selector
            "div.tiktok-1ejylhp-DivContainer.e11995xo0 span",  # Another possible selector
            ".video-meta-caption",  # Another possible selector
            ".tiktok-1wrhn5c-SpanText",  # Another possible selector
            "div[class*='desc'] span",  # Generic selector targeting description classes
            "div[class*='caption'] span"  # Generic selector targeting caption classes
        ]
        
        description = None
        for selector in selectors:
            try:
                print(f"Trying selector: {selector}")
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        text = element.text.strip()
                        if text and len(text) > 5:  # Ensure we have meaningful text
                            print(f"Found description with selector {selector}: {text[:30]}...")
                            description = text
                            break
                if description:
                    break
            except Exception as e:
                print(f"Error with selector {selector}: {str(e)}")
                continue
        
        # If no description found with selectors, try getting page source and extracting
        if not description:
            try:
                print("Trying to extract from page source")
                page_source = driver.page_source
                # Look for common patterns in the HTML that might contain the description
                import re
                desc_patterns = [
                    r'"desc":"([^"]+)"',
                    r'"description":"([^"]+)"',
                    r'"caption":"([^"]+)"'
                ]
                
                for pattern in desc_patterns:
                    matches = re.findall(pattern, page_source)
                    if matches:
                        description = matches[0]
                        print(f"Found description in page source: {description[:30]}...")
                        break
            except Exception as e:
                print(f"Error extracting from page source: {str(e)}")
        
        return description
    except Exception as e:
        print(f"Error in get_tiktok_description_with_cookies: {str(e)}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()
