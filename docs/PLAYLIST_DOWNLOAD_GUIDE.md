# YouTube Playlist Download Guide

This guide explains how to use the YouTube Downloader API to download both individual videos and playlists.

## Prerequisites

1. The API server must be running
2. You need a YouTube video or playlist URL
3. You can use tools like `curl` or `httpie` to make requests

## How to Download a Playlist

### 1. Start the API Server

```bash
cd /home/prakuljain/yt
python app/main.py
```

The server will start on port 2000 by default.

### 2. Make a POST Request to the Download Endpoint

Use the following endpoint to download content:

```
POST http://localhost:2000/download
```

### 3. Request Format

Send a JSON payload with the URL of the video or playlist you want to download:

````json
{
  "url": "YOUR_YOUTUBE_VIDEO_OR_PLAYLIST_URL"
}

## Environment Variables

You can configure the downloader using these environment variables:

- `MAX_DOWNLOAD_SIZE`: Maximum file size in MB (default: 100)
- `DOWNLOAD_FOLDER`: Folder where downloads are saved (default: /downloads)
- `DEBUG`: Enable debug mode (default: False)

Example with environment variables:

```bash
MAX_DOWNLOAD_SIZE=200 DOWNLOAD_FOLDER=/downloads python app/main.py
````

## Download Location

Downloads are now stored in the `/downloads` directory at the root level, not within the app folder. Each video will be saved directly in this directory with its title as the filename.

For example:

```
/downloads/My Video Title.mp4
```
