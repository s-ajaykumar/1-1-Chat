from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    username: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class ConversationCreate(BaseModel):
    user1_id: int
    user2_id: int


class MessageCreate(BaseModel):
    conversation_id: int
    sender_id: int
    content: str


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


class SignupRequest(BaseModel):
    email: EmailStr
    username: str
    password: str


class VerifyOTP(BaseModel):
    email: EmailStr
    otp: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"