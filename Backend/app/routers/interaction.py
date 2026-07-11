from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import schemas, crud
from ..core.security import decode_access_token
from ..models import Interaction, User
from jose import JWTError

router = APIRouter(prefix="/interaction", tags=["interaction"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user from token - returns default user if no token"""
    if not token:
        # Return default user for testing
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            # Create default user if not exists
            user = User(
                username="default",
                hashed_password="dummy",
                full_name="Default User",
                email="default@example.com"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload is None:
            raise credentials_exception
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

@router.post("/", response_model=schemas.InteractionOut)
def create_interaction(
    interaction: schemas.InteractionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return crud.create_interaction(db, interaction, current_user.id)

@router.put("/{interaction_id}", response_model=schemas.InteractionOut)
def update_interaction(
    interaction_id: int,
    update_data: schemas.InteractionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_interaction = crud.update_interaction(db, interaction_id, update_data)
    if not db_interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return db_interaction

@router.get("/", response_model=List[schemas.InteractionOut])
def list_interactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Interaction).filter(
        Interaction.user_id == current_user.id
    ).offset(skip).limit(limit).all()