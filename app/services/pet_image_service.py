import os
import boto3
from typing import List
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.db.models import Pet_Images
from dotenv import load_dotenv
import numpy as np
import cv2
import requests

from app.services.cropper_service import detect_nose_to_dict, crop_nose
from app.services.noseprint_detector_service import noseprint_detector_service

load_dotenv()

BUCKET_NAME = os.getenv("BUCKET_NAME")
REGION_NAME = os.getenv("REGION_NAME")
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Connection S3
s3 = boto3.client('s3',
                  region_name= REGION_NAME,
                  aws_access_key_id=aws_access_key_id,
                  aws_secret_access_key=aws_secret_access_key)


# CRUD Pet_Images
def create_pet_image(db: Session, pet_id: str, file: UploadFile, image_type: bool) -> Pet_Images:
    dir_name = "profile" if image_type else "nose"
    file_key = f"{pet_id}/{dir_name}/{file.filename}"

    # Upload image to s3
    s3.upload_fileobj(
        file.file,
        BUCKET_NAME,
        file_key,
        ExtraArgs={"ContentType": file.content_type, 'ACL': 'public-read'}
    )
    image_url = f"https://{BUCKET_NAME}.s3.{REGION_NAME}.amazonaws.com/{file_key}"
    db_pet_images = Pet_Images(pet_id=pet_id, image_url=image_url, image_type=image_type)
    db.add(db_pet_images)
    db.commit()
    db.refresh(db_pet_images)
    return db_pet_images

def get_pet_images(db: Session, pet_images_id: int) -> Pet_Images:
    # Search image by id
    pet_image = db.query(Pet_Images).filter(Pet_Images.id == pet_images_id).first()
    if not pet_image:
        raise HTTPException(status_code=404, detail=f"No image found with ID: {pet_images_id}")
    return pet_image

def update_pet_images(db: Session, pet_images_id: int, url_imagen: str, image_type: bool) -> Pet_Images:
    db_pet_images = get_pet_images(db, pet_images_id)
    db_pet_images.image_url = url_imagen
    db_pet_images.image_type = image_type
    db.commit()
    db.refresh(db_pet_images)
    return db_pet_images

def delete_pet_images(db: Session, pet_images_id: int) -> None:
    pet_image = get_pet_images(db, pet_images_id)

    try:
        # Eliminar la imagen del bucket S3
        s3.delete_object(Bucket=BUCKET_NAME, Key=pet_image.image_url)
        print(f"Image removed from S3: {pet_image.image_url}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error deleting image in S3: {str(e)}")

    db.query(Pet_Images).filter(Pet_Images.id == pet_images_id).first().delete()
    db.commit()

def all_pet_images_by_nose(db: Session) -> List[Pet_Images]:
    nose_images = db.query(Pet_Images).filter(Pet_Images.image_type == False).all()
    return nose_images

async def compare_to_all_noseprint(db: Session, img_params):
    global url
    umbral = 0
    best = 0
    # fetch all the pet_images of noses
    bd_pet_images_by_nose = all_pet_images_by_nose(db)

    # urls
    for pet_image in bd_pet_images_by_nose:
        try:
            url = pet_image.image_url
            response = requests.get(url)
            response.raise_for_status()  # Throws an exception if the download fails
            np_url = np.frombuffer(response.content, dtype=np.uint8)
            img_url = cv2.imdecode(np_url, cv2.IMREAD_COLOR)
            result = await noseprint_detector_service(img_params, img_url)
            if result > umbral:
                umbral = result
                best = pet_image
        except requests.exceptions.RequestException as e:
            HTTPException(status_code= 400, detail = f"Error downloading image: {url} - {e}")
        except cv2.error as e:
            HTTPException(status_code= 400, detail = f"Error proccesing image: {url} - {e}")
    if umbral > 0.8:
        return best
    return None

async def predict_noseprint(db: Session, img):
    cords = detect_nose_to_dict(img)
    img_crop = crop_nose(img, cords)
    result = await compare_to_all_noseprint(db, img_crop)
    return result