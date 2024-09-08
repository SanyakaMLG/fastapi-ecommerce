...
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.future import select

from app.models import PaymentMethod, User
from app.schemas.payment_method import PaymentMethodCreate, PaymentMethodUpdate
from fastapi import HTTPException


class PaymentMethodService:
    @staticmethod
    async def create_payment_method(session: AsyncSession, payment_method: PaymentMethodCreate, user: User):
        new_payment_method = PaymentMethod(**payment_method.model_dump() | {'user_id': user.id})
        session.add(new_payment_method)
        try:
            await session.commit()
            await session.refresh(new_payment_method)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400,
                                detail="A unique constraint was violated or referential integrity error")
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return new_payment_method

    @staticmethod
    async def update_payment_method(session: AsyncSession, payment_method_id: int,
                                    payment_method_update: PaymentMethodUpdate, user: User):
        try:
            result = await session.execute(select(PaymentMethod).where(PaymentMethod.id == payment_method_id))
            payment_method = result.scalar_one()
            if payment_method.user_id != user.id:
                raise HTTPException(status_code=403, detail="Permission denied")
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Payment Method not found")
        for key, value in payment_method_update.model_dump(exclude_unset=True).items():
            setattr(payment_method, key, value)
        try:
            await session.commit()
            await session.refresh(payment_method)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return payment_method


    @staticmethod
    async def delete_payment_method(session: AsyncSession, payment_method_id: int, user: User):
        try:
            result = await session.execute(select(PaymentMethod).where(PaymentMethod.id == payment_method_id))
            payment_method = result.scalar_one()
            if payment_method.user_id != user.id:
                raise HTTPException(status_code=403, detail="Permission denied")
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Payment Method not found")
        try:
            await session.delete(payment_method)
            await session.commit()
            return payment_method
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
