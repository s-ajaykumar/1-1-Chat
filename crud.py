from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models
import random



def generate_otp():
    return str(random.randint(100000, 999999))


def verify_otp(session: Session, email, otp):
    user = session.query(models.User).filter(models.User.email == email).first()

    if not user:
        return None

    if user.otp_code != otp:
        return None

    if datetime.utcnow() > user.otp_expiry:
        return None

    user.is_verified = True
    user.otp_code = None

    session.commit()

    return user


def get_user_by_email(session: Session, email):
    return session.query(models.User)\
        .filter(models.User.email == email)\
        .first()


def create_user(session: Session, email, username, password_hash):
    otp = generate_otp()

    user = models.User(
        email=email,
        username=username,
        password_hash=password_hash,
        otp_code=otp,
        otp_expiry=datetime.utcnow() + timedelta(minutes=10)
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user, otp




def create_conversation(session: Session, user1_id: int, user2_id: int):
    conversation = models.Conversation()
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    p1 = models.ConversationParticipant(
        conversation_id=conversation.id,
        user_id=user1_id
    )
    p2 = models.ConversationParticipant(
        conversation_id=conversation.id,
        user_id=user2_id
    )

    session.add_all([p1, p2])
    session.commit()

    return conversation


def create_message(session: Session, conversation_id: int, sender_id: int, content: str):
    message = models.Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    return message


def get_messages(session: Session, conversation_id: int):
    return session.query(models.Message)\
        .filter(models.Message.conversation_id == conversation_id)\
        .order_by(models.Message.created_at)\
        .all()


def get_user_conversations(session: Session, user_id: int):
    return session.query(models.ConversationParticipant)\
        .filter(models.ConversationParticipant.user_id == user_id)\
        .all()

