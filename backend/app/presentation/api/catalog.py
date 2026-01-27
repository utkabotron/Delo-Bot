from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.application.dto import CatalogProductDTO, CatalogProductGroupedDTO
from app.application.use_cases import CatalogUseCases
from app.infrastructure.persistence.repositories import SQLAlchemyCatalogRepository
from app.infrastructure.external import GoogleSheetsService

router = APIRouter(prefix="/api/catalog", tags=["catalog"])


def get_use_cases(db: Session = Depends(get_db)) -> CatalogUseCases:
    repository = SQLAlchemyCatalogRepository(db)
    return CatalogUseCases(repository)


@router.get("/grouped", response_model=list[CatalogProductGroupedDTO])
def get_catalog_grouped(
    use_cases: CatalogUseCases = Depends(get_use_cases),
):
    """Возвращает весь каталог с базовыми названиями для dropdown"""
    return use_cases.get_all_grouped()


@router.get("/search", response_model=list[CatalogProductDTO])
def search_catalog(
    q: str = Query("", min_length=0),
    limit: int = Query(20, ge=1, le=100),
    use_cases: CatalogUseCases = Depends(get_use_cases),
):
    return use_cases.search_products(q, limit)


@router.post("/sync")
def sync_catalog(
    db: Session = Depends(get_db),
    use_cases: CatalogUseCases = Depends(get_use_cases),
):
    """Синхронизация каталога из Google Sheets"""
    sheets_service = GoogleSheetsService()
    products = sheets_service.fetch_catalog()

    if not products:
        return {"status": "error", "message": "Failed to fetch data from Google Sheets", "count": 0}

    count = use_cases.sync_catalog(products)
    return {"status": "success", "count": count}


@router.get("/{product_id}", response_model=CatalogProductDTO)
def get_product(
    product_id: int,
    use_cases: CatalogUseCases = Depends(get_use_cases),
):
    product = use_cases.get_product(product_id)
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Product not found")
    return product
