from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.services.cart import CartService
from app.utils.common import current_user

router = APIRouter(prefix='/cart', tags=['carts'])

@router.get('/my_cart')
async def get_cart(session: AsyncSession = Depends(get_session), user: User = Depends(current_user())):
    return CartService.get_cart(session, user)

@router.post('/add_to_cart')
async def add_to_cart(product_id: int,
                      session: AsyncSession = Depends(get_session),
                      user: User = Depends(current_user())):
    try:
        new_cart_item = await CartService.add_to_cart(session, user, product_id)
        return new_cart_item
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.post('/remove_from_cart')
async def remove_from_cart(product_id: int,
                           full_remove: bool = False,
                           session: AsyncSession = Depends(get_session),
                           user: User = Depends(current_user())):
    try:
        cart_item = await CartService.remove_from_cart(session, user, product_id, full_remove)
        return cart_item
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
