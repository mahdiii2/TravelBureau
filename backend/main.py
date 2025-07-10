# backend/app/main.py

from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4
from pathlib import Path

# Use explicit relative imports so the app can be started
# either from the project root (``uvicorn backend.main:app``)
# or from within the ``backend`` package itself.
from .database import SessionLocal, engine
from . import models, schemas, crud, util2

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/get-hotel-contracts",
    response_model=list[schemas.HotelContract],
)
def get_hotel_contracts(db: Session = Depends(get_db)):
    return crud.get_hotel_contracts(db)


@app.post(
    "/upload-file",
    response_model=schemas.HotelContractJob,
)
def upload_file(
    country: str = Form(...),
    hotel: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Invalid file type")

    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)

    file_path = uploads_dir / f"{uuid4()}-{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    job = crud.create_contracts_from_file(db, file_path, country, hotel)
    return job


@app.get("/search-countries")
def search_countries(query: str):
    return util.match_country(query)


@app.get("/search-hotels")
def search_hotels(query: str, cityCountry: str, cityCode: str):
    view_state = util.getSeachHotelsCsrfToken()
    data = util.searchHotels(query, view_state, cityCountry, cityCode)
    return {"data": data}


@app.get(
    "/get-hotel-contract-jobs",
    response_model=list[schemas.HotelContractJob],
)
def get_hotel_contract_jobs(db: Session = Depends(get_db)):
    return crud.get_hotel_contract_jobs(db)
