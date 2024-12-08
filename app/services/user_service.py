from sqlalchemy.orm import Session
from app.db.models import Users
from fastapi import HTTPException

# CRUD USER
def create_user(db: Session, name: str, lastname: str, phone: str, dni: str, email: str, password: str) -> Users:
    existing_user = db.query(Users).filter(Users.dni == dni).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="The user with this DNI already exists.")

    db_user = Users(name=name, lastname=lastname, phone=phone, dni=dni, email=email, password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: str) -> Users:
    return db.query(Users).filter(Users.id == user_id).first()

# Method used for login service
def get_user_by_email(db: Session, user_email: str) -> Users:
    return db.query(Users).filter(Users.email == user_email).first()

def update_user(db: Session, user_id: str, name: str, lastname: str,
                phone: str, dni: str, email: str, password: str) -> Users:
    db_user = get_user(db, user_id)
    db_user.name = name
    db_user.lastname = lastname
    db_user.phone = phone
    db_user.dni = dni
    db_user.email = email
    db_user.password = password
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: str) -> None:
    db.query(Users).filter(Users.id == user_id).first().delete()
    db.commit()
