from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import models, schemas

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(existing_user, key, value)

    db.commit()
    db.refresh(existing_user)
    return existing_user

@app.delete("/users/{user_id}", response_model=schemas.User)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return user

@app.get("/users/{user_id}/matches", response_model=list[schemas.User])
def find_matching_users(user_id: int, db: Session = Depends(get_db)):
    current_user = db.query(models.User).filter(models.User.id == user_id).first()
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    
    all_users = db.query(models.User).filter(models.User.id != user_id).all()

    
    matching_users = []
    for user in all_users:
        
        if set(current_user.interests).intersection(user.interests):
            matching_users.append(user)

    return matching_users
