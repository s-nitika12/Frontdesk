"""
Quick verification script to test all components.
Run this after setup to ensure everything is working correctly.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    try:
        from backend.config import Config
        print("✓ Config imported")
        
        from backend.db import engine, SessionLocal
        print("✓ Database imported")
        
        from backend.models import Base, Customer, HelpRequest, KnowledgeBaseEntry
        print("✓ Models imported")
        
        from backend.ai_agent import AIAgent
        print("✓ AI Agent imported")
        
        from backend.services.kb_services import KBService
        print("✓ KB Service imported")
        
        from backend.services.help_request_service import HelpRequestService
        print("✓ Help Request Service imported")
        
        from backend.services.notification_service import NotificationService
        print("✓ Notification Service imported")
        
        from backend.livekit_integration import LiveKitWrapper
        print("✓ LiveKit Integration imported")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_database():
    """Test database connection and table creation."""
    print("\nTesting database...")
    try:
        from backend.db import engine
        from backend.models import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False


def test_services():
    """Test that services can be instantiated."""
    print("\nTesting services...")
    try:
        from backend.services.kb_services import KBService
        from backend.services.help_request_service import HelpRequestService
        from backend.services.notification_service import NotificationService
        from backend.ai_agent import AIAgent
        
        kb = KBService()
        print("✓ KB Service initialized")
        
        help_svc = HelpRequestService()
        print("✓ Help Request Service initialized")
        
        notifier = NotificationService()
        print("✓ Notification Service initialized")
        
        agent = AIAgent()
        print("✓ AI Agent initialized")
        
        return True
    except Exception as e:
        print(f"✗ Service test failed: {e}")
        return False


def test_livekit():
    """Test LiveKit integration (optional)."""
    print("\nTesting LiveKit integration...")
    try:
        from backend.livekit_integration import LiveKitWrapper
        
        lk = LiveKitWrapper()
        status = lk.placeholder()
        
        if status.get('sdk_available'):
            print("✓ LiveKit SDK is available")
        else:
            print("⚠ LiveKit SDK not installed (optional)")
        
        if status.get('configured'):
            print("✓ LiveKit is configured")
        else:
            print("⚠ LiveKit not configured (optional)")
        
        return True
    except Exception as e:
        print(f"✗ LiveKit test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from backend.config import Config
        
        print(f"  DB_URL: {Config.DB_URL}")
        print(f"  FLASK_PORT: {Config.FLASK_PORT}")
        print(f"  KB_FUZZY_THRESHOLD: {Config.KB_FUZZY_THRESHOLD}")
        print(f"  SUPERVISOR_TTL_SECONDS: {Config.SUPERVISOR_TTL_SECONDS}")
        
        livekit_configured = bool(Config.LIVEKIT_API_KEY and Config.LIVEKIT_API_SECRET)
        if livekit_configured:
            print("  LiveKit: ✓ Configured")
        else:
            print("  LiveKit: ⚠ Not configured (optional)")
        
        print("✓ Configuration loaded")
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_flask_app():
    """Test that Flask app can be created."""
    print("\nTesting Flask app...")
    try:
        from backend.app import app
        
        # Test client
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            if response.status_code == 200:
                print("✓ Health endpoint working")
                data = response.get_json()
                print(f"  Status: {data.get('status')}")
            else:
                print(f"⚠ Health endpoint returned {response.status_code}")
        
        return True
    except Exception as e:
        print(f"✗ Flask app test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Voice AI Assistant - System Verification")
    print("=" * 60)
    print()
    
    tests = [
        ("Imports", test_imports),
        ("Database", test_database),
        ("Services", test_services),
        ("Configuration", test_configuration),
        ("LiveKit", test_livekit),
        ("Flask App", test_flask_app),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} test crashed: {e}")
            results.append((name, False))
        print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name:20s} {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to use.")
        print("\nNext steps:")
        print("1. Run backend: python -m flask run --port=8000")
        print("2. Run UI: streamlit run ui/supervisor_app.py")
        print("3. Or use: .\\setup_and_run.ps1")
        return 0
    else:
        print("\n⚠ Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
