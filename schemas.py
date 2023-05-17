from pydantic import BaseModel

class MessageInputSchema(BaseModel):
    
    phone:str
    message:str
    
    class Config:
        orm_mode = True
        
class MessageDisplay(BaseModel):
    
    id:int
    phone:str
    message:str
    ai_message:str
    created_at:str
    updated_at:str
    
    class Config:
        orm_mode = True
        
if __name__ == "__main__":
    print(MessageInputSchema(phone="123", message="hello world"))