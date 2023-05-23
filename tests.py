from mib_messages.prompts import MessagePrompt

def test_prompts():
    keywords_prompt = MessagePrompt("keywords").format("Hello World")
    fewshot_prompt = MessagePrompt("fewshot").format("Hello World")
    assert len(keywords_prompt) > 1200
    assert len(fewshot_prompt) > 1800
    
    

