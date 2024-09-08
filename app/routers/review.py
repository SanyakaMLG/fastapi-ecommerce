from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.services.review import ReviewService
from app.utils.common import current_user

router = APIRouter(prefix='/review', tags=['reviews'])

@router.post('/')
async def create_review(review: ReviewCreate,
                        session: AsyncSession = Depends(get_session),
                        user: User = Depends(current_user())):
    try:
        new_review = await ReviewService.create_review(session, review, user)
        return new_review
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.put('/{review_id}')
async def update_review(review_id: int,
                        review: ReviewUpdate,
                        session: AsyncSession = Depends(get_session),
                        user: User = Depends(current_user())):
    try:
        updated_review = await ReviewService.update_review(session, review_id, review, user)
        return updated_review
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete('/{review_id}')
async def delete_review(review_id: int,
                        session: AsyncSession = Depends(get_session),
                        user: User = Depends(current_user())):
    try:
        deleted_review = await ReviewService.delete_review(session, review_id, user)
        return deleted_review
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
