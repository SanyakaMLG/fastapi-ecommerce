from random import setstate

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.attribute import AttributeCreate, AttributeUpdate
from app.services.attribute import AttributeService
from app.utils.common import current_user

router = APIRouter(prefix='/attribute', tags=['attributes'])

@router.post('/')
async def create_attribute(attribute: AttributeCreate,
                           session: AsyncSession = Depends(get_session),
                           user = Depends(current_user(superuser=True))):
    try:
        new_attribute = await AttributeService.create_attribute(session, attribute)
        return new_attribute
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.put('/{attribute_id}')
async def update_attribute(attribute_id: int,
                           attribute: AttributeUpdate,
                           session: AsyncSession = Depends(get_session),
                           user = Depends(current_user(superuser=True))):
    try:
        updated_attribute = await AttributeService.update_attribute(session, attribute_id, attribute)
        return updated_attribute
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500)

@router.delete('/{attribute_id}')
async def delete_attribute(attribute_id: int,
                           session: AsyncSession = Depends(get_session),
                           user = Depends(current_user(superuser=True))):
    try:
        deleted_attribute = await AttributeService.delete_attribute(session, attribute_id)
        return deleted_attribute
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500)
