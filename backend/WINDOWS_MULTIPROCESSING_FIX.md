# Windows Multiprocessing Fix

## Problem

Playwright's sync API uses asyncio internally, which conflicts with Windows event loop when run in threads:
```
NotImplementedError
File "...asyncio\base_events.py", line 502, in _make_subprocess_transport
    raise NotImplementedError
```

## Solution

✅ **Use ProcessPoolExecutor instead of ThreadPoolExecutor**

- Processes have their own event loop (no conflict)
- Module-level function for pickling
- Windows spawn method for compatibility

## What Changed

1. **Module-level function** (`_scrape_sync_standalone`)
   - Can be pickled for multiprocessing
   - Contains all scraping logic
   - Returns dicts (not objects) for pickling

2. **ProcessPoolExecutor**
   - Replaces ThreadPoolExecutor
   - Each process has fresh event loop
   - Windows spawn method set explicitly

3. **Document conversion**
   - Dicts converted to ScrapedDocument after process returns
   - Avoids pickling complex objects

## Testing

Try clicking "Collect Data" again - should work now!

If you still see errors, the logs will show exactly where it fails.

