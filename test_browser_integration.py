#!/usr/bin/env python3
"""
Integration test to verify AsyncCamoufox browser interaction works correctly.
This test verifies that the context manager is properly used.
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from camoufox.async_api import AsyncCamoufox

async def test_asynccamoufox_context_manager():
    """Test that AsyncCamoufox context manager works as expected"""
    print("🔍 Testing AsyncCamoufox context manager...")
    
    try:
        async with AsyncCamoufox(headless=True) as browser:
            print(f"✅ Browser type: {type(browser).__name__}")
            print(f"✅ Browser connected: {browser.is_connected()}")
            
            # Test creating a page
            page = await browser.new_page()
            print(f"✅ Page created: {type(page).__name__}")
            
            # Test navigating to a simple page
            await page.goto("about:blank", timeout=5000)
            print("✅ Page navigation works")
            
            # Close the page
            await page.close()
            print("✅ Page closed successfully")
            
        print("✅ Browser context exited cleanly")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_recaptcha_bypass_browser_usage():
    """Test that RecaptchaBypass uses AsyncCamoufox correctly"""
    print("\n🔍 Testing RecaptchaBypass browser usage...")
    
    try:
        from recaptcha_bypass import RecaptchaBypass
        
        bypass = RecaptchaBypass()
        
        # Create a valid-looking anchor URL (though it won't work without a real site)
        # We'll let it fail gracefully but ensure no AttributeError
        test_url = "https://www.google.com/recaptcha/enterprise/anchor?k=6LdyC2cqAAAAAG72L8LGRFqwjhTf6ij2IJ8wXmTJ&co=aHR0cHM6Ly9sbWFyZW5hLmFpOjQ0Mw..&v=1mRJ-DxZiZ-kpTrY_I9tgdHW&size=invisible"
        
        # This should fail (timeout or network error), but shouldn't have AttributeError
        result = await bypass.extract_token(test_url, max_retries=1)
        
        # We expect None because the URL is not actually serving a reCAPTCHA
        if result is None:
            print("✅ RecaptchaBypass handled browser interaction correctly (no AttributeError)")
            return True
        else:
            print(f"⚠️  Unexpected token extracted: {result[:20] if result else None}...")
            return True  # Still a success - means it worked!
            
    except AttributeError as e:
        if "new_page" in str(e) or "is_connected" in str(e):
            print(f"❌ AttributeError detected: {e}")
            return False
        else:
            print(f"⚠️  Different AttributeError: {e}")
            return False
    except Exception as e:
        error_str = str(e)
        if "AttributeError" in error_str and ("new_page" in error_str or "is_connected" in error_str):
            print(f"❌ AttributeError in stack trace: {e}")
            return False
        else:
            print(f"✅ Expected error (no AttributeError): {type(e).__name__}")
            return True

async def main():
    """Run integration tests"""
    print("=" * 60)
    print("AsyncCamoufox Browser Integration Tests")
    print("=" * 60)
    
    test1 = await test_asynccamoufox_context_manager()
    test2 = await test_recaptcha_bypass_browser_usage()
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if test1 and test2:
        print("🎉 All integration tests passed!")
        return 0
    else:
        print("⚠️  Some integration tests failed")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
