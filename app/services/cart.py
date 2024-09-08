from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User, Cart, CartItem, Product


class CartService:
    @staticmethod
    async def get_cart(session: AsyncSession, user: User):
        query = select(Cart).where(Cart.user_id == user.id).options(selectinload(Cart.products))
        cart = await session.execute(query)
        return cart.scalars().all()

    @staticmethod
    async def add_to_cart(session: AsyncSession, user: User, product_id: int):
        query = select(Product).where(Product.id == product_id)
        product = await session.execute(query)
        try:
            product = product.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Product not found")

        max_quantity = product.quantity
        if max_quantity == 0:
            raise HTTPException(status_code=400, detail="Product is out of stock")

        query = select(Cart).where(Cart.user_id == user.id)
        cart = await session.execute(query)
        try:
            cart = cart.scalar_one()
        except NoResultFound:
            cart = Cart(user_id=user.id, is_active=True)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)

        query = select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        cart_item = await session.execute(query)
        try:
            cart_item = cart_item.scalar_one()
            if cart_item.quantity >= max_quantity:
                raise HTTPException(
                    status_code=400, detail="The maximum quantity of this product is already in the cart"
                )
            cart_item.quantity += 1
        except NoResultFound:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=1,
                history_price=None
            )
            session.add(cart_item)

        try:
            await session.commit()
            await session.refresh(cart_item)
            return cart_item
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

    @staticmethod
    async def remove_from_cart(session: AsyncSession, user: User, product_id: int, full_remove: bool = False):
        query = select(Cart).where(Cart.user_id == user.id, Cart.is_active)
        cart = await session.execute(query)
        try:
            cart = cart.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Your cart is empty")

        query = select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product_id)
        cart_item = await session.execute(query)
        try:
            cart_item = cart_item.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Product not found in cart")

        cart_item.quantity -= 1

        if cart_item.quantity == 0 or full_remove:
            await session.delete(cart_item)

        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

        return cart_item

    @staticmethod
    async def before_order(session: AsyncSession, user: User):
        query = (
            select(Cart)
            .where(Cart.user_id == user.id, Cart.is_active)
        )
        cart = await session.execute(query)
        try:
            cart = cart.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Your cart is empty")

        query = (
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .options(selectinload(CartItem.product))
        )
        cart_items = await session.execute(query)
        cart_items = cart_items.scalars().all()

        sold_products = []
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.quantity:
                cart_item.quantity = cart_item.product.quantity
                sold_products.append(cart_item.product.title)

        if sold_products:
            raise HTTPException(
                status_code=400,
                detail=f"Products {', '.join(sold_products)} are out of stock. Quantity has been updated"
            )

        return cart_items

    @staticmethod
    async def after_order(session: AsyncSession, user: User):
        query = (
            select(Cart)
            .where(Cart.user_id == user.id, Cart.is_active)
        )
        cart = await session.execute(query)
        cart = cart.scalar_one()

        query = (
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .options(selectinload(CartItem.product))
        )
        cart_items = await session.execute(query)

        for cart_item in cart_items.scalars().all():
            cart_item.history_price = cart_item.product.price
            cart_item.product.quantity -= cart_item.quantity

        cart.is_active = False
        await session.commit()
        return cart