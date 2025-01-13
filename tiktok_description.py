from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import platform
import sys

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
    # Configure Selenium with Chrome
    options = Options()
    options.add_argument("--headless")  # Headless mode
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver_path = get_chromedriver_path()
        if not os.path.exists(driver_path):
            return None
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        # Load cookies
        driver.get("https://www.tiktok.com")
        load_cookies_from_file(driver, cookie_file, "https://www.tiktok.com")

        # Navigate to the video
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        # Find the description element
        try:
            h1_element = driver.find_element(By.CSS_SELECTOR, "h1[data-e2e='browse-video-desc']")
            description = h1_element.text
            return description
        except Exception:
            return None
    except Exception:
        return None
    finally:
        if 'driver' in locals():
            driver.quit()
