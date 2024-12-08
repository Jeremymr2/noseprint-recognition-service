from sqlalchemy.orm import Session
from app.db.models import Pets, Pet_Images
from fastapi import HTTPException

# CRUD PET
def create_pet(db: Session, user_id: str, name: str, age: str, sex: bool
               , status: bool, breed_id: int, description: str, has_vaccinated: bool, has_medically_conditioned: bool) -> Pets:
    db_pet = Pets(user_id=user_id, name=name, age=age, sex=sex, status= status,
                  breed_id=breed_id, description=description, has_vaccinated=has_vaccinated, has_medically_conditioned=has_medically_conditioned)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

def get_pet(db: Session, pet_id: str) -> Pets:
    return db.query(Pets).filter(Pets.id == pet_id).first()

def update_pet(db: Session, pet_id: str, user_id: str, name: str, age: str, sex: bool
               , status: bool, breed_id: int, description: str, has_vaccinated: bool, has_medically_conditioned: bool) -> Pets:
    db_pet = get_pet(db, pet_id)
    db_pet.user_id = user_id
    db_pet.name = name
    db_pet.age = age
    db_pet.sex = sex
    db_pet.status = status
    db_pet.breed_id = breed_id
    db_pet.description = description
    db_pet.has_vaccinated = has_vaccinated
    db_pet.has_medically_conditioned = has_medically_conditioned
    db.commit()
    db.refresh(db_pet)
    return db_pet

def delete_pet(db: Session, pet_id: str) -> None:
    db.query(Pets).filter(Pets.id == pet_id).first().delete()
    db.commit()

def get_pets_by_user(db: Session, user_id: str) -> list[dict]:
    # query user's pets
    pets = (
        db.query(Pets)
        .filter(Pets.user_id == user_id)
        .all()
    )

    if not pets:
        raise HTTPException(status_code=404, detail=f"No pets were found for the user with ID {user_id}")

    response = []

    for pet in pets:
        # query first image associated with this pet
        image_pet = (
            db.query(Pet_Images)
            .filter(Pet_Images.pet_id == pet.id, Pet_Images.image_type == True) # profile image
            .first()
        )

        response.append({
            "id": pet.id,
            "name": pet.name,
            "age": pet.age,
            "sex": pet.sex,
            "status": pet.status,
            "description": pet.description,
            "breed_id": pet.breed_id,
            "has_vaccinated": pet.has_vaccinated,
            "has_medically_conditioned": pet.has_medically_conditioned,
            "created_at": pet.created_at,
            "profile_image_url": image_pet.image_url if image_pet else None,
        })

    return response