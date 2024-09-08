from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.future import select

from app.models import Attribute
from app.schemas.attribute import AttributeCreate, AttributeUpdate
from fastapi import HTTPException


class AttributeService:
    @staticmethod
    async def create_attribute(session: AsyncSession, attribute: AttributeCreate):
        new_attribute = Attribute(**attribute.model_dump())
        session.add(new_attribute)
        try:
            await session.commit()
            await session.refresh(new_attribute)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400,
                                detail=str(e))
        return new_attribute

    @staticmethod
    async def get_attribute(session: AsyncSession, attribute_id: int):
        try:
            result = await session.execute(select(Attribute).where(Attribute.id == attribute_id))
            attribute = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Attribute not found")
        return attribute

    @staticmethod
    async def update_attribute(session: AsyncSession, attribute_id: int, attribute_update: AttributeUpdate):
        try:
            result = await session.execute(select(Attribute).where(Attribute.id == attribute_id))
            attribute = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Attribute not found")
        for key, value in attribute_update.model_dump(exclude_unset=True).items():
            setattr(attribute, key, value)
        try:
            await session.commit()
            await session.refresh(attribute)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return attribute

    @staticmethod
    async def delete_attribute(session: AsyncSession, attribute_id: int):
        try:
            result = await session.execute(select(Attribute).where(Attribute.id == attribute_id))
            attribute = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Attribute not found")
        await session.delete(attribute)
        await session.commit()
        return attribute
