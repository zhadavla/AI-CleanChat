# src/ai_clean_chat_backend/database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func

DATABASE_URL = "sqlite:///./clean_chatdb.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    is_online = Column(Boolean, default=False)

    messages = relationship("Message", back_populates="user")


# Add a new column to the Message model to store harmfulness
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(String, nullable=False)
    is_harmful = Column(Boolean, default=False)  # New column to store harmfulness

    user = relationship("User")


# Create the tables
Base.metadata.create_all(bind=engine)
