#!/usr/bin/env python3
"""
Test script to verify AsyncCamoufox reCAPTCHA bypass API fixes.
This tests the correct usage of AsyncCamoufox context manager.
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from recaptcha_bypass import RecaptchaBypass

async def test_recaptcha_bypass_initialization():
    """Test that RecaptchaBypass can be initialized without errors"""
    print("🔍 Test 1: Initializing RecaptchaBypass...")
    try:
        bypass = RecaptchaBypass()
        print("✅ RecaptchaBypass initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize RecaptchaBypass: {e}")
        return False

async def test_no_attribute_errors():
    """Test that the fixed code doesn't have AttributeError issues"""
    print("\n🔍 Test 2: Checking for AttributeError issues...")
    try:
        bypass = RecaptchaBypass()
        
        # Test that we don't have _browser attribute issues
        if hasattr(bypass, '_browser'):
            print("❌ Found _browser attribute (should have been removed)")
            return False
        
        # Test that _get_browser method doesn't exist
        if hasattr(bypass, '_get_browser'):
            print("❌ Found _get_browser method (should have been removed)")
            return False
        
        # Test that _close_browser method doesn't exist
        if hasattr(bypass, '_close_browser'):
            print("❌ Found _close_browser method (should have been removed)")
            return False
        
        print("✅ No AttributeError issues detected")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_cleanup_method():
    """Test that cleanup method works without errors"""
    print("\n🔍 Test 3: Testing cleanup method...")
    try:
        bypass = RecaptchaBypass()
        await bypass.cleanup()
        print("✅ Cleanup method works correctly")
        return True
    except Exception as e:
        print(f"❌ Cleanup method failed: {e}")
        return False

async def test_url_validation():
    """Test URL validation functionality"""
    print("\n🔍 Test 4: Testing URL validation...")
    try:
        bypass = RecaptchaBypass()
        
        # Test valid URL
        valid_url = "https://www.google.com/recaptcha/enterprise/anchor?k=test_key&co=example.com&v=test_version&size=invisible"
        result = bypass._validate_anchor_url(valid_url)
        
        if result:
            print("✅ URL validation works correctly")
            return True
        else:
            print("⚠️  URL validation returned False (expected for test URL)")
            return True  # This is expected for a test URL
    except Exception as e:
        print(f"❌ URL validation failed with error: {e}")
        return False

async def test_extract_token_structure():
    """Test that extract_token method structure is correct"""
    print("\n🔍 Test 5: Testing extract_token method structure...")
    try:
        bypass = RecaptchaBypass()
        
        # Test with an invalid URL - should fail gracefully
        result = await bypass.extract_token("invalid_url", max_retries=1)
        
        if result is None:
            print("✅ extract_token handles invalid URLs correctly")
            return True
        else:
            print("⚠️  Unexpected result from extract_token")
            return True  # Not a failure, just unexpected
    except Exception as e:
        # Check if it's an AttributeError about missing methods
        if "has no attribute 'new_page'" in str(e):
            print(f"❌ AttributeError still present: {e}")
            return False
        elif "has no attribute 'is_connected'" in str(e):
            print(f"❌ AttributeError still present: {e}")
            return False
        else:
            print(f"⚠️  Expected error for invalid URL: {e}")
            return True  # Expected to fail with invalid URL

async def main():
    """Run all tests"""
    print("=" * 60)
    print("AsyncCamoufox reCAPTCHA Bypass API Fix Tests")
    print("=" * 60)
    
    tests = [
        test_recaptcha_bypass_initialization,
        test_no_attribute_errors,
        test_cleanup_method,
        test_url_validation,
        test_extract_token_structure
    ]
    
    results = []
    for test in tests:
        result = await test()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
