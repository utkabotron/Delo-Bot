#!/usr/bin/env python3
"""
Скрипт синхронизации каталога из Google Sheets.
Можно запускать через cron: 0 * * * * cd /path/to/delo-bot && python scripts/sync_catalog.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal
from app.infrastructure.persistence.repositories import SQLAlchemyCatalogRepository
from app.infrastructure.external import GoogleSheetsService
from app.application.use_cases import CatalogUseCases


def main():
    print("Starting catalog sync...")

    # Fetch from Google Sheets
    sheets_service = GoogleSheetsService()
    products = sheets_service.fetch_catalog()

    if not products:
        print("Failed to fetch data from Google Sheets or no products found")
        return 1

    print(f"Fetched {len(products)} products from Google Sheets")

    # Save to database
    db = SessionLocal()
    try:
        repository = SQLAlchemyCatalogRepository(db)
        use_cases = CatalogUseCases(repository)
        count = use_cases.sync_catalog(products)
        print(f"Successfully synced {count} products to database")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
