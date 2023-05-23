from __future__ import annotations

from mib_messages.prompts.detailed import DETAILED_PROMPT
from mib_messages.prompts.entity import ENTITY_PROMPT
from mib_messages.prompts.concise import CONCISE_PROMPT
from mib_messages.prompts.keywords import KEYWORDS_PROMPT
from mib_messages.prompts.fewshot import create_default_fewshot_template

from abc import ABC, abstractmethod



TEMPLATES = dict(
    detailed = DETAILED_PROMPT,
    concise = CONCISE_PROMPT,
    entity = ENTITY_PROMPT,
    keywords = KEYWORDS_PROMPT
)

class BaseMessagePrompt(ABC):
    
    @abstractmethod
    def format(self, message:str) -> str:
        ...
        
    def __call__(self, message:str) -> str:
        return self.format(message)
    

class MessagePrompt(BaseMessagePrompt):
    """Get a prompt from one of the template names`detailed`, `concise`, `entity`, `keywords`, `fewshot`"""
    
    def __init__(self, template_name:str, examples:list = None):
        if template_name == 'fewshot':
            self.template = create_default_fewshot_template(examples)     
        else:
            self.template = TEMPLATES.get(template_name)
            if self.template is None:
                raise ValueError(f"Invalid template name: {template_name}")
    
    def format(self, message:str) -> str:
        return self.template.format(message=message)


