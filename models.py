from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String)

class Lawyer(Base):
    __tablename__ = "lawyers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    specialization = Column(String)

class Case(Base):
    __tablename__ = "cases"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    status = Column(String, default="Open")
    client_id = Column(Integer, ForeignKey("clients.id"))
    lawyer_id = Column(Integer, ForeignKey("lawyers.id"))
    date_created = Column(DateTime, default=datetime.utcnow)
    case_details = Column(Text)  # 🆕 New Column

    client = relationship("Client")
    lawyer = relationship("Lawyer")
