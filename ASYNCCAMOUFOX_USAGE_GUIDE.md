# AsyncCamoufox Usage Guide

## Quick Reference

AsyncCamoufox is a context manager that wraps Playwright's browser automation with additional fingerprinting and anti-detection features.

### ✅ Correct Usage

```python
from camoufox.async_api import AsyncCamoufox

async def use_browser():
    # Always use as an async context manager
    async with AsyncCamoufox(headless=True) as browser:
        # Now 'browser' is a Playwright Browser object
        page = await browser.new_page()
        
        # Do your automation
        await page.goto("https://example.com")
        content = await page.content()
        
        # Clean up
        await page.close()
    # Browser automatically closed here
```

### ❌ Common Mistakes

```python
# WRONG: Don't instantiate without context manager
browser = AsyncCamoufox(headless=True)
page = await browser.new_page()  # ❌ AttributeError!

# WRONG: Don't try to cache the context manager
self._browser = AsyncCamoufox(headless=True)
# Later...
page = await self._browser.new_page()  # ❌ AttributeError!

# WRONG: Don't call methods outside context
browser = AsyncCamoufox(headless=True)
if browser.is_connected():  # ❌ AttributeError!
    pass
```

## API Reference

### AsyncCamoufox Constructor

```python
AsyncCamoufox(
    headless: bool = False,
    **launch_options
)
```

Returns a context manager that yields a Playwright Browser instance.

### Browser Object Methods

Once inside the context manager, you have access to all Playwright Browser methods:

#### Essential Methods
- `await browser.new_page()` - Create a new page
- `await browser.new_context()` - Create a new browser context
- `browser.is_connected()` - Check if browser is connected
- `await browser.close()` - Close browser (handled automatically by context manager)
- `browser.contexts` - List of active contexts
- `browser.version` - Browser version string

#### Page Methods (after `page = await browser.new_page()`)
- `await page.goto(url)` - Navigate to URL
- `await page.content()` - Get page HTML
- `await page.evaluate(js)` - Execute JavaScript
- `await page.wait_for_selector(selector)` - Wait for element
- `await page.click(selector)` - Click element
- `await page.fill(selector, value)` - Fill input
- `await page.screenshot()` - Take screenshot
- `await page.close()` - Close page

## Usage Patterns

### Single Page Automation

```python
async with AsyncCamoufox(headless=True) as browser:
    page = await browser.new_page()
    try:
        await page.goto("https://example.com")
        # Do automation
        result = await page.evaluate("() => document.title")
        return result
    finally:
        await page.close()
```

### Multiple Pages

```python
async with AsyncCamoufox(headless=True) as browser:
    # Create multiple pages
    page1 = await browser.new_page()
    page2 = await browser.new_page()
    
    try:
        await page1.goto("https://example1.com")
        await page2.goto("https://example2.com")
        
        # Work with both pages
        # ...
        
    finally:
        await page1.close()
        await page2.close()
```

### Error Handling

```python
async with AsyncCamoufox(headless=True) as browser:
    page = None
    try:
        page = await browser.new_page()
        await page.goto("https://example.com", timeout=30000)
        # Do automation
    except TimeoutError:
        print("Navigation timed out")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if page:
            try:
                await page.close()
            except:
                pass
```

### Reusing Browser Across Multiple Operations

If you need to perform multiple operations, keep them all within the same context:

```python
async with AsyncCamoufox(headless=True) as browser:
    # Operation 1
    page1 = await browser.new_page()
    await page1.goto("https://example1.com")
    result1 = await extract_data(page1)
    await page1.close()
    
    # Operation 2
    page2 = await browser.new_page()
    await page2.goto("https://example2.com")
    result2 = await extract_data(page2)
    await page2.close()
    
    return result1, result2
```

## Configuration Options

### Headless Mode

```python
# Headless (no GUI)
async with AsyncCamoufox(headless=True) as browser:
    pass

# Headed (with GUI - useful for debugging)
async with AsyncCamoufox(headless=False) as browser:
    pass
```

### Custom Launch Options

```python
async with AsyncCamoufox(
    headless=True,
    args=['--no-sandbox', '--disable-gpu']
) as browser:
    pass
```

## Best Practices

1. **Always use context manager** - Never instantiate AsyncCamoufox without `async with`
2. **Close pages explicitly** - While browser auto-closes, pages should be closed explicitly
3. **Handle errors gracefully** - Browser operations can fail; use try/except
4. **Set timeouts** - Use timeout parameters to avoid hanging
5. **Don't cache browser instances** - Create new context for each major operation
6. **Initialize variables** - Set `page = None` before try block to avoid unbound variable errors

## Troubleshooting

### AttributeError: 'AsyncCamoufox' object has no attribute 'new_page'

**Problem:** Trying to call browser methods on AsyncCamoufox directly.

**Solution:** Use `async with` to get the browser object:
```python
async with AsyncCamoufox(headless=True) as browser:
    page = await browser.new_page()  # ✅ Correct
```

### AttributeError: 'AsyncCamoufox' object has no attribute 'is_connected'

**Problem:** Same as above - calling methods on context manager instead of browser.

**Solution:** Same as above - use the browser object from context manager.

### UnboundLocalError: cannot access local variable 'page'

**Problem:** `page` variable used in finally block but may not have been assigned.

**Solution:** Initialize `page = None` before try block:
```python
page = None
try:
    async with AsyncCamoufox(headless=True) as browser:
        page = await browser.new_page()
        # ...
finally:
    if page:
        await page.close()
```

## See Also

- [Playwright Python Documentation](https://playwright.dev/python/)
- [Camoufox GitHub Repository](https://github.com/daijro/camoufox)
