import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from tik_tok_downloader import TikTokDownloader
from typing import List
import threading
import os

class TikTokDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TikTok Video Downloader")
        self.root.geometry("600x500")
        self.cookies_path = None
        self.save_path = 'tiktok_videos'
        self.use_description = False
        self.downloader = TikTokDownloader(
            save_path=self.save_path,
            use_description=self.use_description
        )
        
        self.create_widgets()
        self.running = False
        self.check_for_cookies()
        
    def check_for_cookies(self):
        """Check for cookies.txt in root directory and load if present"""
        cookie_file = os.path.join(os.path.dirname(__file__), "cookies.txt")
        if os.path.exists(cookie_file):
            try:
                self.load_cookies(cookie_file)
                self.cookie_status.config(text="Cookies loaded automatically from cookies.txt", foreground="green")
            except Exception as e:
                self.cookie_status.config(text="Failed to load cookies: Invalid format", foreground="red")
        else:
            self.cookie_status.config(text="No cookies loaded. Please load cookies.txt manually", foreground="orange")
        
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cookie status frame
        cookie_frame = tk.Frame(main_frame)
        cookie_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Cookie status label
        self.cookie_status = tk.Label(cookie_frame, text="Checking for cookies...", anchor="w")
        self.cookie_status.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load cookies button
        cookie_btn = tk.Button(cookie_frame, text="Load Cookies", command=self.load_cookies_dialog)
        cookie_btn.pack(side=tk.RIGHT)
        
        # Input frame
        input_frame = tk.LabelFrame(main_frame, text="Input Links", padx=10, pady=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Text area for links
        self.link_text = scrolledtext.ScrolledText(input_frame, height=10, wrap=tk.WORD)
        self.link_text.pack(fill=tk.BOTH, expand=True)
        
        # Settings frame
        settings_frame = tk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Output folder button
        folder_btn = tk.Button(settings_frame, text="Set Output Folder", command=self.set_output_folder)
        folder_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Naming option
        self.naming_var = tk.BooleanVar()
        naming_check = tk.Checkbutton(
            settings_frame,
            text="Use Description as Filename",
            variable=self.naming_var,
            command=self.toggle_naming
        )
        naming_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Upload button
        upload_btn = tk.Button(button_frame, text="Upload TXT File", command=self.upload_txt)
        upload_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Download button
        self.download_btn = tk.Button(button_frame, text="Start Download", command=self.start_download)
        self.download_btn.pack(side=tk.LEFT)
        
        # Progress frame
        progress_frame = tk.LabelFrame(main_frame, text="Progress", padx=10, pady=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Progress text
        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=10, wrap=tk.WORD)
        self.progress_text.pack(fill=tk.BOTH, expand=True)
        self.progress_text.config(state=tk.DISABLED)
        
    def load_cookies_dialog(self):
        """Open file dialog to load cookies"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")],
            title="Select cookies.txt file"
        )
        if file_path:
            try:
                self.load_cookies(file_path)
                self.cookie_status.config(text=f"Cookies loaded from: {os.path.basename(file_path)}", foreground="green")
            except Exception as e:
                self.cookie_status.config(text=f"Failed to load cookies: {str(e)}", foreground="red")
        
    def load_cookies(self, file_path: str):
        """Load cookies from file"""
        if not os.path.exists(file_path):
            raise Exception("File does not exist")
        
        # Basic validation of cookies file
        with open(file_path, "r") as f:
            first_line = f.readline()
            # More lenient validation since we know the file works
            if not first_line.strip():
                raise Exception("File appears to be empty")
        
        self.cookies_path = file_path
        self.update_downloader()
        
    def set_output_folder(self):
        """Set output folder for downloads"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.save_path = folder_path
            self.update_downloader()
            messagebox.showinfo("Output Folder Set", f"Videos will be saved to: {folder_path}")
        
    def toggle_naming(self):
        """Toggle between TikTok ID and description naming"""
        self.use_description = self.naming_var.get()
        self.update_downloader()
        
    def update_downloader(self):
        """Update downloader instance with current settings"""
        self.downloader = TikTokDownloader(
            save_path=self.save_path,
            cookies=self.cookies_path,
            use_description=self.use_description
        )
        
    def upload_txt(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    links = file.read()
                    self.link_text.delete(1.0, tk.END)
                    self.link_text.insert(tk.END, links)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
                
    def get_links(self) -> List[str]:
        text = self.link_text.get(1.0, tk.END).strip()
        return [link.strip() for link in text.split('\n') if link.strip()]
    
    def update_progress(self, message: str):
        self.progress_text.config(state=tk.NORMAL)
        self.progress_text.insert(tk.END, message + "\n")
        self.progress_text.config(state=tk.DISABLED)
        self.progress_text.yview(tk.END)
        
    def download_thread(self, links: List[str]):
        self.running = True
        self.download_btn.config(state=tk.DISABLED)
        
        total = len(links)
        for i, link in enumerate(links):
            if not self.running:
                break
                
            self.update_progress(f"Downloading {i+1}/{total}: {link}")
            try:
                result = self.downloader.download_video(link)
                if result:
                    self.update_progress(f"Success: {result}")
                else:
                    self.update_progress(f"Failed: {link}")
            except Exception as e:
                self.update_progress(f"Error: {str(e)}")
                
        self.update_progress("Download process completed!")
        self.running = False
        self.download_btn.config(state=tk.NORMAL)
        
    def start_download(self):
        if self.running:
            return
            
        links = self.get_links()
        if not links:
            messagebox.showwarning("No Links", "Please enter or upload some TikTok links!")
            return
            
        if not self.cookies_path:
            messagebox.showwarning("No Cookies", "Please load cookies file first!")
            return
            
        threading.Thread(target=self.download_thread, args=(links,), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = TikTokDownloaderGUI(root)
    root.mainloop()
