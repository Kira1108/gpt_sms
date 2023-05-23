from mib_messages.prompts import MessagePrompt
from mib_messages.message_parser import MessageParser, OpenAIResponse

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
