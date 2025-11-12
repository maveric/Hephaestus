#!/usr/bin/env python3
"""
Integration test to verify environment variable configuration for remote access.
Tests both backend and frontend configuration loading.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_backend_defaults():
    """Test backend configuration with default values."""
    print("Testing backend defaults...")
    from src.core.simple_config import get_config
    
    config = get_config()
    
    assert config.host_ip == 'localhost', f"Expected host_ip='localhost', got '{config.host_ip}'"
    assert config.mcp_host == '0.0.0.0', f"Expected mcp_host='0.0.0.0', got '{config.mcp_host}'"
    assert config.mcp_port == 8000, f"Expected mcp_port=8000, got {config.mcp_port}"
    assert config.cors_allowed_origins == ['*'], f"Expected cors_allowed_origins=['*'], got {config.cors_allowed_origins}"
    
    print("✅ Backend defaults test passed")


def test_backend_custom_env():
    """Test backend configuration with custom environment variables."""
    print("\nTesting backend with custom environment variables...")
    
    # Set custom environment variables
    os.environ['HOST_IP'] = '192.168.1.100'
    os.environ['CORS_ALLOWED_ORIGINS'] = 'http://192.168.1.100:5173,http://localhost:5173'
    
    # Need to reload the module to pick up new environment variables
    import importlib
    import src.core.simple_config
    importlib.reload(src.core.simple_config)
    
    from src.core.simple_config import get_config
    config = get_config()
    
    assert config.host_ip == '192.168.1.100', f"Expected host_ip='192.168.1.100', got '{config.host_ip}'"
    assert len(config.cors_allowed_origins) == 2, f"Expected 2 CORS origins, got {len(config.cors_allowed_origins)}"
    assert 'http://192.168.1.100:5173' in config.cors_allowed_origins
    assert 'http://localhost:5173' in config.cors_allowed_origins
    
    print("✅ Backend custom environment test passed")
    
    # Clean up
    del os.environ['HOST_IP']
    del os.environ['CORS_ALLOWED_ORIGINS']


def test_cors_wildcard():
    """Test CORS configuration with wildcard."""
    print("\nTesting CORS wildcard configuration...")
    
    os.environ['CORS_ALLOWED_ORIGINS'] = '*'
    
    import importlib
    import src.core.simple_config
    importlib.reload(src.core.simple_config)
    
    from src.core.simple_config import get_config
    config = get_config()
    
    assert config.cors_allowed_origins == ['*'], f"Expected cors_allowed_origins=['*'], got {config.cors_allowed_origins}"
    
    print("✅ CORS wildcard test passed")
    
    # Clean up
    del os.environ['CORS_ALLOWED_ORIGINS']


def test_env_example_files():
    """Verify .env.example files exist with required variables."""
    print("\nTesting .env.example files...")
    
    # Check backend .env.example
    backend_env_example = Path(__file__).parent.parent / '.env.example'
    assert backend_env_example.exists(), "Backend .env.example not found"
    
    backend_content = backend_env_example.read_text()
    assert 'HOST_IP' in backend_content, "HOST_IP not in backend .env.example"
    assert 'CORS_ALLOWED_ORIGINS' in backend_content, "CORS_ALLOWED_ORIGINS not in backend .env.example"
    
    # Check frontend .env.example
    frontend_env_example = Path(__file__).parent.parent / 'frontend' / '.env.example'
    assert frontend_env_example.exists(), "Frontend .env.example not found"
    
    frontend_content = frontend_env_example.read_text()
    assert 'VITE_API_HOST' in frontend_content, "VITE_API_HOST not in frontend .env.example"
    assert 'VITE_API_PORT' in frontend_content, "VITE_API_PORT not in frontend .env.example"
    assert 'VITE_API_PROTOCOL' in frontend_content, "VITE_API_PROTOCOL not in frontend .env.example"
    
    print("✅ .env.example files test passed")


def test_documentation():
    """Verify documentation file exists."""
    print("\nTesting documentation...")
    
    doc_path = Path(__file__).parent.parent / 'REMOTE_ACCESS_SETUP.md'
    assert doc_path.exists(), "REMOTE_ACCESS_SETUP.md not found"
    
    doc_content = doc_path.read_text()
    assert 'HOST_IP' in doc_content, "HOST_IP not documented"
    assert 'CORS_ALLOWED_ORIGINS' in doc_content, "CORS_ALLOWED_ORIGINS not documented"
    assert 'VITE_API_HOST' in doc_content, "VITE_API_HOST not documented"
    
    print("✅ Documentation test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Remote Access Configuration Integration Tests")
    print("=" * 60)
    
    try:
        test_backend_defaults()
        test_backend_custom_env()
        test_cors_wildcard()
        test_env_example_files()
        test_documentation()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
