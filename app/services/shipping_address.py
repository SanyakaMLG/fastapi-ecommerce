from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.shipping_address import ShippingAddressCreate, ShippingAddressUpdate
from app.models import User, ShippingAddress


class ShippingAddressService:
    @staticmethod
    async def create_shipping_address(session: AsyncSession, address: ShippingAddressCreate, user: User):
        new_address = ShippingAddress(**address.model_dump())
        new_address.user_id = user.id
        session.add(new_address)
        try:
            await session.commit()
            await session.refresh(new_address)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400,
                                detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return new_address

    @staticmethod
    async def update_shipping_address(session: AsyncSession, address_id: int, address_update: ShippingAddressUpdate, user: User):
        try:
            result = await session.execute(select(ShippingAddress).where(ShippingAddress.id == address_id))
            address = result.scalar_one()
            if address.user_id != user.id:
                raise HTTPException(status_code=403, detail="Permission denied")
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Address not found")
        for key, value in address_update.model_dump(exclude_unset=True).items():
            setattr(address, key, value)
        try:
            await session.commit()
            await session.refresh(address)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return address

    @staticmethod
    async def delete_shipping_address(session: AsyncSession, address_id: int, user: User):
        try:
            result = await session.execute(select(ShippingAddress).where(ShippingAddress.id == address_id))
            address = result.scalar_one()
            if address.user_id != user.id:
                raise HTTPException(status_code=403, detail="Permission denied")
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Address not found")

        try:
            await session.delete(address)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return address