from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.future import select

from app.models import AttributeValue
from app.schemas.attribute_value import AttributeValueCreate, AttributeValueUpdate
from fastapi import HTTPException


class AttributeValueService:
    @staticmethod
    async def create_attribute_value(session: AsyncSession, attribute_value: AttributeValueCreate):
        new_attribute_value = AttributeValue(**attribute_value.model_dump())
        session.add(new_attribute_value)
        try:
            await session.commit()
            await session.refresh(new_attribute_value)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400,
                                detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return new_attribute_value

    @staticmethod
    async def get_attribute_value(session: AsyncSession, attribute_value_id: int):
        try:
            result = await session.execute(select(AttributeValue).where(AttributeValue.id == attribute_value_id))
            attribute_value = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Attribute Value not found")
        return attribute_value

    @staticmethod
    async def update_attribute_value(session: AsyncSession, attribute_value_id: int,
                                     attribute_value_update: AttributeValueUpdate):
        try:
            result = await session.execute(select(AttributeValue).where(AttributeValue.id == attribute_value_id))
            attribute_value = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Attribute Value not found")
        for key, value in attribute_value_update.model_dump(exclude_unset=True).items():
            setattr(attribute_value, key, value)
        try:
            await session.commit()
            await session.refresh(attribute_value)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return attribute_value

    @staticmethod
    async def delete_attribute_value(session: AsyncSession, attribute_value_id: int):
        try:
            result = await session.execute(select(AttributeValue).where(AttributeValue.id == attribute_value_id))
            attribute_value = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Attribute Value not found")
        try:
            await session.delete(attribute_value)
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
        return attribute_value
