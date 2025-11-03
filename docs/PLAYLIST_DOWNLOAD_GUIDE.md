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

```json
{
  "url": "YOUR_YOUTUBE_VIDEO_OR_PLAYLIST_URL"
}
```

### 4. Example with curl

For a single video:

```bash
curl -X POST http://localhost:2000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

For a playlist:

```bash
curl -X POST http://localhost:2000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/playlist?list=PLAYLIST_ID"}'
```

### 5. Optional Quality Parameter

You can also specify the quality of the download:

```json
{
  "url": "YOUR_YOUTUBE_URL",
  "quality": "720p"
}
```

Available quality options:

- `1080p`
- `720p` (default)
- `480p`
- `best`

## Response Format

### For Single Videos

```json
{
  "status": "success",
  "message": "Video downloaded successfully",
  "type": "video",
  "video": {
    "title": "Video Title",
    "duration": 300,
    "uploader": "Uploader Name",
    "view_count": 10000,
    "filesize_mb": 45.5,
    "quality": "720p",
    "format": "mp4",
    "filename": "Video Title.mp4"
  }
}
```

### For Playlists

```json
{
  "status": "success",
  "message": "Playlist 'Playlist Title' downloaded successfully",
  "type": "playlist",
  "playlist": {
    "title": "Playlist Title",
    "entries_count": 10,
    "downloaded_items": [
      {
        "title": "Video 1 Title",
        "duration": 300,
        "filesize_mb": 45.5
      },
      {
        "title": "Video 2 Title",
        "duration": 240,
        "filesize_mb": 32.1
      }
    ]
  }
}
```

## Downloaded Files

Downloaded files are saved in the `downloads` directory by default. The filename format is:

```
{Video Title}.{extension}
```

## Error Handling

If there's an error, you'll receive a response like:

```json
{
  "error": "Error description",
  "status": "failed"
}
```

Common errors:

- File size exceeds the limit (configured via `MAX_DOWNLOAD_SIZE` environment variable)
- Invalid URL
- Network issues
- Video not available

## Environment Variables

You can configure the downloader using these environment variables:

- `MAX_DOWNLOAD_SIZE`: Maximum file size in MB (default: 100)
- `DOWNLOAD_FOLDER`: Folder where downloads are saved (default: downloads)
- `DEBUG`: Enable debug mode (default: False)

Example with environment variables:

```bash
MAX_DOWNLOAD_SIZE=200 DOWNLOAD_FOLDER=/tmp/downloads python app/main.py
```
