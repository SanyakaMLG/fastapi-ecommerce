from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import User
from app.schemas.shipping_address import ShippingAddressCreate, ShippingAddressUpdate
from app.services.shipping_address import ShippingAddressService
from app.utils.common import current_user

router = APIRouter(prefix='/shipping_address', tags=['shipping_addresses'])

@router.post('/')
async def create_shipping_address(address: ShippingAddressCreate,
                                  session: AsyncSession = Depends(get_session),
                                  user: User = Depends(current_user())):
    try:
        new_address = await ShippingAddressService.create_shipping_address(session, address, user)
        return new_address
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.put('/{address_id}')
async def update_shipping_address(address_id: int,
                                  address: ShippingAddressUpdate,
                                  session: AsyncSession = Depends(get_session),
                                  user: User = Depends(current_user())):
    try:
        updated_address = await ShippingAddressService.update_shipping_address(session, address_id, address, user)
        return updated_address
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete('/{address_id}')
async def delete_shipping_address(address_id: int,
                                  session: AsyncSession = Depends(get_session),
                                  user: User = Depends(current_user())):
    try:
        deleted_address = await ShippingAddressService.delete_shipping_address(session, address_id, user)
        return deleted_address
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")