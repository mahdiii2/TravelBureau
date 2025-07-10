from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class HotelContractBase(BaseModel):
    hotelName: str | None = None
    category: str | None = None
    currency: str | None = None
    roomName: str | None = None
    numAdults: int | None = None
    numChildren: int | None = None
    mealPlan: str | None = None
    name: str | None = None
    basePrice: float | None = None
    numAdultsForPrice: int | None = None
    adultPrice: float | None = None
    numChildrenForPrice: int | None = None
    childPrice: float | None = None

class HotelContractCreate(HotelContractBase):
    pass

class HotelContract(HotelContractBase):
    id: UUID
    createdAt: datetime

    class Config:
        orm_mode = True

class HotelContractJob(BaseModel):
    id: UUID
    state: str | None = None
    fileUrl: str | None = None
    fileName: str | None = None
    createdAt: datetime

    class Config:
        orm_mode = True
