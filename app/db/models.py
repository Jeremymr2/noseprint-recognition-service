from sqlmodel import SQLModel, Field
from datetime import datetime
import shortuuid
from typing import Tuple

# TABLE USERS
class Users(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(default_factory=shortuuid.uuid, primary_key=True)
    name: str
    lastname: str
    dni: str = Field(sa_column_kwargs={"unique": True})
    phone: str = Field(sa_column_kwargs={"unique": True})
    email: str = Field(sa_column_kwargs={"unique": True})
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# TABLE BREED
class Breeds(SQLModel, table=True):
    __tablename__ = "breeds"

    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column_kwargs={"unique": True})


# TABLE PET
class Pets(SQLModel, table=True):
    __tablename__ = "pets"

    id: str = Field(default_factory=shortuuid.uuid, primary_key=True)  # UUID corto
    user_id: str = Field(foreign_key="users.id")
    name: str
    age: str
    sex: bool
    status: bool = True  # 1: available | 0: missing
    breed_id: int = Field(foreign_key="breeds.id")
    description: str
    has_vaccinated: bool = True
    has_medically_conditioned: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


# TABLE PET IMAGES (1:PERFIL - 0:NARIZ)
class Pet_Images(SQLModel, table=True):
    __tablename__ = "pet_images"

    id: int = Field(default=None, primary_key=True)
    pet_id: str = Field(foreign_key="pets.id")
    image_url: str
    image_type: bool  # 1: perfil | 0:nariz
    created_at: datetime = Field(default_factory=datetime.utcnow)


# # TABLE EVENT
# class Event(SQLModel, table=True):
#     __tablename__ = "events"
#
#     id: int = Field(default=None, primary_key=True)
#     pet_id: str = Field(foreign_key="mascotas.id")
#     location: Tuple[float,float]
#     is_missing: bool # 1: missing | 0: sighting
#     created_at: datetime = Field(default_factory=datetime.utcnow)