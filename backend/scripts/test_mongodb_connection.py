"""Test MongoDB/Cosmos DB connection."""

import asyncio
import sys
from pathlib import Path
from urllib.parse import quote_plus, urlparse, urlunparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import structlog

logger = structlog.get_logger()


async def test_connection():
    """Test MongoDB connection with different URL encodings."""
    print("Testing MongoDB Connection...")
    print(f"Database: {settings.database_name}")
    print(f"Connection String: {settings.database_url[:50]}...")
    print()
    
    # Test 1: Original connection string
    print("Test 1: Original connection string")
    try:
        client = AsyncIOMotorClient(
            settings.database_url,
            serverSelectionTimeoutMS=10000
        )
        await client.admin.command('ping')
        print("✓ SUCCESS with original connection string!")
        client.close()
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print()
    
    # Test 2: URL encode the password
    print("Test 2: URL-encoded password")
    try:
        parsed = urlparse(settings.database_url)
        # Extract username and password
        if '@' in parsed.netloc:
            auth, host = parsed.netloc.split('@')
            if ':' in auth:
                username, password = auth.split(':', 1)
                # URL encode password
                encoded_password = quote_plus(password)
                # Reconstruct
                new_netloc = f"{username}:{encoded_password}@{host}"
                new_url = urlunparse((
                    parsed.scheme,
                    new_netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))
                
                client = AsyncIOMotorClient(
                    new_url,
                    serverSelectionTimeoutMS=10000
                )
                await client.admin.command('ping')
                print("✓ SUCCESS with URL-encoded password!")
                print(f"Use this connection string in .env:")
                print(f"DATABASE_URL={new_url}")
                client.close()
                return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        print()
    
    # Test 3: Manual connection string construction
    print("Test 3: Manual connection string")
    print("Please check:")
    print("1. The connection string in Azure Portal")
    print("2. That the key hasn't been regenerated")
    print("3. That IP whitelist allows your connection")
    print()
    
    return False


if __name__ == "__main__":
    result = asyncio.run(test_connection())
    if not result:
        print("\n⚠️  Connection failed. Check MONGODB_CONNECTION_FIX.md for solutions.")
        sys.exit(1)
    else:
        print("\n✓ Connection successful!")

