from sqlalchemy.orm import Session
from app.db.models import Breeds

def list_breeds(db: Session):
    return db.query(Breeds).all()
