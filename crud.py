from sqlalchemy.orm import Session
from sqlalchemy import update
from models import Message
from database import engine


def create_message(db:Session, phone:str, message:str):
    msg = Message(phone=phone, message=message)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def update_message(db:Session, id:int, ai_message:str) -> bool:
    db.execute(
        update(Message).where(Message.id == id).values(ai_message=ai_message)
    )
    db.commit()
    return True

def create_message_from_dataframe(df, if_exists = 'append'):
    
    if not set(['message','phone']).issubset(df.columns):
        raise ValueError("Dataframe must have columns 'message' and 'phone'.")
    
    df[['message','phone']].copy().to_sql(
        Message.__tablename__, 
        con=engine, 
        if_exists=if_exists, 
        index=False)
    return True


def delete_all(db:Session):
    """delete all record from database"""
    db.query(Message).delete()
    db.commit()
    return True


def get_unparsed_messages(db:Session, limit = 256):
    """get all messages that have not been parsed by the AI"""
    return db.query(Message).filter(Message.ai_message == None).limit(limit).all()

