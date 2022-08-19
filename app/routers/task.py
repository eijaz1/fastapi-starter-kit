from fastapi import APIRouter, Depends, status, HTTPException, Header
from typing import List
from sqlalchemy.orm import Session
from app import schemas, models, oauth2
from app import database
import shortuuid

get_db = database.get_db

router = APIRouter(
    prefix='/tasks',
    tags = ['Tasks']
)

@router.post('/create', response_model=schemas.TaskShow, status_code=status.HTTP_201_CREATED)
def create_task(request: schemas.TaskCreate, db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    new_task = models.Task(**request.dict(), user_id=current_user.id, id=shortuuid.uuid())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get('/{id}', response_model=schemas.TaskShow, status_code=status.HTTP_200_OK)
def get_task(id: int, db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter_by(id=id, user_id=current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'Task with id {id} is not found')
    return task

@router.get('', response_model=List[schemas.TaskShow], status_code=status.HTTP_200_OK)
def get_tasks(db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    tasks = db.query(models.Task).filter_by(user_id=current_user.id).all()
    return tasks

@router.put('/{id}', response_model=schemas.TaskShow, status_code=status.HTTP_202_ACCEPTED)
def update_task(id, request: schemas.TaskUpdate, db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    task_query = db.query(models.Task).filter_by(id=id, user_id=current_user.id)

    if not task_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f'Task with id {id} is not found')
    
    task_query.update(request.dict(), synchronize_session=False)
    db.commit()
    return task_query.first()

@router.delete('/{id}')
def delete_task(publicId: str, db: Session = Depends(get_db), current_user: schemas.UserShow = Depends(oauth2.get_current_user)):
    task_query = db.query(models.Task).filter_by(id=id, user_id=current_user.id)

    if not task_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'task with id {id} does not exist')

    task_query.delete(synchronize_session=False)
    db.commit()
    return {'detail': f'Task with id {id} deleted'}