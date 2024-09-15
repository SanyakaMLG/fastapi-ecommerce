from fastapi import HTTPException
from sqlalchemy import select, insert, Result
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, lazyload

from app.models import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    async def get_categories(session: AsyncSession):
        query = select(Category)
        categories = await session.execute(query)
        return categories.scalars().all()

    @staticmethod
    async def create_category(session: AsyncSession, category: CategoryCreate):
        query = insert(Category).values(**category.model_dump())
        try:
            await session.execute(query)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return category

    @staticmethod
    async def update_category(session: AsyncSession, category_update: CategoryUpdate, category_id: int):
        try:
            result = await session.execute(select(Category).where(Category.id == category_id))
            category = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Category not found")
        for key, value in category_update.model_dump(exclude_unset=True).items():
            setattr(category, key, value)
        try:
            await session.commit()
            await session.refresh(category)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return category

    @staticmethod
    async def get_categories_with_children(session: AsyncSession, category_id: int) -> list[int]:
        async def get_all_children_ids(category_id: int) -> list[int]:
            stmt = select(Category).filter_by(parent_id=category_id)
            result = await session.execute(stmt)
            categories = result.scalars().all()
            ids = [c.id for c in categories]
            for category in categories:
                ids.extend(await get_all_children_ids(category.id))
            return ids

        result_ids = [category_id]
        result_ids.extend(await get_all_children_ids(category_id))
        return result_ids