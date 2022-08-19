from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, oauth2
from app import database
from sqlalchemy.orm import Session
from datetime import timedelta
from app.auth.utils import verify

router = APIRouter(
    tags=['Auth']
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter_by(email=request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'Invalid credentials')
    
    if not verify(request.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'Invalid credentials (pw)')

    #generate jwt token and return it
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = oauth2.create_access_token(
        data={'id': user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}