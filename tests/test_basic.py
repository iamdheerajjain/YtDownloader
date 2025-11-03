import sys
import os
from unittest.mock import patch, MagicMock

app_path = os.path.join(os.path.dirname(__file__), '..', 'app')
sys.path.insert(0, app_path)

def test_import_main():
    """Test that main module can be imported successfully"""
    import main
    assert main is not None

def test_home_endpoint():
    """Test the home endpoint"""
    import main
    main.app.config['TESTING'] = True
    client = main.app.test_client()
    
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert 'app' in data
    assert data['app'] == 'YouTube Downloader API'

def test_health_endpoint():
    """Test the health endpoint"""
    import main
    main.app.config['TESTING'] = True
    client = main.app.test_client()
    
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'UP'

def test_ready_endpoint():
    """Test the readiness endpoint"""
    import main
    main.app.config['TESTING'] = True
    client = main.app.test_client()
    
    response = client.get('/ready')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data

@patch('main.YoutubeDL')
def test_info_endpoint(mock_ytdl):
    """Test the video info endpoint"""
    import main

    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {
        'title': 'Test Video',
        'duration': 300,
        'uploader': 'Test Uploader',
        'view_count': 1000,
        'upload_date': '20230101',
        'description': 'Test description',
        'thumbnail': 'http://example.com/thumb.jpg',
        'formats': [{'format_id': '1'}, {'format_id': '2'}]
    }
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    
    main.app.config['TESTING'] = True
    client = main.app.test_client()

    response = client.post('/info', json={'url': 'https://youtube.com/watch?v=test'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['video']['title'] == 'Test Video'

    response = client.post('/info', json={})
    assert response.status_code == 400

@patch('main.YoutubeDL')
def test_download_endpoint(mock_ytdl):
    """Test the download endpoint"""
    import main

    mock_instance = MagicMock()
    mock_instance.extract_info.return_value = {
        'title': 'Test Video',
        'duration': 300,
        'uploader': 'Test Uploader',
        'view_count': 1000,
        'filesize': 5000000,  # ~5MB
        'ext': 'mp4'
    }
    mock_ytdl.return_value.__enter__.return_value = mock_instance
    
    main.app.config['TESTING'] = True
    client = main.app.test_client()

    response = client.post('/download', json={'url': 'https://youtube.com/watch?v=test'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['video']['title'] == 'Test Video'

    response = client.post('/download', json={})
    assert response.status_code == 400