import random

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import User, Cart, CartItem, Order, OrderStatus, PaymentMethod
from app.schemas.order import OrderCreate
from app.services.cart import CartService


class OrderService:
    @staticmethod
    async def create_order(session: AsyncSession, user: User, order_in: OrderCreate):
        active_cart = await CartService.get_cart(session, user)
        if not active_cart:
            raise HTTPException(status_code=400, detail="You don't have any items in your cart for create order")

        payment_method = select(PaymentMethod).where(PaymentMethod.id == order_in.payment_method_id)
        payment_method = await session.execute(payment_method)
        try:
            payment_method = payment_method.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Payment method not found")

        if payment_method.user_id != user.id:
            raise HTTPException(status_code=403, detail="Permission denied")

        cart_items, products = await CartService.before_order(session, user)

        cart_cost = 0
        for cart_item in cart_items:
            product = next(filter(lambda x: x.id == cart_item.product_id, products))
            cart_cost += product.price * cart_item.quantity * (1 - product.discount / 100)

        order_params = order_in.model_dump()

        if order_params['delivery_type'] == 'delivery' and order_params['delivery_address'] is None:
            raise HTTPException(status_code=400, detail="Delivery address is required for delivery type")

        order = Order(
            **order_params,
            status=OrderStatus.new,
            cart_id=active_cart.id,
            cart_cost=cart_cost,
            delivery_cost=random.randint(150, 300) if order_params['delivery_type'] == 'delivery' else 0
        )

        session.add(order)

        cart = await CartService.after_order(session, user)
        try:
            await session.commit()
            await session.refresh(order)
        except IntegrityError as e:
            await session.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

        return cart

    @staticmethod
    async def get_orders(session: AsyncSession, user: User):
        query = (
            select(Cart)
            .where(Cart.user_id == user.id, Cart.is_active == False)
            .options(selectinload(Cart.order).
                     selectinload(Order.shipping_address),
                     selectinload(Cart.order).
                     selectinload(Order.payment_method),
                     selectinload(Cart.products))
            .order_by(Cart.created_at.desc())
        )
        orders = await session.execute(query)
        orders = orders.scalars().all()

        list_orders = []
        for order in orders:
            dict_order = {}

            query = (
                select(CartItem)
                .where(CartItem.cart_id == order.id)
            )
            cart_items = await session.execute(query)
            cart_items = cart_items.scalars().all()

            dict_order['order_num'] = order.order.id
            dict_order['status'] = order.order.status.value
            dict_order['cart_cost'] = order.order.cart_cost
            dict_order['delivery_type'] = order.order.delivery_type.value
            dict_order['delivery_cost'] = order.order.delivery_cost
            dict_order['total_cost'] = order.order.cart_cost + order.order.delivery_cost
            dict_order['created_at'] = order.order.created_at
            dict_order['products'] = []
            for cart_item in cart_items:
                product = next(filter(lambda x: x.id == cart_item.product_id, order.products))
                dict_product = {
                    'product_name': product.title,
                    'quantity': cart_item.quantity,
                    'price': cart_item.history_price
                }
                dict_order['products'].append(dict_product)

            dict_order['delivery_address'] = order.order.shipping_address
            dict_order['payment_method'] = order.order.payment_method

            list_orders.append(dict_order)

        return list_orders

    @staticmethod
    async def update_order_status(session: AsyncSession, user: User, order_id: int, status: OrderStatus):
        query = (
            select(Order)
            .where(Order.id == order_id)
        )
        order = await session.execute(query)
        try:
            order = order.scalar_one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Order not found")

        if (status == OrderStatus.canceled
                and order.cart.user_id != user.id
                and not user.is_superuser):
            raise HTTPException(status_code=403, detail="Permission denied")

        order.status = status

        try:
            await session.commit()
        except:
            await session.rollback()
            raise HTTPException(status_code=500, detail="An unexpected error occurred")

        return order
