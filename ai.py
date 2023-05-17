from crud import get_unparsed_messages, update_message
from database import get_db
import json
import typer
import time
import logging
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("AI")

def next_batch(size =256):
    return get_unparsed_messages(next(get_db()),limit = size)

def gpt_parse(message:str, phone:str) -> dict:
    """TODO: this is going to be an AI message parser, 
    receiving a message and a phone number, and returns a json string
    IF GPT returns valid json -> return a dictionary
    ELSE -> return a dictionary with error message
    """
    return {'message':message, 'phone':phone}


def main():
    batch_id = 1
    
    while True:
        batch = next_batch(size = 3)
        
        if len(batch) == 0:
            break
        
        logger.info(f"Parsing batch {batch_id}")
        for message in batch:
            parsed_result = gpt_parse(message.message, message.phone)
            update_message(next(get_db()), message.id, json.dumps(parsed_result, ensure_ascii=False))
            
        time.sleep(3)
        
        batch_id += 1
        
    if batch_id == 1:
        logger.info("No unparsed messages.")
        
if __name__ == "__main__":
    typer.run(main)