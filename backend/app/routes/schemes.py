from fastapi import APIRouter, HTTPException

from app.schemas.scheme import SchemeRecord
from app.database.mongodb import get_database
from app.utils.scheme_data import load_runtime_scheme_seed

router = APIRouter(prefix="/schemes", tags=["schemes"])


@router.get("/{scheme_id}", response_model=SchemeRecord)
def scheme_details(scheme_id: str) -> SchemeRecord:
    scheme = next((item for item in load_runtime_scheme_seed(get_database()).schemes if item.scheme_id == scheme_id), None)
    if scheme is None:
        raise HTTPException(status_code=404, detail="Scheme not found.")
    return scheme