# 🎬 YouTube Playlist Downloader

A simple and efficient Python script for downloading YouTube videos with high-quality video and audio merging.

## ✨ Features

- 🎥 Downloads videos in up to 1080p quality
- 🎵 Merges video and audio streams automatically
- 📁 Organizes downloads into separate folders for each video
- 🛡️ Error handling for problematic videos
- 📝 Clean folder structure with video titles as folder names

## 📋 Requirements

- Python 3.6 or higher
- `yt-dlp` library
- FFmpeg (for video/audio merging)

## 🚀 Installation

1. **Clone or download this repository**

2. **Install required Python package:**

   ```bash
   pip install yt-dlp
   ```

3. **Install FFmpeg:**

   **Windows:**

   - Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - Add to system PATH

   **macOS:**

   ```bash
   brew install ffmpeg
   ```

   **Linux:**

   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

## 💻 Usage

1. Run the script:

   ```bash
   python downloader.py
   ```

2. Enter the YouTube video URL when prompted

3. Videos will be downloaded to the `my_youtube_downloads` folder

## ⚙️ Configuration

You can customize the download folder by modifying the `base_download_folder` variable in `downloader.py`:

```python
base_download_folder = 'my_youtube_downloads'  # Change this to your preferred folder
```

## 🔧 Technical Details

- **Video Quality:** Best available up to 1080p
- **Output Format:** MP4
- **Audio/Video:** Automatically merged with FFmpeg
- **Error Handling:** Continues even if individual downloads fail
