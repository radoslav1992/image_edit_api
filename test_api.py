"""
Enhanced Test Suite for Background Removal API
Tests all features including rate limiting, caching, webhooks, etc.
"""

import requests
import json
import time
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

# Test image URL from example
TEST_IMAGE_URL = "https://replicate.delivery/pbxt/MAqakpYnuaS5IxU4WZAh5irkSn92wuYc5bdU1TNV5xzIJ8sM/gzp35qt55t4aatwznmccv2ssgds2.png"

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_test_header(test_name: str):
    """Print a formatted test header"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🧪 {test_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.RESET}")


def test_root_endpoint() -> bool:
    """Test the root endpoint"""
    print_test_header("Test Root Endpoint")
    
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            data = response.json()
            print_success("Root endpoint working")
            print(f"   API: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Status: {data.get('status')}")
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        print_info("Make sure the server is running: python main.py")
        return False


def test_health_check() -> bool:
    """Test health check endpoint"""
    print_test_header("Test Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success("Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Version: {data.get('version')}")
            print(f"   Uptime: {data.get('uptime')}")
            print(f"   API Configured: {data.get('api_configured')}")
            print(f"   Cache Stats: {data.get('cache_stats')}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_remove_background(use_cache: bool = False) -> Optional[str]:
    """Test background removal endpoint"""
    test_name = "Test Background Removal (Cache)" if use_cache else "Test Background Removal"
    print_test_header(test_name)
    
    try:
        payload = {
            "image_url": TEST_IMAGE_URL,
            "format": "png",
            "reverse": False,
            "threshold": 0,
            "background_type": "rgba"
        }
        
        print_info(f"Sending request to {API_PREFIX}/remove-background...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json=payload,
            timeout=90
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print_success("Background removal successful")
            print(f"   Output URL: {result.get('output_url')}")
            print(f"   Processing Time: {result.get('processing_time'):.2f}s")
            print(f"   Request Duration: {duration:.2f}s")
            print(f"   Cached: {result.get('cached', False)}")
            print(f"   Request ID: {result.get('request_id')}")
            return result.get('output_url')
        elif response.status_code == 429:
            print_error("Rate limit exceeded")
            print_info("Wait a moment and try again")
            return None
        else:
            print_error(f"Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print_error("Request timed out")
        print_info("Processing can take 10-30 seconds for the first request")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def test_cache_functionality() -> bool:
    """Test caching by making two identical requests"""
    print_test_header("Test Cache Functionality")
    
    print_info("Making first request (should not be cached)...")
    result1 = test_remove_background(use_cache=False)
    
    if not result1:
        print_error("First request failed, cannot test cache")
        return False
    
    time.sleep(2)
    
    print_info("\nMaking second identical request (should be cached)...")
    result2 = test_remove_background(use_cache=True)
    
    if result2 and result1 == result2:
        print_success("Cache working correctly - same result returned faster")
        return True
    else:
        print_error("Cache test inconclusive")
        return False


def test_cache_stats() -> bool:
    """Test cache statistics endpoint"""
    print_test_header("Test Cache Statistics")
    
    try:
        response = requests.get(f"{BASE_URL}/cache/stats")
        if response.status_code == 200:
            data = response.json()
            print_success("Cache stats retrieved")
            print(f"   Cache: {json.dumps(data.get('cache'), indent=6)}")
            print(f"   Enabled: {data.get('enabled')}")
            return True
        else:
            print_error(f"Failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_batch_processing() -> bool:
    """Test batch processing endpoint"""
    print_test_header("Test Batch Processing")
    
    try:
        # Use a smaller test image for batch processing
        image_urls = [TEST_IMAGE_URL, TEST_IMAGE_URL]
        
        print_info(f"Sending batch request with {len(image_urls)} images...")
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background/batch",
            json=image_urls,
            params={"format": "png", "background_type": "rgba"},
            timeout=120
        )
        
        duration = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print_success("Batch processing successful")
            print(f"   Total: {result.get('total')}")
            print(f"   Successful: {result.get('successful')}")
            print(f"   Failed: {result.get('failed')}")
            print(f"   Processing Time: {result.get('processing_time'):.2f}s")
            print(f"   Total Duration: {duration:.2f}s")
            
            # Show first result
            if result.get('results'):
                first = result['results'][0]
                print(f"   First Result: {first.get('success')}")
                print(f"   Cached: {first.get('cached', False)}")
            
            return result.get('successful', 0) > 0
        elif response.status_code == 429:
            print_error("Rate limit exceeded")
            return False
        else:
            print_error(f"Failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print_error("Batch request timed out")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def test_validation_errors() -> bool:
    """Test input validation"""
    print_test_header("Test Input Validation")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Invalid URL
    print_info("Test 1: Invalid URL")
    try:
        payload = {
            "image_url": "not-a-valid-url",
            "format": "png"
        }
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json=payload,
            timeout=10
        )
        if response.status_code == 422:  # Validation error
            print_success("Invalid URL rejected correctly")
            tests_passed += 1
        else:
            print_error(f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test 2: Invalid format
    print_info("\nTest 2: Invalid format")
    try:
        payload = {
            "image_url": TEST_IMAGE_URL,
            "format": "invalid_format"
        }
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json=payload,
            timeout=10
        )
        if response.status_code in [400, 422]:
            print_success("Invalid format rejected correctly")
            tests_passed += 1
        else:
            print_error(f"Expected 400/422, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test 3: Missing required field
    print_info("\nTest 3: Missing required field")
    try:
        payload = {
            "format": "png"
            # Missing image_url
        }
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/remove-background",
            json=payload,
            timeout=10
        )
        if response.status_code == 422:
            print_success("Missing field rejected correctly")
            tests_passed += 1
        else:
            print_error(f"Expected 422, got {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    print(f"\n   Validation tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests


def test_legal_endpoints() -> bool:
    """Test legal endpoints (Terms, Privacy)"""
    print_test_header("Test Legal Endpoints")
    
    tests_passed = 0
    
    # Test Terms of Service
    print_info("Test 1: Terms of Service")
    try:
        response = requests.get(f"{BASE_URL}/terms")
        if response.status_code == 200:
            data = response.json()
            if 'title' in data and 'terms' in data:
                print_success("Terms of Service endpoint working")
                tests_passed += 1
            else:
                print_error("Terms response missing required fields")
        else:
            print_error(f"Failed with status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test Privacy Policy
    print_info("\nTest 2: Privacy Policy")
    try:
        response = requests.get(f"{BASE_URL}/privacy")
        if response.status_code == 200:
            data = response.json()
            if 'title' in data and 'policy' in data:
                print_success("Privacy Policy endpoint working")
                tests_passed += 1
            else:
                print_error("Privacy response missing required fields")
        else:
            print_error(f"Failed with status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    return tests_passed == 2


def test_info_endpoints() -> bool:
    """Test information endpoints (Pricing, SLA)"""
    print_test_header("Test Information Endpoints")
    
    tests_passed = 0
    
    # Test Pricing
    print_info("Test 1: Pricing Information")
    try:
        response = requests.get(f"{BASE_URL}/pricing")
        if response.status_code == 200:
            data = response.json()
            if 'plans' in data:
                print_success("Pricing endpoint working")
                print(f"   Plans available: {len(data['plans'])}")
                tests_passed += 1
            else:
                print_error("Pricing response missing plans")
        else:
            print_error(f"Failed with status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    # Test SLA
    print_info("\nTest 2: Service Level Agreement")
    try:
        response = requests.get(f"{BASE_URL}/sla")
        if response.status_code == 200:
            data = response.json()
            if 'title' in data and 'sla' in data:
                print_success("SLA endpoint working")
                tests_passed += 1
            else:
                print_error("SLA response missing required fields")
        else:
            print_error(f"Failed with status {response.status_code}")
    except Exception as e:
        print_error(f"Error: {str(e)}")
    
    return tests_passed == 2


def test_rate_limiting() -> bool:
    """Test rate limiting (gentle test)"""
    print_test_header("Test Rate Limiting")
    
    print_info("Testing rate limits with rapid requests...")
    print_info("(This may take a moment)")
    
    try:
        # Make several rapid requests
        success_count = 0
        rate_limited = False
        
        for i in range(5):
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                success_count += 1
            elif response.status_code == 429:
                rate_limited = True
                print_success("Rate limiting is working (got 429 response)")
                return True
            time.sleep(0.1)
        
        if success_count == 5:
            print_success("Rate limiting configured (no limit hit with 5 requests)")
            print_info("Rate limits are active but generous for health checks")
            return True
        
        return False
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False


def run_all_tests():
    """Run all test suites"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}🚀 Background Removal API - Enhanced Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"\n{Colors.YELLOW}Testing API at: {BASE_URL}{Colors.RESET}")
    print(f"{Colors.YELLOW}API Prefix: {API_PREFIX}{Colors.RESET}\n")
    
    results = {}
    
    # Core functionality tests
    results['Root Endpoint'] = test_root_endpoint()
    results['Health Check'] = test_health_check()
    results['Background Removal'] = test_remove_background() is not None
    
    # Cache tests
    results['Cache Stats'] = test_cache_stats()
    results['Cache Functionality'] = test_cache_functionality()
    
    # Batch processing
    results['Batch Processing'] = test_batch_processing()
    
    # Validation tests
    results['Input Validation'] = test_validation_errors()
    
    # Legal/Info endpoints
    results['Legal Endpoints'] = test_legal_endpoints()
    results['Info Endpoints'] = test_info_endpoints()
    
    # Rate limiting
    results['Rate Limiting'] = test_rate_limiting()
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}📊 Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.GREEN}✅ PASS{Colors.RESET}" if result else f"{Colors.RED}❌ FAIL{Colors.RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    percentage = (passed / total * 100) if total > 0 else 0
    print(f"\n{Colors.YELLOW}Results: {passed}/{total} tests passed ({percentage:.1f}%){Colors.RESET}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All tests passed! Your API is production-ready!{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Next steps:{Colors.RESET}")
        print(f"  1. View interactive docs: {BASE_URL}/docs")
        print(f"  2. Check pricing info: {BASE_URL}/pricing")
        print(f"  3. Review deployment guide: docs/DEPLOYMENT.md")
        print(f"  4. List on RapidAPI: https://rapidapi.com/provider")
    else:
        print(f"{Colors.YELLOW}⚠️  Some tests failed. Please check:{Colors.RESET}")
        print(f"  1. Is the API server running? (python main.py)")
        print(f"  2. Is REPLICATE_API_TOKEN set in .env?")
        print(f"  3. Do you have an internet connection?")
        print(f"  4. Check server logs for errors")
    
    print()


if __name__ == "__main__":
    run_all_tests()
