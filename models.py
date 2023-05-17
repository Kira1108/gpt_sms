from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Text, 
    DateTime,
    Boolean
)
from sqlalchemy.sql import func
from database import Base

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=True, comment = "str: phone number or sender name")
    message = Column(Text, nullable=True, comment = "str: message content")
    ai_message = Column(Text, nullable=True, comment = "str: ai response json")
    ai_json = Column(Text,nullable=True, comment = "str: ai response json")
    json_compatible = Column(Boolean, nullable=True, comment = "bool: is ai response json compatible")
    prompt_tokens = Column(Integer, nullable=True, comment = "int: prompt tokens used")
    completion_tokens = Column(Integer, nullable=True, comment = "int: completion tokens used")
    total_tokens = Column(Integer, nullable=True, comment = "int: total tokens used")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
