import os
import platform
import subprocess
import re
import zipfile
import shutil
import requests
import json
from pathlib import Path

def get_chrome_version():
    """Get the installed Chrome version"""
    system = platform.system().lower()
    try:
        if system == "windows":
            # Use PowerShell to get Chrome version
            cmd = ['powershell', '-command', '(Get-Item "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe").VersionInfo.ProductVersion']
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = process.stdout.strip()
            return version
        elif system == "darwin":  # macOS
            cmd = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"]
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = re.search(r'Chrome\s+(\d+\.\d+\.\d+\.\d+)', process.stdout)
            if version:
                return version.group(1)
        elif system == "linux":
            cmd = ["google-chrome", "--version"]
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = re.search(r'Chrome\s+(\d+\.\d+\.\d+\.\d+)', process.stdout)
            if version:
                return version.group(1)
    except Exception as e:
        print(f"Error getting Chrome version: {e}")
    
    # Fallback: Try to get version from registry on Windows
    if system == "windows":
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
            version, _ = winreg.QueryValueEx(key, "version")
            return version
        except Exception as e:
            print(f"Error getting Chrome version from registry: {e}")
    
    return None

def get_major_version(version):
    """Extract major version number from version string"""
    if version:
        return version.split('.')[0]
    return None

def download_chromedriver(chrome_version):
    """Download the appropriate ChromeDriver version"""
    major_version = get_major_version(chrome_version)
    if not major_version:
        print("Could not determine Chrome major version")
        return False
    
    # Get the latest ChromeDriver version for this Chrome major version
    try:
        # First try the new Chrome for Testing API
        url = f"https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        response = requests.get(url)
        data = response.json()
        
        # Find the latest version that matches our major version
        matching_versions = []
        for version_info in data.get('versions', []):
            version = version_info.get('version', '')
            if version.startswith(f"{major_version}."):
                matching_versions.append(version_info)
        
        if not matching_versions:
            print(f"No matching ChromeDriver found for Chrome version {chrome_version}")
            return False
        
        # Sort by version and get the latest
        latest_version_info = sorted(matching_versions, key=lambda x: x['version'])[-1]
        version = latest_version_info['version']
        
        # Find the chromedriver download URL for our platform
        system = platform.system().lower()
        architecture = platform.machine().lower()
        
        download_url = None
        for download in latest_version_info.get('downloads', {}).get('chromedriver', []):
            platform_name = download.get('platform')
            if system == 'windows' and platform_name == 'win64':
                download_url = download.get('url')
                break
            elif system == 'darwin':  # macOS
                if 'arm' in architecture and platform_name == 'mac-arm64':
                    download_url = download.get('url')
                    break
                elif 'arm' not in architecture and platform_name == 'mac-x64':
                    download_url = download.get('url')
                    break
            elif system == 'linux' and platform_name == 'linux64':
                download_url = download.get('url')
                break
        
        if not download_url:
            print(f"Could not find download URL for ChromeDriver {version} on {system} {architecture}")
            return False
        
        # Download and extract the ChromeDriver
        print(f"Downloading ChromeDriver version {version} for Chrome {chrome_version}...")
        response = requests.get(download_url, stream=True)
        zip_path = os.path.join(os.path.dirname(__file__), "chromedriver_download.zip")
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file
        extract_dir = os.path.join(os.path.dirname(__file__), "chromedriver_extract")
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        os.makedirs(extract_dir)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find the chromedriver executable in the extracted files
        chromedriver_exec = None
        for root, dirs, files in os.walk(extract_dir):
            for file in files:
                if file == "chromedriver.exe" or file == "chromedriver":
                    chromedriver_exec = os.path.join(root, file)
                    break
            if chromedriver_exec:
                break
        
        if not chromedriver_exec:
            print("Could not find chromedriver executable in the downloaded package")
            return False
        
        # Determine the destination directory
        base_path = os.path.join(os.path.dirname(__file__), "chromedriver")
        if system == "windows":
            dest_dir = os.path.join(base_path, "chromedriver-win64")
        elif system == "linux":
            dest_dir = os.path.join(base_path, "chromedriver-linux64")
        elif system == "darwin":  # macOS
            if "arm" in architecture:
                dest_dir = os.path.join(base_path, "chromedriver-mac-arm64")
            else:
                dest_dir = os.path.join(base_path, "chromedriver-mac-x64")
        else:
            print(f"Unsupported operating system: {system}")
            return False
        
        # Ensure the destination directory exists
        os.makedirs(dest_dir, exist_ok=True)
        
        # Copy the chromedriver executable to the destination
        dest_path = os.path.join(dest_dir, os.path.basename(chromedriver_exec))
        shutil.copy2(chromedriver_exec, dest_path)
        
        # Make the file executable on Unix-like systems
        if system != "windows":
            os.chmod(dest_path, 0o755)
        
        # Clean up temporary files
        try:
            os.remove(zip_path)
            shutil.rmtree(extract_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temporary files: {e}")
        
        print(f"Successfully installed ChromeDriver {version} to {dest_path}")
        return True
        
    except Exception as e:
        print(f"Error downloading ChromeDriver: {e}")
        return False

def ensure_compatible_chromedriver():
    """Ensure that a compatible ChromeDriver is available"""
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("Could not determine Chrome version. Please download ChromeDriver manually.")
        return False
    
    print(f"Detected Chrome version: {chrome_version}")
    
    # Check if we need to download a new ChromeDriver
    system = platform.system().lower()
    architecture = platform.machine().lower()
    
    base_path = os.path.join(os.path.dirname(__file__), "chromedriver")
    if system == "windows":
        driver_path = os.path.join(base_path, "chromedriver-win64", "chromedriver.exe")
    elif system == "linux":
        driver_path = os.path.join(base_path, "chromedriver-linux64", "chromedriver")
    elif system == "darwin":  # macOS
        if "arm" in architecture:
            driver_path = os.path.join(base_path, "chromedriver-mac-arm64", "chromedriver")
        else:
            driver_path = os.path.join(base_path, "chromedriver-mac-x64", "chromedriver")
    else:
        print(f"Unsupported operating system: {system}")
        return False
    
    # If ChromeDriver doesn't exist, download it
    if not os.path.exists(driver_path):
        print("ChromeDriver not found. Downloading...")
        return download_chromedriver(chrome_version)
    
    # Try to get the version of the existing ChromeDriver
    try:
        cmd = [driver_path, "--version"]
        process = subprocess.run(cmd, capture_output=True, text=True)
        driver_version_match = re.search(r'ChromeDriver\s+(\d+\.\d+\.\d+)', process.stdout)
        if driver_version_match:
            driver_version = driver_version_match.group(1)
            driver_major = driver_version.split('.')[0]
            chrome_major = chrome_version.split('.')[0]
            
            if driver_major == chrome_major:
                print(f"ChromeDriver version {driver_version} is compatible with Chrome version {chrome_version}")
                return True
            else:
                print(f"ChromeDriver version {driver_version} is not compatible with Chrome version {chrome_version}. Downloading compatible version...")
                return download_chromedriver(chrome_version)
    except Exception as e:
        print(f"Error checking ChromeDriver version: {e}")
    
    # If we couldn't determine the version or there was an error, download a new one to be safe
    print("Could not verify ChromeDriver version. Downloading compatible version...")
    return download_chromedriver(chrome_version)

if __name__ == "__main__":
    ensure_compatible_chromedriver()
