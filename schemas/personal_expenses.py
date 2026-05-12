from datetime import datetime 
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel

class personalExpenseCreate(BaseModel):
    title : str 
    amount : Decimal
    category :str |None = None
    date : datetime |None = None
    notes : str | None = None

class personalExpenseUpdate(BaseModel):
    title : str | None = None
    amount : Decimal | None = None
    category :str |None = None
    date : datetime |None = None
    notes : str | None = None

class personalExpenseResponse(BaseModel):
    id : UUID
    user_id : UUID
    group_id : UUID | None = None
    group_expense_id: UUID | None = None
    title : str 
    amount : Decimal
    category : str | None = None 
    date : datetime | None = None 
    notes : str | None = None 
    created_at : datetime 

    model_config = {
        "from_attributes": True
    }