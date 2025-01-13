# 🎵 TikTok Easy Video Downloader

![TikTok Cover](TikTok.png)

A streamlined Python utility for downloading TikTok videos, designed with user convenience, robust error handling, and enhanced features for a seamless experience.

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)
[![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=green&labelColor=green)](https://www.jetbrains.com/pycharm/)
[![Git](https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

---

## ✨ Key Features

- 📥 High-quality TikTok video downloads.
- 🎯 Option to use video descriptions as filenames.
- 🗂️ Automatic directory creation and organization.
- 🔄 Live progress tracking and updates.
- 🛡️ Comprehensive error handling for smoother operations.
- 🌐 Cookie integration for enhanced compatibility.
- 📝 In-depth logging for process monitoring.

---

## 🚀 Requirements

Before you begin, ensure you have:

- Python 3.7 or higher installed.
- Chrome browser installed on your system.
- A TikTok account (for exporting cookies).

---

## 📦 Installation Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/fralapo/TikTok-Easy-Video-Downloader
cd TikTok-Easy-Video-Downloader
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Set Up ChromeDriver
1. Download the appropriate ChromeDriver version from [ChromeDriver](https://googlechromelabs.github.io/chrome-for-testing/#stable).
2. Place the executable in the `chromedriver` directory:
   ```
   chromedriver/
   ├── chromedriver-linux64/
   ├── chromedriver-mac-arm64/
   ├── chromedriver-mac-x64/
   └── chromedriver-win64/
   ```

---

## 🔐 Configuring Cookies

To access TikTok content, you'll need to export cookies from a logged-in browser session.

1. Install the [Get cookies.txt LOCALLY]([https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)) extension for Chrome.
2. Log in to your TikTok account using Chrome.
3. Navigate to a TikTok video.
4. Use the extension to export cookies as `cookies.txt`.
5. Place the `cookies.txt` file in the root directory of the project.

---

## 💻 Usage Instructions

### Command Line Usage

Basic download:
```bash
python tik_tok_downloader.py https://www.tiktok.com/@username/video/1234567890 --cookies cookies.txt
```

Use video descriptions as filenames:
```bash
python tik_tok_downloader.py https://www.tiktok.com/@username/video/1234567890 --use-description --cookies cookies.txt
```

Set custom output directory:
```bash
python tik_tok_downloader.py https://www.tiktok.com/@username/video/1234567890 --output my_videos --cookies cookies.txt
```

Download multiple videos from a file:
```bash
python tik_tok_downloader.py --file links.txt --cookies cookies.txt
```

### Graphical User Interface (GUI)

To use the GUI:
```bash
python tiktok_gui.py
```

#### GUI Features:
- Automatic or manual cookie loading.
- Bulk URL input via paste or file upload.
- Customizable output directory.
- Toggle to use video descriptions for filenames.
- Real-time progress updates.

### Command Line Options

| Argument            | Description                                    | Default          |
|---------------------|------------------------------------------------|------------------|
| URL(s)              | TikTok video URL(s) to download               | Required         |
| `--cookies`         | Path to cookies.txt file                      | `cookies.txt`    |
| `--output`, `-o`    | Directory for saving videos                   | `tiktok_videos`  |
| `--file`, `-f`      | File containing TikTok URLs (one per line)     | None             |
| `--use-description`, `-d` | Use video description as filename       | False            |

---

## 🤝 Contributing

We welcome contributions to improve this project! Follow these steps to contribute:

1. Fork this repository.
2. Create a new branch for your feature:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add AmazingFeature"
   ```
4. Push your branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request.

---

## 📝 License

This project is open-sourced under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This tool is designed for educational purposes only. Please respect TikTok's terms of service and the rights of content creators.

---

## 📞 Support

Need help? Have questions?

- Open an issue on the [GitHub Issues](https://github.com/fralapo/TikTok-Easy-Video-Downloader/issues) page.
- Refer to the documentation for further assistance.
