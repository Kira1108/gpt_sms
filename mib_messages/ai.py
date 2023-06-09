from mib_messages.crud import get_unparsed_messages, update_message
from mib_messages.database import get_db
from mib_messages.message_parser import MessageParser
import json
import time
import logging
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("AI")

def next_batch(size =20):
    return get_unparsed_messages(next(get_db()),limit = size)

def gpt_parse(message_id:int, message:str, phone:str, parser:MessageParser) -> bool:
    try:
        msg = f"Sent from {phone}. Message: {message}"
        
        resp = parser.parse(msg)
        
        ai_message = resp.content
        
        try:
            ai_json = json.dumps(resp.content, ensure_ascii=False)
            json_compatible = True
        except:
            ai_json = None
            json_compatible = False
        prompt_tokens = resp.prompt_tokens
        completion_tokens = resp.completion_tokens
        total_tokens = resp.total_tokens
        
        info = dict(
            ai_message = ai_message,
            ai_json = ai_json,
            json_compatible = json_compatible,
            prompt_tokens = prompt_tokens,
            completion_tokens = completion_tokens,
            total_tokens = total_tokens
        )
        
        return update_message(next(get_db()), message_id, **info)
    except Exception as e:
        logger.info("Error parsing message. Don' worry, we'll try again later. OpenAI overload is not a real problem.")
        logger.info(e)
        


def ai_loop(template:Optional[str] = 'keywords',batch:int = 20, limit: int = 100):
    
    # initialize a parser
    parser = MessageParser(template_name = template)
    
    batch_id = 1
    
    message_count = 0
    
    while True:
        
        # fetch a batch of messages
        current_batch = next_batch(size = batch)
        
        if len(current_batch) == 0:
            break
        
        logger.info(f"Parsing batch {batch_id}")
        
        results = []
        with ThreadPoolExecutor(max_workers=batch) as executor:
            
            # parse each message in the batch
            for message in current_batch:
                future = executor.submit(gpt_parse, message.id, message.message, message.phone, parser)
                results.append(future)

                
        message_count += batch
            
        if message_count >= limit:
            logger.info(f"Reached message limit of {limit}.")
            return
        
        time.sleep(0.2)
        
        batch_id += 1
        
    if batch_id == 1:
        logger.info("No unparsed messages.")
        