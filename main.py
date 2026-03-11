from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import models
import schemas
import crud
import auth
import email_service

from db import SessionLocal, engine, Base


Base.metadata.create_all(bind=engine)
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/signup")
def signup(data: schemas.SignupRequest, session: Session = Depends(get_db)):
    hashed = auth.hash_password(data.password)
    user, otp = crud.create_user(
        session,
        data.email,
        data.username,
        hashed
    )
    email_service.send_otp_email(data.email, otp)

    return {"message": "OTP sent to email"}


@app.post("/verify-otp")
def verify_otp(data: schemas.VerifyOTP, session: Session = Depends(get_db)):
    user = crud.verify_otp(session, data.email, data.otp)

    if not user:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    return {"message": "Account verified"}


@app.post("/login", response_model=schemas.TokenResponse)
def login(data: schemas.LoginRequest, session: Session = Depends(get_db)):
    user = crud.get_user_by_email(session, data.email)

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not auth.verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Wrong password")

    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Account not verified")

    token = auth.create_access_token({"user_id": user.id})

    return {"access_token": token}


@app.get("/users/by-email/{email}")
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username
    }





@app.post("/users", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, session: Session = Depends(get_db)):
    return crud.create_user(session, user.username)


@app.post("/conversations")
def create_conversation(
    conversation: schemas.ConversationCreate,
    session: Session = Depends(get_db)
):
    return crud.create_conversation(
        session,
        conversation.user1_id,
        conversation.user2_id
    )


@app.post("/messages", response_model=schemas.MessageOut)
def send_message(
    message: schemas.MessageCreate,
    session: Session = Depends(get_db)
):
    return crud.create_message(
        session,
        message.conversation_id,
        message.sender_id,
        message.content
    )


@app.get("/messages/{conversation_id}", response_model=list[schemas.MessageOut])
def get_messages(conversation_id: int, session: Session = Depends(get_db)):
    return crud.get_messages(session, conversation_id)


@app.get("/users/{user_id}/conversations")
def get_user_conversations(user_id: int, session: Session = Depends(get_db)):
    return crud.get_user_conversations(session, user_id)