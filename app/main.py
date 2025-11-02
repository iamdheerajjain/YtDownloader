from flask import Flask, request, jsonify
from yt_dlp import YoutubeDL
from prometheus_client import Counter, Histogram, generate_latest, Gauge
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

DEBUG = os.getenv('DEBUG', 'False') == 'True'
MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', '100'))  # MB
DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER', 'downloads')
APP_VERSION = os.getenv('APP_VERSION', '1.0.0')

# Prometheus metrics
download_requests_total = Counter(
    'download_requests_total',
    'Total number of download requests',
    ['status']
)
download_duration_seconds = Histogram(
    'download_duration_seconds',
    'Time spent processing downloads'
)
health_check_counter = Counter(
    'health_check_requests_total',
    'Total number of health check requests'
)
app_info = Gauge(
    'app_info',
    'Application information',
    ['version']
)
active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

# Set app info metric
app_info.labels(version=APP_VERSION).set(1)

# Track active requests
@app.before_request
def before_request():
    active_requests.inc()

@app.after_request
def after_request(response):
    active_requests.dec()
    return response

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    """Home endpoint - provides API information"""
    logger.info("Home endpoint accessed")
    return jsonify({
        "app": "YouTube Downloader API",
        "status": "running",
        "version": APP_VERSION,
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/ready": "Readiness check",
            "/metrics": "Prometheus metrics",
            "/download": "POST - Download video info",
            "/info": "POST - Get video info without downloading"
        },
        "environment": {
            "debug": DEBUG,
            "max_download_size_mb": MAX_DOWNLOAD_SIZE
        }
    })

@app.route('/health')
def health():
    """Liveness probe - is the application alive?"""
    health_check_counter.inc()
    logger.debug("Health check performed")
    return jsonify({
        "status": "UP",
        "timestamp": time.time(),
        "version": APP_VERSION
    })

@app.route('/ready')
def ready():
    """Readiness probe - is the application ready to serve traffic?"""
    try:
        if os.path.exists(DOWNLOAD_FOLDER) and os.access(DOWNLOAD_FOLDER, os.W_OK):
            logger.debug("Readiness check passed")
            return jsonify({
                "status": "READY",
                "checks": {
                    "download_folder": "accessible",
                    "dependencies": "loaded"
                },
                "version": APP_VERSION
            })
        else:
            logger.warning("Readiness check failed - download folder not accessible")
            return jsonify({
                "status": "NOT_READY",
                "checks": {
                    "download_folder": "not_accessible"
                },
                "version": APP_VERSION
            }), 503
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return jsonify({
            "status": "NOT_READY",
            "error": str(e),
            "version": APP_VERSION
        }), 503

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.route('/info', methods=['POST'])
def get_info():
    """Get video information without downloading"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            download_requests_total.labels(status='error').inc()
            return jsonify({"error": "No JSON data provided"}), 400
        
        video_url = data.get('url')
        
        if not video_url:
            download_requests_total.labels(status='error').inc()
            return jsonify({"error": "No URL provided"}), 400
        
        logger.info(f"Getting info for video: {video_url}")
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }  # type: dict
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Handle potential None values
            formats = info.get('formats') or []
            
            response_data = {
                "status": "success",
                "video": {
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "uploader": info.get('uploader'),
                    "view_count": info.get('view_count'),
                    "upload_date": info.get('upload_date'),
                    "description": info.get('description', '')[:200] + '...' if info.get('description') else None,
                    "thumbnail": info.get('thumbnail'),
                    "formats_available": len(formats)
                }
            }
            
            download_requests_total.labels(status='success').inc()
            duration = time.time() - start_time
            download_duration_seconds.observe(duration)
            
            logger.info(f"Successfully retrieved info for: {info.get('title')}")
            return jsonify(response_data)
            
    except Exception as e:
        download_requests_total.labels(status='error').inc()
        logger.error(f"Error getting video info: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.route('/download', methods=['POST'])
def download():
    """Download video endpoint - returns video information"""
    start_time = time.time()
    
    try:
        data = request.get_json()
        if not data:
            download_requests_total.labels(status='error').inc()
            return jsonify({"error": "No JSON data provided"}), 400
        
        video_url = data.get('url')
        quality = data.get('quality', '720p')
        
        if not video_url:
            download_requests_total.labels(status='error').inc()
            return jsonify({"error": "No URL provided"}), 400
        
        logger.info(f"Download request for: {video_url} (quality: {quality})")
        
        quality_map = {
            '1080p': 'bestvideo[height<=1080]+bestaudio/best',
            '720p': 'bestvideo[height<=720]+bestaudio/best',
            '480p': 'bestvideo[height<=480]+bestaudio/best',
            'best': 'best'
        }
        
        format_str = quality_map.get(quality, 'bestvideo[height<=720]+bestaudio/best')
        
        ydl_opts = {
            'format': format_str,
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'ignoreerrors': True,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            filesize = info.get('filesize') or info.get('filesize_approx', 0)
            filesize_mb = filesize / (1024 * 1024) if filesize else 0
            
            if filesize_mb > MAX_DOWNLOAD_SIZE:
                logger.warning(f"File too large: {filesize_mb}MB > {MAX_DOWNLOAD_SIZE}MB")
                download_requests_total.labels(status='error').inc()
                return jsonify({
                    "error": f"File size ({filesize_mb:.2f}MB) exceeds limit ({MAX_DOWNLOAD_SIZE}MB)",
                    "status": "failed"
                }), 400
            
            response_data = {
                "status": "success",
                "message": "Video information retrieved (download simulation)",
                "video": {
                    "title": info.get('title'),
                    "duration": info.get('duration'),
                    "uploader": info.get('uploader'),
                    "view_count": info.get('view_count'),
                    "filesize_mb": round(filesize_mb, 2),
                    "quality": quality,
                    "format": info.get('ext')
                },
                "note": "In production, file would be downloaded to server"
            }
            
            download_requests_total.labels(status='success').inc()
            duration = time.time() - start_time
            download_duration_seconds.observe(duration)
            
            logger.info(f"Successfully processed: {info.get('title')} in {duration:.2f}s")
            return jsonify(response_data)
            
    except Exception as e:
        download_requests_total.labels(status='error').inc()
        logger.error(f"Download error: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "status": 404,
        "available_endpoints": ["/", "/health", "/ready", "/metrics", "/info", "/download"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "status": 500
    }), 500

if __name__ == '__main__':
    logger.info(f"Starting YouTube Downloader API v{APP_VERSION}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Download folder: {DOWNLOAD_FOLDER}")
    logger.info(f"Max download size: {MAX_DOWNLOAD_SIZE}MB")
    
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=DEBUG
    )
