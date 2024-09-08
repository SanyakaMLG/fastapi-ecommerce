from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas.product import ProductCreate
from app.services.product import ProductService
from app.utils.common import current_user

router = APIRouter(prefix="/product", tags=["products"])

@router.get("/{product_id}")
async def get_product(product_id: int,
                      session: AsyncSession = Depends(get_session)):
    try:
        product = await ProductService.get_product(session, product_id)
        return product
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/")
async def create_product(product: ProductCreate,
                         session: AsyncSession = Depends(get_session),
                         user: User = Depends(current_user(superuser=True))):
    try:
        new_product = await ProductService.create_product(session, product)
        return new_product
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post("/filtered")
async def get_products(category_id: int = None, skip: int = 0, limit: int = 100, filter: dict[int, list[int]] = None,
                       session: AsyncSession = Depends(get_session)):
    try:
        products = await ProductService.get_products(session, category_id, skip, limit, filter)
        return products
    except HTTPException as e:
        raise e

@router.put("/{product_id}")
async def update_product(product_id: int,
                         product: ProductCreate,
                         session: AsyncSession = Depends(get_session),
                         user: User = Depends(current_user(superuser=True))):
    try:
        updated_product = await ProductService.update_product(session, product_id, product)
        return updated_product
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get('/available_filters/{category_id}')
async def get_available_filters(category_id: int, session: AsyncSession = Depends(get_session)):
    filters = await ProductService.get_available_filters(session, category_id)
    return filters