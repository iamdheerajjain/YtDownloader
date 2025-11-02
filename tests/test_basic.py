import sys
import os

def test_import_main():
    """Test that main module can be imported successfully"""
    # Add the app directory to the Python path
    app_path = os.path.join(os.path.dirname(__file__), '..', 'app')
    sys.path.insert(0, app_path)
    
    # This should work now that we've added the app directory to the path
    import main
    assert main is not None
