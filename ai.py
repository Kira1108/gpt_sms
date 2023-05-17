from crud import get_unparsed_messages, update_message
from database import get_db
import json
import typer
import time
import logging
from typing import Optional
from message_parser import MessageParser, OpenAIResponse
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("AI")

def next_batch(size =256):
    return get_unparsed_messages(next(get_db()),limit = size)

def gpt_parse(message:str, phone:str, parser:MessageParser) -> OpenAIResponse:
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
    
    update_message(next(get_db()), message.id, **info)


def main(template:Optional[str] = 'keywords'):
    
    parser = MessageParser(template_name = template)
    
    batch_id = 1
    
    while True:
        batch = next_batch(size = 3)
        
        if len(batch) == 0:
            break
        
        logger.info(f"Parsing batch {batch_id}")
        for message in batch:
            resp = gpt_parse(message.message, message.phone, parser)
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
            
            update_message(next(get_db()), message.id, **info)
        time.sleep(3)
        
        batch_id += 1
        
    if batch_id == 1:
        logger.info("No unparsed messages.")
        
if __name__ == "__main__":
    typer.run(main)