from sqlalchemy.orm import Session
from traefisy.db import models


def get_routers(db: Session):
    return db.query(models.Router).all()


def is_router_duplicate(db: Session, name: str, domain: str) -> bool:
    """Check if a router with the given name or domain already exists."""

    return db.query(models.Router).filter((models.Router.name == name) | (models.Router.domain == domain)).first() is not None


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


def remove_router(db: Session, identifier: str):
    router = db.query(models.Router).filter(models.Router.id.startswith(identifier)).first()
    if not router:
        router = db.query(models.Router).filter(models.Router.name == identifier).first()

    if router:
        db.delete(router)
        db.commit()
        return True
    return False
