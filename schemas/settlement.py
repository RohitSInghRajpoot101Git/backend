from pydantic import BaseModel, EmailStr, Field, datetime
from uuid import UUID
from decimal import Decimal


class SettlementCreate(BaseModel):
    # group_id : UUID
    # payer_id : UUID
    # receiver_id : UUID
    amount : Decimal = Field(gt=0)
    
class SettlementResponse(BaseModel):
    id : UUID
    group_id : UUID
    payer_id : UUID
    receiver_id : UUID
    amount : Decimal = Field(gt=0)

class SettlementUpdate(BaseModel):
    # Should payer_id,receiver_id and ammount be optional or mendatatory?
    payer_id : UUID | None = None
    receiver_id : UUID | None = None
    amount : Decimal | None = Field(default=None,gt=0)
    
class SettlementListResponse(BaseModel):
    settlements : list [SettlementResponse] | None = None
    total_count : int = 0
    

# Basic schema, needed to be updated later 
