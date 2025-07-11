from sqlalchemy.orm import Session
from .dbmanager import HotelContract

def contract_exists(db: Session, provider_code: str, hotel_name: str) -> bool:
    """Return True if a contract with given identifiers exists."""
    contract = db.query(HotelContract).filter(
        HotelContract.provider_code == provider_code,
        HotelContract.hotel_name == hotel_name,
    ).first()
    return contract is not None

def createContractHotel(
    db: Session,
    country_name: str,
    country_code: str,
    hotel_name: str,
    provider_code: str,
    file_name: str,
):
    contract = HotelContract(
        country_name=country_name,
        country_code=country_code,
        hotel_name=hotel_name,
        provider_code=provider_code,
        file_name=file_name,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract
