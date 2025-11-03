"""
Test script to demonstrate downloading YouTube videos and playlists
using the YouTube Downloader API.
"""

import requests
import json
import sys
import time

def download_content(api_url, content_url, quality='720p'):
    """
    Download a YouTube video or playlist using the API
    
    Args:
        api_url (str): The base URL of the API (e.g., http://localhost:2000)
        content_url (str): The YouTube video or playlist URL to download
        quality (str): Quality of the download (1080p, 720p, 480p, best)
    
    Returns:
        dict: The API response
    """
    download_endpoint = f"{api_url}/download"

    payload = {
        "url": content_url,
        "quality": quality
    }

    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"Sending download request for: {content_url}")
        print(f"Quality: {quality}")

        response = requests.post(
            download_endpoint, 
            data=json.dumps(payload), 
            headers=headers,
            timeout=300
        )

        return {
            'status_code': response.status_code,
            'response': response.json() if response.content else {}
        }
            
    except requests.exceptions.Timeout:
        return {
            'status_code': 0,
            'response': {'error': 'Request timeout', 'status': 'failed'}
        }
    except requests.exceptions.ConnectionError:
        return {
            'status_code': 0,
            'response': {'error': 'Connection error', 'status': 'failed'}
        }
    except Exception as e:
        return {
            'status_code': 0,
            'response': {'error': f'Error: {str(e)}', 'status': 'failed'}
        }

def main():
    api_url = "http://localhost:2000"
    content_url = None
    quality = "720p"

    if len(sys.argv) < 2:
        print("Usage: python test_download.py <youtube_url> [api_url] [quality]")
        print("Example: python test_download.py 'https://www.youtube.com/watch?v=example'")
        print("Example: python test_download.py 'https://www.youtube.com/playlist?list=example' http://localhost:2000 1080p")
        sys.exit(1)
    
    content_url = sys.argv[1]
    
    if len(sys.argv) > 2:
        api_url = sys.argv[2]
    
    if len(sys.argv) > 3:
        quality = sys.argv[3]
    
    print(f"YouTube Downloader API Test")
    print("=" * 40)
    print(f"API URL: {api_url}")
    print(f"Content URL: {content_url}")
    print(f"Quality: {quality}")
    print("=" * 40)

    result = download_content(api_url, content_url, quality)

    print(f"\nResponse Status: {result['status_code']}")
    print("Response Data:")
    print(json.dumps(result['response'], indent=2))

    if result['status_code'] == 200 and result['response'].get('status') == 'success':
        print("\n✓ Download request completed successfully!")
        if result['response'].get('type') == 'playlist':
            playlist = result['response'].get('playlist', {})
            print(f"  Playlist: {playlist.get('title')}")
            print(f"  Entries: {playlist.get('entries_count')}")
        else:
            video = result['response'].get('video', {})
            print(f"  Video: {video.get('title')}")
            print(f"  File Size: {video.get('filesize_mb')} MB")
            print(f"  Filename: {video.get('filename')}")
    else:
        print("\n✗ Download request failed!")
        error = result['response'].get('error', 'Unknown error')
        print(f"  Error: {error}")

if __name__ == "__main__":
    main()