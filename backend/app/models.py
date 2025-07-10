from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from uuid import uuid4

from database import Base

class HotelContract(Base):
    __tablename__ = 'hotel_contract'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    hotelName = Column(String)
    category = Column(String)
    currency = Column(String)
    roomName = Column(String)
    numAdults = Column(Integer)
    numChildren = Column(Integer)
    mealPlan = Column(String)
    name = Column(String)
    basePrice = Column(Float)
    numAdultsForPrice = Column(Integer)
    adultPrice = Column(Float)
    numChildrenForPrice = Column(Integer)
    childPrice = Column(Float)
    createdAt = Column(DateTime, server_default=func.now())

class HotelContractJob(Base):
    __tablename__ = 'hotel_contract_job'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    state = Column(String)
    fileUrl = Column(String)
    fileName = Column(String)
    createdAt = Column(DateTime, server_default=func.now())

class HotelContractQueue(Base):
    __tablename__ = 'hotel_contract_queue'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    hotelName = Column(String)
    category = Column(String)
    currency = Column(String)
    roomName = Column(String)
    numAdults = Column(Integer)
    numChildren = Column(Integer)
    mealPlan = Column(String)
    name = Column(String)
    basePrice = Column(Float)
    numAdultsForPrice = Column(Integer)
    adultPrice = Column(Float)
    numChildrenForPrice = Column(Integer)
    childPrice = Column(Float)
    createdAt = Column(DateTime, server_default=func.now())
    isProcessed = Column(Boolean, default=False)
    hotelContractJobId = Column(UUID(as_uuid=True), ForeignKey('hotel_contract_job.id'))
