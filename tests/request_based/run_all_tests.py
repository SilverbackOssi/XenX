import sys
import os
import time

# Add the current directory to the path so we can import the test modules
sys.path.append(os.path.dirname(__file__))

def run_all_tests():
    """Run all the request-based tests"""
    print("===== Running All Request-Based Tests =====")
    
    # Import test modules
    from test_profile_update import run_profile_tests
    from test_enterprise_management import run_enterprise_tests
    from test_enterprise_branding import run_branding_tests
    
    # Run profile tests
    print("\n\n===== PROFILE TESTS =====")
    run_profile_tests()
    time.sleep(1)  # Give the server a moment to process
    
    # Run enterprise management tests
    print("\n\n===== ENTERPRISE MANAGEMENT TESTS =====")
    run_enterprise_tests()
    time.sleep(1)  # Give the server a moment to process
    
    # Run enterprise branding tests
    print("\n\n===== ENTERPRISE BRANDING TESTS =====")
    run_branding_tests()
    
    print("\n\n===== All Tests Completed =====")

if __name__ == "__main__":
    # Check if server is running before starting tests
    import requests
    try:
        requests.get("http://localhost:8000/health", timeout=5)
        print("Server is running. Starting tests...")
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("ERROR: Server is not running at http://localhost:8000.")
        print("Please start the server first with: uvicorn main:app --reload")
        sys.exit(1)
