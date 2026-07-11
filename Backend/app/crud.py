from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_hcps(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.HCP).offset(skip).limit(limit).all()

def create_hcp(db: Session, hcp: schemas.HCPCreate):
    db_hcp = models.HCP(**hcp.model_dump())
    db.add(db_hcp)
    db.commit()
    db.refresh(db_hcp)
    return db_hcp

def create_interaction(db: Session, interaction: schemas.InteractionCreate, user_id: int):
    data = interaction.model_dump(exclude={'materials', 'samples', 'followups'})
    data['user_id'] = user_id
    db_interaction = models.Interaction(**data)
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)

    for mat in interaction.materials:
        db_mat = models.Material(interaction_id=db_interaction.id, **mat.model_dump())
        db.add(db_mat)
    for samp in interaction.samples:
        db_samp = models.Sample(interaction_id=db_interaction.id, **samp.model_dump())
        db.add(db_samp)
    for fup in interaction.followups:
        db_fup = models.FollowUp(interaction_id=db_interaction.id, **fup.model_dump())
        db.add(db_fup)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

def update_interaction(db: Session, interaction_id: int, update_data: schemas.InteractionUpdate):
    db_interaction = db.query(models.Interaction).filter(models.Interaction.id == interaction_id).first()
    if not db_interaction:
        return None
    for key, value in update_data.model_dump(exclude_unset=True).items():
        if key in ['materials', 'samples', 'followups']:
            continue
        setattr(db_interaction, key, value)
    if update_data.materials is not None:
        db.query(models.Material).filter(models.Material.interaction_id == interaction_id).delete()
        for mat in update_data.materials:
            db_mat = models.Material(interaction_id=interaction_id, **mat.model_dump())
            db.add(db_mat)
    if update_data.samples is not None:
        db.query(models.Sample).filter(models.Sample.interaction_id == interaction_id).delete()
        for samp in update_data.samples:
            db_samp = models.Sample(interaction_id=interaction_id, **samp.model_dump())
            db.add(db_samp)
    if update_data.followups is not None:
        db.query(models.FollowUp).filter(models.FollowUp.interaction_id == interaction_id).delete()
        for fup in update_data.followups:
            db_fup = models.FollowUp(interaction_id=interaction_id, **fup.model_dump())
            db.add(db_fup)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction