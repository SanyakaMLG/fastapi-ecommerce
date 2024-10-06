from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import CategoryService
from app.utils.common import current_user

router = APIRouter(prefix='/categories', tags=['categories'])


@router.get('/')
async def get_categories(session: AsyncSession = Depends(get_session)):
    result = await CategoryService.get_categories(session)
    return result


@router.get('/tree')
async def get_tree_categories(session: AsyncSession = Depends(get_session)):
    result = await CategoryService.get_categories_tree(session)
    return result


@router.post('/')
async def create_category(category: CategoryCreate,
                          session: AsyncSession = Depends(get_session),
                          user: User = Depends(current_user(superuser=True))):
    try:
        new_category = await CategoryService.create_category(session, category)
        return new_category
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post('/{category_id}')
async def update_category(category: CategoryUpdate,
                          category_id: int,
                          session: AsyncSession = Depends(get_session),
                          user = Depends(current_user(superuser=True))):
    try:
        updated_category = await CategoryService.update_category(session, category, category_id)
        return updated_category
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

