from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.future import select

from app.models import Review, User
from app.schemas.review import ReviewCreate, ReviewUpdate
from fastapi import HTTPException


class ReviewService:
    @staticmethod
    async def create_review(session: AsyncSession, review: ReviewCreate, user: User):
        product_id = review.product_id
        query = select(Review).where(Review.product_id == product_id, Review.user_id == user.id)
        result = await session.execute(query)
        try:
            result.scalar_one()
            raise HTTPException(status_code=400, detail="You have already reviewed this product")
        except NoResultFound:
            pass
        new_review = Review(**review.model_dump())
        new_review.user_id = user.id
        session.add(new_review)
        try:
            await session.commit()
            await session.refresh(new_review)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400,
                                detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return new_review

    @staticmethod
    async def update_review(session: AsyncSession, review_id: int, review_update: ReviewUpdate, user: User):
        try:
            result = await session.execute(select(Review).where(Review.id == review_id))
            review = result.scalar_one()
            if review.user_id != user.id and not user.is_superuser:
                raise HTTPException(status_code=403, detail="Permission denied")
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Review not found")
        for key, value in review_update.model_dump(exclude_unset=True).items():
            setattr(review, key, value)
        try:
            await session.commit()
            await session.refresh(review)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return review

    @staticmethod
    async def delete_review(session: AsyncSession, review_id: int, user: User):
        try:
            result = await session.execute(select(Review).where(Review.id == review_id))
            review = result.scalar_one()
            if review.user_id != user.id and not user.is_superuser:
                raise HTTPException(status_code=403, detail="Permission denied")
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Review not found")
        try:
            await session.delete(review)
            await session.commit()
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return review