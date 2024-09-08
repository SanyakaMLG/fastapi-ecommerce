from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User, OrderStatus
from app.schemas.order import OrderCreate
from app.services.order import OrderService
from app.utils.common import current_user

router = APIRouter(prefix='/order', tags=['orders'])

@router.get('/my_orders')
async def get_orders(session: AsyncSession = Depends(get_session), user: User = Depends(current_user())):
    try:
        orders = await OrderService.get_orders(session, user)
        return orders
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post('/create_order')
async def create_order(order_create: OrderCreate,
                       session: AsyncSession = Depends(get_session),
                       user: User = Depends(current_user())):
    try:
        order = await OrderService.create_order(session, user, order_create)
        return order
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post('/cancel_order')
async def cancel_order(order_id: int,
                       session: AsyncSession = Depends(get_session),
                       user: User = Depends(current_user())):
    try:
        order = await OrderService.update_order_status(session, user, order_id, OrderStatus.canceled)
        return order
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post('/update_status')
async def update_order_status(order_id: int, status: OrderStatus,
                              session: AsyncSession = Depends(get_session),
                              user: User = Depends(current_user(superuser=True))):
    try:
        order = await OrderService.update_order_status(session, user, order_id, status)
        return order
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
