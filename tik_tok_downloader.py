import yt_dlp
import os
import re
import argparse
from typing import Optional, Dict, Any
from datetime import datetime
from tiktok_description import get_tiktok_description_with_cookies

class TikTokDownloader:
    def __init__(self, save_path: str = 'tiktok_videos', cookies: Optional[str] = None, use_description: bool = False):
        """
        Initialize TikTok downloader with configurable save path and optional cookies
        
        Args:
            save_path (str): Directory where videos will be saved
            cookies (Optional[str]): Path to cookies.txt file
            use_description (bool): Use video description as filename
        """
        self.save_path = save_path
        self.cookies = cookies
        self.use_description = use_description
        self.create_save_directory()
    
    def create_save_directory(self) -> None:
        """Create the save directory if it doesn't exist"""
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate if the provided URL is a TikTok URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        tiktok_pattern = r'https?://((?:vm|vt|www)\.)?tiktok\.com/.*'
        return bool(re.match(tiktok_pattern, url))
    
    @staticmethod
    def progress_hook(d: Dict[str, Any]) -> None:
        """
        Hook to display download progress
        
        Args:
            d (Dict[str, Any]): Progress information dictionary
        """
        if d['status'] == 'downloading':
            progress = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            print(f"Downloading: {progress} at {speed} ETA: {eta}", end='\r')
        elif d['status'] == 'finished':
            print("\nDownload completed, finalizing...")
    
    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing invalid characters
        
        Args:
            filename (str): Original filename
            
        Returns:
            str: Sanitized filename
        """
        # Remove invalid Windows characters
        invalid_chars = r'<>:"/\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')
        
        # Remove multiple spaces
        filename = ' '.join(filename.split())
        
        # Limit length to 255 characters (Windows limit)
        return filename[:255]
    
    def get_description(self, video_url: str) -> Optional[str]:
        """
        Get video description using Selenium
        
        Args:
            video_url (str): URL of the TikTok video
            
        Returns:
            Optional[str]: Video description or None if not found
        """
        if self.cookies and os.path.exists(self.cookies):
            description = get_tiktok_description_with_cookies(video_url, self.cookies)
            if description:
                return self.sanitize_filename(description)
        return None
    
    def rename_with_description(self, file_path: str, description: str) -> str:
        """
        Rename file with video description
        
        Args:
            file_path (str): Path to the original file
            description (str): Video description
            
        Returns:
            str: New file path
        """
        directory = os.path.dirname(file_path)
        extension = os.path.splitext(file_path)[1]
        new_filename = f"{description}{extension}"
        new_path = os.path.join(directory, new_filename)
        
        # Handle filename conflicts
        counter = 1
        while os.path.exists(new_path):
            new_filename = f"{description}_{counter}{extension}"
            new_path = os.path.join(directory, new_filename)
            counter += 1
        
        try:
            os.rename(file_path, new_path)
            return new_path
        except Exception as e:
            print(f"Warning: Could not rename file: {str(e)}")
            return file_path
    
    def get_filename(self, video_url: str) -> str:
        """
        Generate filename for the video
        
        Args:
            video_url (str): Video URL
            
        Returns:
            str: Generated filename
        """
        tiktok_id = re.search(r'/video/(\d+)', video_url)
        if tiktok_id:
            return f"tiktok_{tiktok_id.group(1)}.mp4"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"tiktok_{timestamp}.mp4"
    
    def download_video(self, video_url: str) -> Optional[str]:
        """
        Download TikTok video
        
        Args:
            video_url (str): URL of the TikTok video
            
        Returns:
            Optional[str]: Path to downloaded file if successful, None otherwise
        """
        if not self.validate_url(video_url):
            print("Error: Invalid TikTok URL")
            return None

        ydl_opts = {
            'format': 'best',
            'noplaylist': True,
            'quiet': False,
            'progress_hooks': [self.progress_hook],
            'extractor_args': {'tiktok': {'webpage_download': True}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }

        # Add cookies if provided
        if self.cookies and os.path.exists(self.cookies):
            ydl_opts['cookiefile'] = self.cookies

        try:
            # Generate initial filename
            filename = self.get_filename(video_url)
            output_path = os.path.join(self.save_path, filename)
            
            # Update outtmpl with the final filename
            ydl_opts['outtmpl'] = output_path
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
                # If description naming is enabled, try to rename the file
                if self.use_description:
                    description = self.get_description(video_url)
                    if description:
                        new_path = self.rename_with_description(output_path, description)
                        if new_path != output_path:
                            print(f"\nVideo successfully downloaded and renamed: {new_path}")
                            return new_path
                        else:
                            print(f"\nVideo successfully downloaded (could not rename): {output_path}")
                            return output_path
                    else:
                        print(f"\nVideo successfully downloaded (could not get description): {output_path}")
                        return output_path
                
                print(f"\nVideo successfully downloaded: {output_path}")
                return output_path
                
        except yt_dlp.utils.DownloadError as e:
            print(f"Error downloading video: {str(e)}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
        
        return None

def main():
    parser = argparse.ArgumentParser(description="TikTok Video Downloader")
    parser.add_argument('urls', nargs='*', help="TikTok URLs to download")
    parser.add_argument('--cookies', help="Path to cookies.txt file")
    parser.add_argument('--output', '-o', default='tiktok_videos', 
                       help="Output directory for downloaded videos")
    parser.add_argument('--file', '-f', help="Text file containing TikTok URLs (one per line)")
    parser.add_argument('--use-description', '-d', action='store_true',
                       help="Use video description as filename instead of TikTok ID")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = TikTokDownloader(
        save_path=args.output,
        cookies=args.cookies,
        use_description=args.use_description
    )
    
    # Get URLs from file if provided
    urls = args.urls
    if args.file:
        try:
            with open(args.file, 'r') as f:
                urls.extend([line.strip() for line in f if line.strip()])
        except Exception as e:
            print(f"Error reading file: {str(e)}")
            return
    
    if not urls:
        print("No URLs provided. Use --help for usage information.")
        return
    
    # Download videos
    for url in urls:
        print(f"\nDownloading: {url}")
        result = downloader.download_video(url)
        if not result:
            print(f"Failed to download: {url}")

if __name__ == "__main__":
    main()
