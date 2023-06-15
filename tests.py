from mib_messages.prompts import MessagePrompt
from mib_messages.message_parser import MessageParser, OpenAIResponse
from mib_messages.crud import (
    get_unparsed_messages, 
    update_message,
    get_msg_by_id
)

from mib_messages.database import get_db

def test_prompts():
    keywords_prompt = MessagePrompt("keywords").format("Hello World")
    fewshot_prompt = MessagePrompt("fewshot").format("Hello World")
    assert len(keywords_prompt) > 1200
    assert len(fewshot_prompt) > 1800
    
    
def test_message_parser():
    """In a test environment, we don't want to make an API call to OpenAI."""
    msg_parser = MessageParser('fewshot')
    result = msg_parser.parse("Hello World")
    assert isinstance(result, OpenAIResponse)
    assert result.content == "fake content"
    assert result.prompt_tokens == 10
    assert result.completion_tokens == 10
    assert result.total_tokens == 20
    
def test_get_unparsed():
    unparsed = get_unparsed_messages(next(get_db()), 4)
    assert len(unparsed) == 4

def test_update():    
    update_message(
        next(get_db()), 
        1, 
        ai_message = "Hello World", 
        prompt_tokens = 10, 
        completion_tokens = 10, 
        total_tokens = 20,
        ai_json = '{"key",:"fake"}',
        json_compatible= True)
    
    msg = get_msg_by_id(next(get_db()),1)
    assert msg.ai_message == "Hello World"
    assert msg.prompt_tokens == 10
    assert msg.completion_tokens == 10
    assert msg.total_tokens == 20
    assert msg.ai_json == '{"key",:"fake"}'
    assert msg.json_compatible == True

    