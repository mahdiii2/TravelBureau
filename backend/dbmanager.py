import os
from uuid import uuid4
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_NAME = os.getenv('DB_NAME', 'travelbureau')

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class HotelContract(Base):
    __tablename__ = 'hotel_contracts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    country_name = Column(String, nullable=False)
    country_code = Column(String, nullable=False)
    hotel_name = Column(String, nullable=False)
    provider_code = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
