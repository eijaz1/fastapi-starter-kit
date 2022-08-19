from fastapi import APIRouter, Depends, status, HTTPException
from typing import List, Optional
from sqlalchemy.orm import Session
from app import schemas, models, oauth2
from app import database
from app.auth.utils import hash, verify
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from app.oauth2 import create_access_token, verify_access_token
from datetime import timedelta
import shortuuid

get_db = database.get_db

router = APIRouter(
    prefix='/users',
    tags = ['Users']
)

@router.post('/create', response_model=schemas.UserShow, status_code=status.HTTP_201_CREATED)
def create_user(request: schemas.UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(email=request.email, password=hash(request.password), id=shortuuid.uuid())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('', response_model=List[schemas.UserShow], status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users

@router.get('/{id}', response_model=schemas.UserShow, status_code=status.HTTP_200_OK)
def get_user(db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter_by(id=current_user.id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'User with id {current_user.id} is not found')
    return user

@router.put('/{id}', response_model=schemas.UserShow, status_code=status.HTTP_202_ACCEPTED)
def update_user(id, request: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    print(f' current user is {current_user}')
    user_query = db.query(models.User).filter_by(id=id)
    user = user_query.first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'User with id {id} is not found')
    
    user_query.update(request.dict(), synchronize_session=False)
    db.commit()
    return user_query.first()

@router.patch('/update_password', response_model=schemas.UserShow, status_code=status.HTTP_202_ACCEPTED)
def update_password(request: schemas.UserUpdatePassword, db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    print(request.dict())
    user_query = db.query(models.User).filter_by(id=current_user.id)
    user = user_query.first()

    if not verify(request.current_password, user.password):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, 
        detail=f'Current password is incorrect')

    new_password_dict = {'password': hash(request.new_password)}
    # new_password = 'password': hash(request.new_password)
    user_query.update(new_password_dict, synchronize_session=False)

    db.commit()
    return user_query.first()


@router.patch('/update_forgotten_password', response_model=schemas.UserShow, status_code=status.HTTP_202_ACCEPTED)
def update_forgotten_password(request: schemas.UserUpdateForgottenPassword, db: Session = Depends(get_db)):
    try:
        user_id = verify_access_token(request.token).id
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=f'Invalid token')
        
    user_query = db.query(models.User).filter_by(id=user_id)
    if not user_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'User with id {user_id} is not found')

    new_password_dict = {'password': hash(request.new_password)}
    user_query.update(new_password_dict, synchronize_session=False)

    db.commit()
    return user_query.first()

#check fastapi_mail docs for config settings
conf = ConnectionConfig(
    MAIL_USERNAME = "test@gmail.com",
    MAIL_PASSWORD = "password",
    MAIL_FROM = "test@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

@router.get('/send_forgot_password_email/{email}', status_code=status.HTTP_200_OK)
async def send_forgot_password_email(email, db: Session = Depends(get_db)):
    print(email)
    user = db.query(models.User).filter_by(email=email).first()
    ACCESS_TOKEN_EXPIRE_MINUTES = 15
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'id': user.id}, expires_delta=access_token_expires)

    html = """
    <p>Use this token to reset your password. token: {access_token}</p> 
    """.format(access_token=access_token)

    message = MessageSchema(
        subject="Forgotten password",
        recipients=[email],
        body=html,
        subtype="html"
    )
    fast_mail = FastMail(conf)
    await fast_mail.send_message(message)

    return {'message': f'email sent to {email}'}
