from yt_dlp import YoutubeDL

def download_video(video_url, base_download_folder='downloads'):
    ydl_opts = {
        'format': 'bestvideo[height<=1080]+bestaudio/best',
        'outtmpl': f'{base_download_folder}/%(title)s/%(title)s.%(ext)s',
        'ignoreerrors': True,
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }]
    }
    with YoutubeDL(ydl_opts) as ydl:
        print(f"Downloading video: {video_url} into separate folder")
        ydl.download([video_url])
video_url = input("Enter YouTube video URL: ")
base_download_folder = 'my_youtube_downloads' 
download_video(video_url, base_download_folder)