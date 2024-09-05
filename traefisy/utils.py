from sqlalchemy.orm import Session
from db import models


def save_acme_info(db: Session, acme_email: str, cert_dir: str):
    settings = db.query(models.Settings).first()
    if not settings:
        settings = models.Settings(acme_email=acme_email, cert_dir=cert_dir)
        db.add(settings)
    else:
        settings.acme_email = acme_email
        settings.cert_dir = cert_dir
    db.commit()


def get_acme_info(db: Session):
    return db.query(models.Settings).first()


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
