"""Generate embeddings for existing documents using Voyage AI."""

import asyncio
import sys
sys.path.insert(0, '/app')

from app.db.database import init_db, get_db_session
from app.db.models import Document, DocumentChunk
from app.llm.embeddings import get_embeddings, embeddings_available
from sqlalchemy import select
import structlog

logger = structlog.get_logger()


async def generate_embeddings():
    """Generate embeddings for all document chunks that don't have them."""
    print("Initializing database...")
    await init_db()

    # Check if embeddings are available
    embeddings = get_embeddings()
    if not embeddings:
        print("ERROR: Voyage AI embeddings not configured. Please set VOYAGE_API_KEY.")
        return

    print(f"Using Voyage AI model: {embeddings.model}")

    async with get_db_session() as session:
        # Get all chunks without embeddings
        stmt = select(DocumentChunk).where(DocumentChunk.embedding.is_(None))
        result = await session.execute(stmt)
        chunks = result.scalars().all()

        print(f"Found {len(chunks)} chunks without embeddings")

        if not chunks:
            print("All chunks already have embeddings!")
            return

        # Process chunks in batches
        batch_size = 10
        total_generated = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            print(f"\nProcessing batch {i // batch_size + 1}/{(len(chunks) + batch_size - 1) // batch_size}...")

            texts = [chunk.content[:8000] for chunk in batch]  # Limit content length

            try:
                # Generate embeddings for the batch
                vectors = await embeddings.generate_batch(texts)

                # Update chunks with embeddings
                for chunk, vector in zip(batch, vectors):
                    chunk.embedding = vector
                    total_generated += 1
                    print(f"  Generated embedding for chunk {chunk.id} ({len(vector)} dimensions)")

                await session.commit()

            except Exception as e:
                print(f"  ERROR generating embeddings for batch: {e}")
                continue

        print(f"\n✓ Generated embeddings for {total_generated} chunks")


if __name__ == "__main__":
    asyncio.run(generate_embeddings())
