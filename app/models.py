# app/models.py

from sqlalchemy import Column, Integer, String, Boolean, Enum
from app.database import Base
import enum

# Define user types
class UserType(str, enum.Enum):
    client = "client"
    ops = "ops"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    user_type = Column(Enum(UserType), nullable=False)
