from sqlalchemy.orm import Session
from . import models, schemas
from uuid import uuid4
import pandas as pd
from pathlib import Path

UPLOAD_DIR = Path('uploads')
UPLOAD_DIR.mkdir(exist_ok=True)


def get_hotel_contracts(db: Session, limit: int = 50):
    return db.query(models.HotelContract).order_by(models.HotelContract.createdAt.desc()).limit(limit).all()


def get_hotel_contract_jobs(db: Session, limit: int = 50):
    return db.query(models.HotelContractJob).order_by(models.HotelContractJob.createdAt.desc()).limit(limit).all()


def create_contracts_from_file(db: Session, file_path: Path, country: str, hotel: str):
    job = models.HotelContractJob(id=uuid4(), state='PENDING', fileUrl=str(file_path), fileName=file_path.name)
    db.add(job)
    df = pd.read_excel(file_path)
    for _, row in df.iterrows():
        queue = models.HotelContractQueue(
            hotelName=hotel,
            category=row.get('Category'),
            currency=row.get('Currency'),
            roomName=row.get('Room Name'),
            numAdults=row.get('Number of Adults'),
            numChildren=row.get('Number of Children'),
            mealPlan=row.get('Meal Plan'),
            name=row.get('Name'),
            basePrice=row.get('Base Price'),
            numAdultsForPrice=row.get('Number of Adults for Price'),
            adultPrice=row.get('Adult Price'),
            numChildrenForPrice=row.get('Number of Children for Price'),
            childPrice=row.get('Child Price'),
            hotelContractJobId=job.id
        )
        db.add(queue)
    db.commit()
    db.refresh(job)
    return job
