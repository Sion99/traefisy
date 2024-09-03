from sqlalchemy.orm import Session
from db import models


def add_router(db: Session, name: str, domain: str, service_name: str, service_url: str, entrypoints: str, tls: bool):
    router = models.Router(
        name=name,
        domain=domain,
        service_name=service_name,
        service_url=service_url,
        entrypoints=entrypoints,
        tls=tls
    )
    db.add(router)
    db.commit()
    db.refresh(router)
    return router


def get_routers(db: Session):
    return db.query(models.Router).all()
