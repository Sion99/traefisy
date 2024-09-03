from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Router(Base):
    __tablename__ = 'routers'

    id = Column(Integer, primary_key=True, index=True)
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
