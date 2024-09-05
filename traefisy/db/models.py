from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, index=True)
    acme_email = Column(String, nullable=False)
    cert_dir = Column(String, nullable=False)


class Router(Base):
    __tablename__ = 'routers'

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    service_name = Column(String, nullable=False)
    service_url = Column(String, nullable=False)
    entrypoints = Column(String, nullable=False)
    tls = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
