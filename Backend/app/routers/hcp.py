from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, crud
from .interaction import get_current_user

router = APIRouter(prefix="/hcp", tags=["hcp"])

@router.get("/", response_model=list[schemas.HCPOut])
def list_hcps(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return crud.get_hcps(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.HCPOut)
def create_hcp(
    hcp: schemas.HCPCreate, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return crud.create_hcp(db, hcp)