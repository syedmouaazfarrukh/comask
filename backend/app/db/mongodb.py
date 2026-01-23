"""MongoDB/Cosmos DB connection and session management."""

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import structlog

logger = structlog.get_logger()

# Global MongoDB client
_client: AsyncIOMotorClient | None = None
_database = None


async def get_mongodb_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        # URL encode the connection string if needed
        import urllib.parse
        # Parse and reconstruct URL to ensure proper encoding
        parsed = urllib.parse.urlparse(settings.database_url)
        # Reconstruct with proper encoding
        encoded_url = urllib.parse.urlunparse(parsed)
        
        _client = AsyncIOMotorClient(
            encoded_url,
            serverSelectionTimeoutMS=10000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        logger.info("MongoDB client initialized", database=settings.database_name)
    return _client


async def get_mongodb_db():
    """Get MongoDB database instance."""
    global _database
    if _database is None:
        client = await get_mongodb_client()
        _database = client[settings.database_name]
    return _database


async def close_mongodb():
    """Close MongoDB connections."""
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB connections closed")


async def init_mongodb():
    """Initialize MongoDB (test connection)."""
    try:
        client = await get_mongodb_client()
        # Test connection with longer timeout
        await client.admin.command('ping', serverSelectionTimeoutMS=10000)
        logger.info("MongoDB connection successful", database=settings.database_name)
        return True
    except Exception as e:
        error_msg = str(e)
        logger.warning(
            "MongoDB connection failed - continuing without database",
            error=error_msg,
            note="The app will start but database features won't work until connection is fixed"
        )
        # Don't raise - allow app to start without DB for development
        return False

