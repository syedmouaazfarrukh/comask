"""Collect data from various regulatory sources."""

import asyncio
import sys
sys.path.insert(0, '/app')

import httpx
from app.db.database import init_db, get_db_session
from app.db.models import Document, DocumentChunk, AuthorityLevel, JurisdictionType, DocumentType
from app.llm.embeddings import get_embeddings
from app.scrapers.ecfr import ECFRClient
from datetime import date
import uuid
import structlog
from sqlalchemy import select

logger = structlog.get_logger()


# Key FERC parts for energy regulation
FERC_KEY_PARTS = [
    # Part 35: Filing of Rate Schedules and Tariffs
    (35, "Filing of Rate Schedules and Tariffs"),
    # Part 37: Open Access Same-Time Information Systems
    (37, "Open Access Same-Time Information Systems"),
    # Part 38: Standards for Public Utility Business Operations
    (38, "Standards for Public Utility Business Operations"),
    # Part 284: Certain Sales and Transportation of Natural Gas
    (284, "Certain Sales and Transportation of Natural Gas"),
    # Part 292: Regulations Under Sections 201 and 210 of PURPA
    (292, "Regulations Under Sections 201 and 210 of PURPA"),
]

# Key EPA parts for energy-related environmental regulations
EPA_KEY_PARTS = [
    # Part 60: Standards of Performance for New Stationary Sources
    (60, "Standards of Performance for New Stationary Sources"),
    # Part 63: National Emission Standards for Hazardous Air Pollutants
    (63, "National Emission Standards for Hazardous Air Pollutants"),
]


async def collect_ecfr_data():
    """Collect key federal regulations from eCFR."""
    print("\n=== Collecting Federal Regulations from eCFR ===\n")

    await init_db()
    client = ECFRClient()
    embeddings = get_embeddings()

    documents_added = 0

    try:
        async with get_db_session() as session:
            # Collect FERC regulations (Title 18)
            print("Fetching FERC regulations (Title 18)...")
            for part_num, part_name in FERC_KEY_PARTS:
                print(f"  Fetching Part {part_num}: {part_name}...")

                try:
                    content = await client.get_full_text(18, part_num)

                    if content and len(content) > 500:
                        # Clean XML content
                        import re
                        text = re.sub(r'<[^>]+>', ' ', content)
                        text = re.sub(r'\s+', ' ', text).strip()

                        # Truncate if too long (keep first 50000 chars)
                        if len(text) > 50000:
                            text = text[:50000] + "\n\n[Content truncated for storage]"

                        # Check if document already exists
                        from sqlalchemy import select
                        checksum = f"ecfr-18-{part_num}"
                        result = await session.execute(
                            select(Document).where(Document.checksum == checksum)
                        )
                        existing = result.scalar_one_or_none()

                        if existing:
                            print(f"    Already exists, skipping...")
                            continue

                        # Create document
                        doc = Document(
                            id=uuid.uuid4(),
                            title=f"18 CFR Part {part_num} - {part_name}",
                            content=text,
                            source_url=f"https://www.ecfr.gov/current/title-18/part-{part_num}",
                            document_type=DocumentType.REGULATION,
                            authority_level=AuthorityLevel.FEDERAL,
                            jurisdiction_type=JurisdictionType.FEDERAL,
                            source_name="eCFR - FERC",
                            citation=f"18 CFR Part {part_num}",
                            published_date=date.today(),
                            checksum=checksum,
                        )
                        session.add(doc)
                        await session.flush()

                        # Create chunks (simple chunking)
                        chunks = chunk_text(text, chunk_size=2000, overlap=200)
                        for i, chunk_text_content in enumerate(chunks):
                            # Generate embedding if available
                            embedding = None
                            if embeddings:
                                try:
                                    embedding = await embeddings.generate(chunk_text_content[:8000])
                                except Exception as e:
                                    print(f"    Warning: Could not generate embedding: {e}")

                            chunk = DocumentChunk(
                                id=uuid.uuid4(),
                                document_id=doc.id,
                                content=chunk_text_content,
                                chunk_index=i,
                                embedding=embedding,
                            )
                            session.add(chunk)

                        await session.commit()
                        documents_added += 1
                        print(f"    Added with {len(chunks)} chunks")

                except Exception as e:
                    print(f"    Error: {e}")
                    continue

                # Rate limiting
                await asyncio.sleep(2)

            # Collect EPA regulations (Title 40)
            print("\nFetching EPA regulations (Title 40)...")
            for part_num, part_name in EPA_KEY_PARTS:
                print(f"  Fetching Part {part_num}: {part_name}...")

                try:
                    content = await client.get_full_text(40, part_num)

                    if content and len(content) > 500:
                        # Clean XML content
                        import re
                        text = re.sub(r'<[^>]+>', ' ', content)
                        text = re.sub(r'\s+', ' ', text).strip()

                        # Truncate if too long
                        if len(text) > 50000:
                            text = text[:50000] + "\n\n[Content truncated for storage]"

                        # Check if document already exists
                        checksum = f"ecfr-40-{part_num}"
                        result = await session.execute(
                            select(Document).where(Document.checksum == checksum)
                        )
                        existing = result.scalar_one_or_none()

                        if existing:
                            print(f"    Already exists, skipping...")
                            continue

                        # Create document
                        doc = Document(
                            id=uuid.uuid4(),
                            title=f"40 CFR Part {part_num} - {part_name}",
                            content=text,
                            source_url=f"https://www.ecfr.gov/current/title-40/part-{part_num}",
                            document_type=DocumentType.REGULATION,
                            authority_level=AuthorityLevel.FEDERAL,
                            jurisdiction_type=JurisdictionType.FEDERAL,
                            source_name="eCFR - EPA",
                            citation=f"40 CFR Part {part_num}",
                            published_date=date.today(),
                            checksum=checksum,
                        )
                        session.add(doc)
                        await session.flush()

                        # Create chunks
                        chunks = chunk_text(text, chunk_size=2000, overlap=200)
                        for i, chunk_text_content in enumerate(chunks):
                            embedding = None
                            if embeddings:
                                try:
                                    embedding = await embeddings.generate(chunk_text_content[:8000])
                                except Exception as e:
                                    print(f"    Warning: Could not generate embedding: {e}")

                            chunk = DocumentChunk(
                                id=uuid.uuid4(),
                                document_id=doc.id,
                                content=chunk_text_content,
                                chunk_index=i,
                                embedding=embedding,
                            )
                            session.add(chunk)

                        await session.commit()
                        documents_added += 1
                        print(f"    Added with {len(chunks)} chunks")

                except Exception as e:
                    print(f"    Error: {e}")
                    continue

                await asyncio.sleep(2)

    finally:
        await client.close()

    print(f"\n=== Completed: Added {documents_added} federal regulation documents ===\n")
    return documents_added


def chunk_text(text: str, chunk_size: int = 2000, overlap: int = 200) -> list:
    """Split text into overlapping chunks."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            for sep in ['. ', '.\n', '\n\n', '\n', ' ']:
                sep_pos = text.rfind(sep, start + chunk_size // 2, end)
                if sep_pos != -1:
                    end = sep_pos + len(sep)
                    break

        chunks.append(text[start:end].strip())
        start = end - overlap

        if start >= len(text):
            break

    return chunks


async def show_statistics():
    """Show current database statistics."""
    print("\n=== Database Statistics ===\n")

    await init_db()

    async with get_db_session() as session:
        from sqlalchemy import select, func

        # Count documents
        result = await session.execute(select(func.count(Document.id)))
        doc_count = result.scalar()

        # Count chunks
        result = await session.execute(select(func.count(DocumentChunk.id)))
        chunk_count = result.scalar()

        # Count chunks with embeddings
        result = await session.execute(
            select(func.count(DocumentChunk.id)).where(DocumentChunk.embedding.isnot(None))
        )
        embedded_count = result.scalar()

        # Count by jurisdiction
        result = await session.execute(
            select(Document.jurisdiction_type, func.count(Document.id))
            .group_by(Document.jurisdiction_type)
        )
        jurisdiction_counts = result.all()

        print(f"Total Documents: {doc_count}")
        print(f"Total Chunks: {chunk_count}")
        print(f"Chunks with Embeddings: {embedded_count}")
        print(f"\nDocuments by Jurisdiction:")
        for jur, count in jurisdiction_counts:
            print(f"  {jur.value if jur else 'Unknown'}: {count}")


async def collect_federal_register_data():
    """Collect recent rules from Federal Register API."""
    print("\n=== Collecting Federal Register Rules ===\n")

    await init_db()
    embeddings = get_embeddings()

    documents_added = 0

    # Agencies to collect from
    agencies = [
        ("federal-energy-regulatory-commission", "FERC"),
        ("environmental-protection-agency", "EPA"),
        ("energy-department", "DOE"),
    ]

    async with httpx.AsyncClient(timeout=60.0) as client:
        async with get_db_session() as session:
            for agency_slug, agency_name in agencies:
                print(f"Fetching {agency_name} rules...")

                try:
                    url = "https://www.federalregister.gov/api/v1/documents.json"
                    params = {
                        "conditions[agencies][]": agency_slug,
                        "conditions[type][]": "RULE",
                        "per_page": 20,
                        "fields[]": ["title", "abstract", "document_number", "publication_date",
                                    "html_url", "full_text_xml_url", "raw_text_url", "agencies"]
                    }

                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()

                    for doc_data in data.get("results", []):
                        title = doc_data.get("title", "Untitled")
                        doc_num = doc_data.get("document_number", "")

                        print(f"  Processing: {title[:60]}...")

                        # Check if already exists
                        checksum = f"fr-{doc_num}"
                        result = await session.execute(
                            select(Document).where(Document.checksum == checksum)
                        )
                        existing = result.scalar_one_or_none()

                        if existing:
                            print(f"    Already exists, skipping...")
                            continue

                        # Get full text if available
                        content = doc_data.get("abstract", "")

                        # Try to fetch raw text
                        raw_text_url = doc_data.get("raw_text_url")
                        if raw_text_url:
                            try:
                                text_response = await client.get(raw_text_url)
                                if text_response.status_code == 200:
                                    content = text_response.text
                                    # Truncate if too long
                                    if len(content) > 50000:
                                        content = content[:50000] + "\n\n[Content truncated]"
                            except Exception as e:
                                print(f"    Warning: Could not fetch full text: {e}")

                        if not content or len(content) < 100:
                            print(f"    Skipping - no content")
                            continue

                        # Parse publication date
                        pub_date_str = doc_data.get("publication_date")
                        pub_date = None
                        if pub_date_str:
                            try:
                                from datetime import datetime
                                pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d").date()
                            except:
                                pub_date = date.today()

                        # Create document
                        doc = Document(
                            id=uuid.uuid4(),
                            title=title,
                            content=content,
                            source_url=doc_data.get("html_url", ""),
                            document_type=DocumentType.REGULATION,
                            authority_level=AuthorityLevel.FEDERAL,
                            jurisdiction_type=JurisdictionType.FEDERAL,
                            source_name=f"Federal Register - {agency_name}",
                            citation=f"FR Doc. {doc_num}",
                            published_date=pub_date,
                            checksum=checksum,
                        )
                        session.add(doc)
                        await session.flush()

                        # Create chunks
                        chunks = chunk_text(content, chunk_size=2000, overlap=200)
                        for i, chunk_content in enumerate(chunks):
                            embedding = None
                            if embeddings:
                                try:
                                    embedding = await embeddings.generate(chunk_content[:8000])
                                except Exception as e:
                                    print(f"    Warning: Could not generate embedding: {e}")

                            chunk = DocumentChunk(
                                id=uuid.uuid4(),
                                document_id=doc.id,
                                content=chunk_content,
                                chunk_index=i,
                                embedding=embedding,
                            )
                            session.add(chunk)

                        await session.commit()
                        documents_added += 1
                        print(f"    Added with {len(chunks)} chunks")

                        # Rate limiting
                        await asyncio.sleep(1)

                except Exception as e:
                    print(f"  Error fetching {agency_name}: {e}")
                    continue

    print(f"\n=== Completed: Added {documents_added} Federal Register documents ===\n")
    return documents_added


async def collect_all():
    """Collect data from all available sources."""
    print("\n" + "="*60)
    print("COLLECTING DATA FROM ALL SOURCES")
    print("="*60 + "\n")

    total = 0

    # Show initial stats
    await show_statistics()

    # Collect from Federal Register
    total += await collect_federal_register_data()

    # Show final stats
    await show_statistics()

    print(f"\nTotal documents added: {total}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Collect regulatory data")
    parser.add_argument("--ecfr", action="store_true", help="Collect eCFR federal regulations")
    parser.add_argument("--federal-register", action="store_true", help="Collect Federal Register rules")
    parser.add_argument("--all", action="store_true", help="Collect from all sources")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    args = parser.parse_args()

    if args.stats:
        asyncio.run(show_statistics())
    elif args.ecfr:
        asyncio.run(collect_ecfr_data())
    elif args.federal_register:
        asyncio.run(collect_federal_register_data())
    elif args.all:
        asyncio.run(collect_all())
    else:
        # Default: collect from Federal Register
        asyncio.run(collect_federal_register_data())
        asyncio.run(show_statistics())
