from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    interactions = relationship("Interaction", back_populates="user")

class HCP(Base):
    __tablename__ = "hcps"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    specialty = Column(String, nullable=True)
    hospital = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    interactions = relationship("Interaction", back_populates="hcp")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    interaction_type = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    time = Column(String, nullable=False)
    attendees = Column(Text, nullable=True)
    topics_discussed = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    outcome = Column(Text, nullable=True)
    follow_up_actions = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    hcp = relationship("HCP", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
    materials = relationship("Material", back_populates="interaction", cascade="all, delete-orphan")
    samples = relationship("Sample", back_populates="interaction", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="interaction", cascade="all, delete-orphan")

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    interaction = relationship("Interaction", back_populates="materials")

class Sample(Base):
    __tablename__ = "samples"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, default=1)
    interaction = relationship("Interaction", back_populates="samples")

class FollowUp(Base):
    __tablename__ = "followups"
    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    action = Column(Text, nullable=False)
    due_date = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    interaction = relationship("Interaction", back_populates="followups")