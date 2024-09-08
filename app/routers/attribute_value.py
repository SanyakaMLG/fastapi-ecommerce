from alembic.util import status
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.attribute_value import AttributeValueCreate, AttributeValueUpdate
from app.services.attribute_value import AttributeValueService
from app.utils.common import current_user

router = APIRouter(prefix='/attribute_value', tags=['attribute_values'])

@router.post('/')
async def create_attribute_value(attribute_value: AttributeValueCreate,
                                 session: AsyncSession = Depends(get_session),
                                 user = Depends(current_user(superuser=True))):
    try:
        new_attribute_value = await AttributeValueService.create_attribute_value(session, attribute_value)
        return new_attribute_value
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.put('/{attribute_value_id}')
async def update_attribute_value(attribute_value_id: int,
                                 attribute_value: AttributeValueUpdate,
                                 session: AsyncSession = Depends(get_session),
                                 user = Depends(current_user(superuser=True))):
    try:
        updated_attribute_value = await AttributeValueService.update_attribute_value(session, attribute_value_id, attribute_value)
        return updated_attribute_value
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500)

@router.delete('/{attribute_value_id}')
async def delete_attribute_value(attribute_value_id: int,
                                 session: AsyncSession = Depends(get_session),
                                 user = Depends(current_user(superuser=True))):
    try:
        deleted_attribute_value = await AttributeValueService.delete_attribute_value(session, attribute_value_id)
        return deleted_attribute_value
    except HTTPException as e:
        raise e
    except:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
