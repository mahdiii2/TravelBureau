from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from uuid import uuid4
from pathlib import Path

from .dbmanager import Base, engine, SessionLocal
from . import util

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/contracts")
async def upload_contract(
    country_name: str = Form(...),
    country_code: str = Form(...),
    hotel_name: str = Form(...),
    provider_code: str = Form(...),
    excel: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not excel.filename:
        raise HTTPException(status_code=400, detail="Excel file required")
    if not all([country_name, country_code, hotel_name, provider_code]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    if util.contract_exists(db, provider_code, hotel_name):
        raise HTTPException(status_code=409, detail="Contract already exists")

    uploads = Path("uploads")
    uploads.mkdir(exist_ok=True)
    file_path = uploads / f"{uuid4()}-{excel.filename}"
    with open(file_path, "wb") as f:
        f.write(await excel.read())

    util.createContractHotel(
        db,
        country_name=country_name,
        country_code=country_code,
        hotel_name=hotel_name,
        provider_code=provider_code,
        file_name=str(file_path),
    )

    return {"status": "created"}
