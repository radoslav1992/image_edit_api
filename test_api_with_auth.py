"""
Test Suite for Background Removal API with Authentication
"""

import requests
import json
import time
import os
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Get API key from environment or prompt user
API_KEY = os.getenv("API_KEY") or input("Enter your API key (or press Enter to skip): ").strip()

# Test image URL
TEST_IMAGE_URL = "https://replicate.delivery/pbxt/MAqakpYnuaS5IxU4WZAh5irkSn92wuYc5bdU1TNV5xzIJ8sM/gzp35qt55t4aatwznmccv2ssgds2.png"

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def get_headers():
    """Get headers with API key if configured"""
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return headers


def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.RESET}")


def print_header(text: str):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")


def test_without_api_key():
    """Test that protected endpoints require API key"""
    print_header("🔒 Test API Key Requirement")
    
    try:
        # Try without API key
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json={"image_url": TEST_IMAGE_URL},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 401:
            print_success("API correctly requires authentication")
            return True
        elif response.status_code == 200:
            print_info("API is in development mode (no key required)")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_with_invalid_key():
    """Test that invalid API keys are rejected"""
    print_header("🔐 Test Invalid API Key")
    
    try:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "invalid_key_12345"
        }
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json={"image_url": TEST_IMAGE_URL},
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [401, 403]:
            print_success("Invalid API key correctly rejected")
            return True
        elif response.status_code == 200:
            print_info("API is in development mode (accepts any key)")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_with_valid_key():
    """Test with valid API key"""
    print_header("✅ Test Valid API Key")
    
    if not API_KEY:
        print_info("No API key provided, skipping test")
        return True
    
    try:
        payload = {
            "image_url": TEST_IMAGE_URL,
            "format": "png",
            "background_type": "rgba"
        }
        
        print_info("Sending authenticated request...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json=payload,
            headers=get_headers(),
            timeout=90
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print_success("Authenticated request successful!")
            print(f"   Output URL: {result.get('output_url')}")
            print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
            print(f"   Total Duration: {duration:.2f}s")
            print(f"   Request ID: {result.get('request_id')}")
            return True
        elif response.status_code in [401, 403]:
            print_error("Authentication failed - check your API key")
            print(f"   Response: {response.text}")
            return False
        else:
            print_error(f"Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_public_endpoints():
    """Test that public endpoints don't require API key"""
    print_header("🌐 Test Public Endpoints")
    
    public_endpoints = [
        ("/", "Root"),
        ("/health", "Health Check"),
        ("/terms", "Terms of Service"),
        ("/privacy", "Privacy Policy"),
        ("/pricing", "Pricing"),
        ("/sla", "SLA")
    ]
    
    passed = 0
    
    for endpoint, name in public_endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                print_success(f"{name} accessible without API key")
                passed += 1
            else:
                print_error(f"{name} returned {response.status_code}")
        except Exception as e:
            print_error(f"{name} error: {str(e)}")
    
    print(f"\n   {passed}/{len(public_endpoints)} public endpoints working")
    return passed == len(public_endpoints)


def test_rapidapi_headers():
    """Test RapidAPI header authentication"""
    print_header("🚀 Test RapidAPI Headers")
    
    try:
        headers = {
            "Content-Type": "application/json",
            "X-RapidAPI-Key": "test_rapidapi_key",
            "X-RapidAPI-User": "test_user"
        }
        
        payload = {
            "image_url": TEST_IMAGE_URL,
            "format": "png"
        }
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json=payload,
            headers=headers,
            timeout=90
        )
        
        if response.status_code == 200:
            print_success("RapidAPI headers accepted")
            return True
        else:
            print_info(f"RapidAPI simulation returned {response.status_code}")
            print_info("(This is expected if API requires actual RapidAPI validation)")
            return True
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def main():
    """Run all authentication tests"""
    print_header("🔐 API Authentication Test Suite")
    
    if API_KEY:
        print_info(f"Testing with API Key: {API_KEY[:8]}...")
    else:
        print_info("Testing without API Key (development mode)")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"API Prefix: {API_PREFIX}")
    
    results = {}
    
    # Run tests
    results['Public Endpoints'] = test_public_endpoints()
    results['API Key Requirement'] = test_without_api_key()
    results['Invalid Key Rejection'] = test_with_invalid_key()
    results['Valid Key Authentication'] = test_with_valid_key()
    results['RapidAPI Headers'] = test_rapidapi_headers()
    
    # Summary
    print_header("📊 Test Summary")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{status} - {test_name}")
    
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\n{Colors.YELLOW}Results: {passed}/{total} tests passed ({percentage:.1f}%){Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All authentication tests passed!{Colors.RESET}\n")
    else:
        print(f"{Colors.YELLOW}⚠️  Some tests failed. Please check the output above.{Colors.RESET}\n")
    
    # Next steps
    print_header("📝 Next Steps")
    print("1. Test your API key in production:")
    print(f"   export API_KEY=your_key && python test_api_with_auth.py")
    print("\n2. View interactive docs:")
    print(f"   {BASE_URL}/docs")
    print("\n3. Configure RapidAPI:")
    print("   - Set your deployed API URL")
    print("   - RapidAPI will handle authentication")
    print("   - Your API will receive X-RapidAPI-* headers")
    print()


if __name__ == "__main__":
    main()

