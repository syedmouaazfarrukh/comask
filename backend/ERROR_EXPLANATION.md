# Error Explanation & Fixes

## Errors in Terminal

### 1. ChromaDB Telemetry Warnings (Lines 17-18)
```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
Failed to send telemetry event ClientCreateCollectionEvent: capture() takes 1 positional argument but 3 were given
```

**What it is:**
- ChromaDB tries to send telemetry data
- There's a version mismatch causing the error
- **Not critical** - ChromaDB still works fine

**Fix:** Disable telemetry completely (see below)

### 2. Azure OpenAI Embedding Errors (Lines 25-27)
```
Error code: 404 - DeploymentNotFound
```

**What it is:**
- No embedding deployment configured in Azure OpenAI
- System automatically falls back to keyword search
- **Not critical** - queries still work

**Fix:** Create embedding deployment OR ignore (keyword search works)

### 3. No Documents Found (Line 28)
```
Document search completed, results: 0
```

**What it is:**
- Database is empty - no data collected yet
- **Expected** until you run data collection

**Fix:** Run data collection first

## Fixes Applied

### Fix 1: Disable ChromaDB Telemetry
Updated `app/db/vector_db.py` to properly disable telemetry.

### Fix 2: Suppress Embedding Errors
Updated embedding generation to only log warnings, not errors.

### Fix 3: Better Error Messages
Added clearer messages when no data is available.

