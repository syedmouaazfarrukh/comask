"""
Fix broken Colorado URLs in the database.

Changes direct PDF links (which return 403) to landing pages that work.

Run with: python -m scripts.fix_colorado_urls
"""

import asyncio
from sqlalchemy import select, update
from app.db.database import get_db_session, init_db
from app.db.models import Document

# URL replacements: old_url -> new_url
URL_FIXES = {
    # Colorado Legislature PDFs -> Landing pages
    "https://leg.colorado.gov/sites/default/files/images/olls/crs2021-title-40.pdf":
        "https://leg.colorado.gov/colorado-revised-statutes",
    "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-40.pdf":
        "https://leg.colorado.gov/colorado-revised-statutes",

    # Colorado PUC E-Filing (needs verification - may need different filing ID)
    "https://www.dora.state.co.us/pls/efi/EFI.Show_Filing?p_fil=G_930344":
        "https://www.dora.state.co.us/pls/efi/EFI_Search_UI.search",

    # FERC Order 2222 -> eLibrary search
    "https://www.ferc.gov/media/ferc-order-no-2222-fact-sheet":
        "https://elibrary.ferc.gov/eLibrary/search?q=order%202222",

    # NERC -> Direct standards page (may work better)
    "https://www.nerc.com/pa/Stand/Pages/ReliabilityStandards.aspx":
        "https://www.nerc.com/pa/Stand/Pages/AllReliabilityStandards.aspx",
}


async def fix_urls():
    """Update broken URLs in the database."""
    await init_db()

    async with get_db_session() as session:
        # Get all documents
        result = await session.execute(select(Document))
        documents = result.scalars().all()

        fixed_count = 0

        for doc in documents:
            if doc.source_url in URL_FIXES:
                old_url = doc.source_url
                new_url = URL_FIXES[old_url]

                print(f"Fixing: {doc.title[:50]}...")
                print(f"  Old: {old_url[:60]}...")
                print(f"  New: {new_url[:60]}...")
                print()

                doc.source_url = new_url
                fixed_count += 1

        if fixed_count > 0:
            await session.commit()
            print(f"✅ Fixed {fixed_count} URLs")
        else:
            print("No URLs needed fixing")


async def dry_run():
    """Preview what would be fixed without making changes."""
    await init_db()

    print("=== DRY RUN: URLs that would be fixed ===\n")

    async with get_db_session() as session:
        result = await session.execute(select(Document))
        documents = result.scalars().all()

        would_fix = 0

        for doc in documents:
            if doc.source_url in URL_FIXES:
                print(f"Document: {doc.title[:60]}...")
                print(f"  Current URL: {doc.source_url[:70]}...")
                print(f"  Would change to: {URL_FIXES[doc.source_url][:70]}...")
                print()
                would_fix += 1

        print(f"Total documents that would be fixed: {would_fix}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        asyncio.run(dry_run())
    else:
        print("Running URL fix script...")
        print("Use --dry-run to preview changes without applying them\n")
        asyncio.run(fix_urls())
