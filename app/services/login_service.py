from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_session

from app.services.user_service import get_user_by_email
from jose import jwt
import os
from dotenv import load_dotenv
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")

def encode_token(payload: dict) -> str:
    token = jwt.encode(payload, os.getenv("KEY_JWT"), algorithm="HS256")
    return token

def decode_token(token: Annotated[str, Depends(oauth2_scheme)] , db: Session = Depends(get_session)) -> dict:
    data = jwt.decode(token, os.getenv("KEY_JWT"), algorithms=["HS256"])
    user = get_user_by_email(db, data["email"])
    logger.info(user)
    return user

def create_token(db: Session, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    db_user = get_user_by_email(db, form_data.username)
    if not db_user or form_data.password != db_user.password:
        return None
    token = encode_token({"id":db_user.id,"email": db_user.email})
    return token

def profile(my_user: Annotated[dict, Depends(decode_token)]):
    return my_user