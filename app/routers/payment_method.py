from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas.payment_method import PaymentMethodCreate
from app.services.payment_method import PaymentMethodService
from app.utils.common import current_user

router = APIRouter(prefix='/payment_method', tags=['payment_methods'])

@router.get('/')
async def get_payment_methods(session: AsyncSession = Depends(get_session),
                              user: User = Depends(current_user())):
    try:
        payment_methods = await PaymentMethodService.get_payment_methods(session, user)
        return payment_methods
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post('/')
async def create_payment_method(payment_method: PaymentMethodCreate,
                                session: AsyncSession = Depends(get_session),
                                user: User = Depends(current_user())):
    try:
        new_payment_method = await PaymentMethodService.create_payment_method(session, payment_method, user)
        return new_payment_method
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete('/{payment_method_id}')
async def delete_payment_method(payment_method_id: int,
                                session: AsyncSession = Depends(get_session),
                                user: User = Depends(current_user())):
    try:
        deleted_payment_method = await PaymentMethodService.delete_payment_method(session, payment_method_id, user)
        return deleted_payment_method
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
