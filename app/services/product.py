import json

from fastapi import HTTPException
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Product, ProductAttributeValues, AttributeValue
from app.schemas.product import ProductCreate
from app.utils.common import remap_available_filters


class ProductService:
    @staticmethod
    async def create_product(session: AsyncSession, product_create: ProductCreate):
        product = product_create.model_dump()
        attribute_values = product.pop('attribute_values')
        new_product = Product(**product)
        session.add(new_product)

        for attribute_value_id in attribute_values:
            product_attribute_value = ProductAttributeValues(
                product_id=new_product.id,
                attribute_value_id=attribute_value_id)
            session.add(product_attribute_value)

        try:
            await session.commit()
            await session.refresh(new_product)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400,
                                detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500,
                                detail="An unexpected error occurred")
        return new_product

    @staticmethod
    async def get_product(session: AsyncSession, product_id: int):
        query = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.reviews), selectinload(Product.attributes))
        )
        result = await session.execute(query)
        try:
            product = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Product not found")

        return product

    @staticmethod
    async def _get_available_filters(session: AsyncSession, category_id: int):
        query = (
            select(Product)
            .where(Product.category_id == category_id)
            .options(selectinload(Product.attributes))
        )
        result = await session.execute(query)
        products = result.scalars().all()

        filters = {}
        for product in products:
            for attribute_value in product.attributes:
                if not attribute_value.attribute.in_filter:
                    continue
                attribute_id = attribute_value.attribute_id
                value_id = attribute_value.id
                if attribute_id not in filters:
                    filters[attribute_id] = {value_id}
                else:
                    if value_id not in filters[attribute_id]:
                        filters[attribute_id].add(value_id)
        return filters

    @staticmethod
    async def get_available_filters(session: AsyncSession, category_id: int):
        if category_id is None:
            return {}

        query = (
            select(Product)
            .where(Product.category_id == category_id)
        )
        result = await session.execute(query)
        products = result.scalars().all()

        filters = {}
        for product in products:
            for attribute_value in product.attributes:
                attribute_name = attribute_value.attribute.title
                attribute_id = attribute_value.attribute_id
                value_id = attribute_value.id
                value_name = attribute_value.value
                if (attribute_name, attribute_id) not in filters:
                    filters[(attribute_name, attribute_id)] = \
                        {(value_name, value_id)}
                else:
                    if (value_name, value_id) not in filters[(attribute_name, attribute_id)]:
                        filters[(attribute_name, attribute_id)].add((value_name, value_id))
        return remap_available_filters(filters)

    @staticmethod
    async def get_products(session: AsyncSession, category_id: int = None,
                           skip: int = 0, limit: int = 100,
                           filter: dict[int, list[int]] = None):
        if not filter:
            query = select(Product)
            if category_id:
                query = query.where(Product.category_id == category_id)
            query = query.offset(skip).limit(limit)
            result = await session.execute(query)
            return result.scalars().all()
        elif category_id is None:
            raise HTTPException(status_code=400, detail="Category ID is required for filtering")

        available_filters = await ProductService._get_available_filters(session, category_id)
        for attribute_id, values in filter.items():
            if attribute_id not in available_filters:
                raise HTTPException(status_code=400, detail="Invalid filter")
            for value_id in values:
                if value_id not in available_filters[attribute_id]:
                    raise HTTPException(status_code=400, detail="Invalid filter value")

        query = (
                select(Product)
                .where(Product.category_id == category_id)
                .join(ProductAttributeValues,
                      Product.id == ProductAttributeValues.product_id)
                .join(AttributeValue,
                      AttributeValue.id == ProductAttributeValues.attribute_value_id)
                .distinct()
            )

        conditions = []
        for atr_id, av_ids in filter.items():
            subconditions = []

            for av_id in av_ids:
                subquery = (
                    select(ProductAttributeValues.product_id)
                    .join(AttributeValue,
                          AttributeValue.id == ProductAttributeValues.attribute_value_id)
                    .where(AttributeValue.id == av_id)
                    .distinct()
                ).subquery()
                subconditions.append(Product.id.in_(subquery))

            conditions.append(or_(*subconditions))

        if conditions:
            query = query.where(and_(*conditions)).offset(skip).limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_product(session: AsyncSession, product_id: int, product_update: ProductCreate):
        try:
            result = await session.execute(select(Product).where(Product.id == product_id))
            product = result.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Product not found")

        product_update = product_update.model_dump()
        new_attribute_values = product_update.pop('attribute_values')
        for key, value in product_update.items():
            setattr(product, key, value)

        query = select(ProductAttributeValues).where(ProductAttributeValues.product_id == product_id)
        result = await session.execute(query)
        product_attribute_values = result.scalars().all()
        for product_attribute_value in product_attribute_values:
            await session.delete(product_attribute_value)

        session.add(product)

        for attribute_value_id in new_attribute_values:
            product_attribute_value = ProductAttributeValues(
                product_id=product_id,
                attribute_value_id=attribute_value_id)
            session.add(product_attribute_value)

        try:
            await session.commit()
            await session.refresh(product)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400,
                                detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500,
                                detail="An unexpected error occurred")
        return product