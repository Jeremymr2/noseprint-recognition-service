import numpy as np
from fastapi import UploadFile, Depends, APIRouter
from sqlmodel import select, Session
from fastapi.responses import StreamingResponse
from app.services.breed_service import list_breeds
from app.services.cropper_service import detect_nose_to_dict, crop_nose
from app.services.login_service import create_token, decode_token
from typing import Annotated
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
# Import
from app.db.session import get_session
from dotenv import load_dotenv
import cv2
import io
from app.services.pet_image_service import create_pet_image, predict_noseprint, compare_to_all_noseprint
from app.services.pet_service import create_pet, get_pets_by_user, get_pet, update_pet, delete_pet
from app.services.user_service import get_user, create_user, delete_user, update_user

load_dotenv()

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/healthcheck/")
def healthcheck(session: Session = Depends(get_session)):
    try:
        statement = select(1)
        result = session.exec(statement).first()
        if result:
            return {
                "Status": "Ok",
                "version": "1.0",
                "database": "Conexión exitosa"
            }
        else:
            return {
                "Status": "Fail",
                "version": "1.0",
                "database": "No se pudo conectar a la base de datos"
            }
    except Exception as e:
        return {
            "Status": "Error",
            "version": "1.0",
            "database": f"Error de conexión: {str(e)}"
        }

# @app.post("/predict/")
# async def predict(file: UploadFile):
#     return {"filename": file.filename}

# LOGIN
@router.post("/token")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_session)):
    token = create_token(db, form_data)
    if not token:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrecta")
    return {"access_token": token}

@router.get("/user/profile")
def user_profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user

@router.post("/user/pet")
def user_create_pet(name: str, age: str, sex: bool,
                    status: bool, breed_id: int, description: str, has_vaccinated: bool, has_medically_conditioned: bool,
                    my_user: Annotated[dict, Depends(decode_token)], db: Session = Depends(get_session)):
    # id usuario autenticado
    id_autenticado = my_user.id
    if not id_autenticado:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    # Crear la mascota
    db_mascota = create_pet(db, id_autenticado, name, age, sex, status, breed_id, description, has_vaccinated, has_medically_conditioned)
    return db_mascota

@router.get("/pet/user/{user_id}")
def pet_by_user(user_id: str, db: Session = Depends(get_session)):
    db_pet = get_pets_by_user(db, user_id)
    return db_pet

# USERS
@router.post("/user")
def create_user_service(name: str, lastname: str, phone: str, dni: str, email: str, password: str, db:Session = Depends(get_session)):
    try:
        db_user = create_user(db, name, lastname, phone, dni, email, password)
        return db_user
    except HTTPException as e:
        raise e

@router.get("/user/pets")
def list_pet_by_user(my_user: Annotated[dict, Depends(decode_token)],
                     db: Session = Depends(get_session)):
    authenticated_id = my_user.id
    if not authenticated_id:
        raise HTTPException(status_code=401, detail="Not authorized to perform this action")
    try:
        response = get_pets_by_user(db, authenticated_id)
        return response
    except HTTPException as e:
        raise e

@router.get("/breeds")
def list_breeds_service(db: Session = Depends(get_session)):
    db_breeds = list_breeds(db)
    return db_breeds

@router.get("/user/{id}")
def get_user_service(id: str, db:Session = Depends(get_session)):
    db_users = get_user(db, id)
    return db_users

@router.put("/user/{id}")
def update_user_service(user_id: str, name: str, lastname: str, phone: str, dni: str, email: str, password: str, db: Session = Depends(get_session)):
    db_users = update_user(db, user_id, name, lastname, phone, dni, email, password)
    return db_users

@router.delete("/user/{id}")
def delete_user_service(user_id: str, db:Session = Depends(get_session)):
    db_users = delete_user(db, user_id)
    return db_users

# MASCOTAS
@router.post("/pets")
def create_pet_service(user_id: str, name: str, age: str, sexo: bool
               , status: bool, breed_id: int, description: str, has_vacinnated: bool, has_medically_conditioned: bool, db: Session = Depends(get_session)):
    db_pet = create_pet(db, user_id, name, age, sexo, status, breed_id, description, has_vacinnated, has_medically_conditioned)
    return db_pet

@router.get("/pets/{pet_id}")
def get_pet_service(pet_id: str, db:Session = Depends(get_session)):
    db_pet = get_pet(db, pet_id)
    return db_pet

@router.put("/pets/{id}")
def update_pet_service(pet_id:str, user_id: str, name: str, age: str, sex: bool
               , status: bool, breed_id: int, description: str, has_vaccinated: bool, has_medically_conditioned: bool, db: Session = Depends(get_session)):
    db_pet = update_pet(db, pet_id, user_id, name, age, sex, status, breed_id, description, has_vaccinated, has_medically_conditioned)
    return db_pet

@router.delete("/pets/{id}")
def delete_pet_service(pet_id: str, db:Session = Depends(get_session)):
    db_pet = delete_pet(db, pet_id)
    return db_pet

# PET_IMAGES
# @router.post("/pets/image")
# async def upload_pet_image(pet_id: str, file: UploadFile, image_type: bool, db: Session = Depends(get_session)):
#     db_pet_image = create_pet_image(db, pet_id, file, image_type)
#     return db_pet_image

@router.post("/pets/image/profile")
async def upload_pet_image_profile(pet_id: str, file: UploadFile, db: Session = Depends(get_session)):
    db_pet_image = create_pet_image(db, pet_id, file, True)
    return db_pet_image

@router.post("/pets/image/nose")
async def upload_pet_image_nose(pet_id: str, file: UploadFile, db: Session = Depends(get_session)):
    db_pet_image = create_pet_image(db, pet_id, file, False)
    return db_pet_image

# Modelo
# @router.post("/detect/json")
# async def detect_nose_json(file: UploadFile):
#     binary_image = await file.read()
#     response_json = detect_nose_to_json(binary_image)
#     return {"result":response_json}
#
# @router.post("/detect/image")
# async def detect_nose_image(file: UploadFile):
#     binary_image = await file.read()
#     response_image = detect_nose_to_image(binary_image)
#     return Response(content=response_image.getvalue(), media_type="image/jpeg")

@router.post("/predict")
async def predict(file: UploadFile, db: Session = Depends(get_session)):
    img = await file.read()
    # pet = await predict_noseprint(db, image)
    cords = detect_nose_to_dict(img)
    print("type cords",type(cords))
    img_crop = crop_nose(img, cords)
    print("type img_crop",type(img_crop))
    result = await compare_to_all_noseprint(db, img_crop)
    print("type result",type(result))
    return result

@router.post("/noseprint")
async def predict(file: UploadFile):
    img = await file.read()
    # pet = await predict_noseprint(db, image)
    cords = detect_nose_to_dict(img)
    print("type cords",type(cords))
    img_crop = crop_nose(img, cords)
    # Convertir los bytes a un array NumPy
    np_array = np.frombuffer(img, dtype=np.uint8)
    # Decodificar el array NumPy a una imagen
    img_cv = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    # Convertir la imagen recortada a formato JPEG o PNG
    _, img_encoded = cv2.imencode('.jpg', img_crop)  # Puedes usar '.png' si prefieres PNG
    img_bytes = img_encoded.tobytes()

    # Devolver la imagen como respuesta
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/jpeg")

# @app.get("/findpet/{pet_id}")
# def find_pet(pet_id: int):
#     return {"pet_id": pet_id}
