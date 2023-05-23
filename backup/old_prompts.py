from __future__ import annotations
from langchain import PromptTemplate, FewShotPromptTemplate
from dataclasses import dataclass
import json

@dataclass
class MessagePrompt:
    """Get a prompt from one of the template names`detailed`, `concise`, `entity`, `keywords`"""
    
    template_name:str
    
    def __post_init__(self):
        self.template = TEMPLATES.get(self.template_name)
        if self.template is None:
            raise ValueError(f"Invalid template name: {self.template_name}")
        
    def format(self, message:str) -> str:
        return self.template.format(message=message)
    
# ======================================================================================================================================

DETAILED_TEMPLATE= """I want you to act as a SMS service analyst, you classify the messages into categories.
The task is a multi-label classification task(primary_category and secondary_category)
The primary_category focus on the functionality of the message, and the secondary_category focus on the content type(industry, business type, app type) of the message.

The Primary category can be one of the following:
Advertisement: Messages promoting products, services, or events
Notification: General information or updates from apps, services, or systems
Verification: Messages containing codes or links for authentication
Subscription: Messages related to user subscriptions or content updates
Transaction: Messages about financial transactions or account updates
Reminder: Messages reminding users about appointments or events
Alert: Urgent or critical messages requiring immediate action
Survey: Messages requesting user feedback or participation
Support: Messages related to customer support or query resolution
Invitation: Messages inviting users to events or exclusive offers
Personal: Messages for personal communication or non-commercial use
Spam: Unsolicited or unwanted messages

The Secondary category can be an array of the following classes:
Entertainment: Messages from entertainment companies, event organizers, or content providers
Banking and Finance: Messages from banks, financial institutions, or investment firms
Retail: Messages from retail stores, e-commerce platforms, or online marketplaces
Telecom: Messages from telecommunication companies or mobile service providers
Travel and Hospitality: Messages from airlines, travel agencies, hotels, or booking services
Government and Public Services: Messages from government agencies or public service providers
Healthcare: Messages from healthcare providers, clinics, or medical institutions
Education: Messages from educational institutions, schools, or online learning platforms
Social Networking: Messages from social media platforms, networking sites, or online communities
Utilities: Messages from utility service providers, such as electricity, water, or gas companies
News and Media: Messages from news outlets, media organizations, or journalists
Non-Profit: Messages from non-profit organizations or charitable institutions
Technology: Messages from technology companies, software developers, or gadget manufacturers
Automotive: Messages from automotive companies or dealerships
Food and Dining: Messages from restaurants, food delivery services, or catering businesses
Sports: Messages from sports organizations, teams, or event organizers
Fashion and Beauty: Messages from fashion brands, beauty products, or cosmetics companies
Real Estate: Messages from real estate agencies, property developers, or brokers
Legal and Insurance: Messages from law firms, insurance companies, or legal services
Job and Recruitment: Messages related to job offers, career opportunities, or recruitment agencies
Loan Service: Messages from loan service providers, banks offering loan services or related.

You should format your answer in JSON FORMAT with keys being primary_category and secondary_category
The message to be classified is delimited by triple backticks

message = ```{message}```"""

DETAILED_PROMPT = PromptTemplate(input_variables=["message"], template=DETAILED_TEMPLATE)

# ======================================================================================================================================

CONCISE_TEMPLATE= """I want you to act as a SMS service analyst, you classify the messages into categories.
The classification task is a multi-label classification task(primary_category and secondary_category)
The primary_category focus on the functionality of the message, and the secondary_category focus on the content type(industry, business type, app type) of the message.

The Primary category can be one of the following classes:
[Advertisement, Notification, Verification, Subscription, Transaction, Reminder, Alert, Survey, Support, Invitation, Personal, Spam]

The Secondary category can be an array of the following classes:
[Entertainment, Banking and Finance, Retail, Telecom, Travel and Hospitality, Government and Public Services, Healthcare, Education, Social Networking, Utilities, News and Media, Non-Profit, Technology, Automotive, Food and Dining, Sports, Fashion and Beauty, Real Estate, Legal and Insurance, Job and Recruitment, Loan Service]

You should format your answer in JSON FORMAT with keys being primary_category and secondary_category
The message to be classified is delimited by triple backticks

message = ```{message}```
"""

CONCISE_PROMPT = PromptTemplate(input_variables=["message"], template=CONCISE_TEMPLATE)

# ======================================================================================================================================

ENTITY_TEMPLATE = """
I want you to act as a SMS service analyst, you classify the messages into categories and extract named entities from messages.
The classification task is a multi-label classification task(primary_category and secondary_category)
The primary_category focus on the functionality of the message, and the secondary_category focus on the content type(industry, business type, app type) of the message.

The Primary category can be one of the following:
[Advertisement, Notification, Verification, Subscription, Transaction, Reminder, Alert, Survey, Support, Invitation, Personal, Spam]

The Secondary category can be an array of the following classes:
[Entertainment, Banking and Finance, Retail, Telecom, Travel and Hospitality, Government and Public Services, Healthcare, Education, Social Networking, Utilities, News and Media, Non-Profit, Technology, Automotive, Food and Dining, Sports, Fashion and Beauty, Real Estate, Legal and Insurance, Job and Recruitment, Loan Service]

Besides the classification task, you should also extract message sender information.
The sender cand be various, such as a company name, a name of a mobile app, a product of a bank, loan product etc. 

You should format your answer in JSON FORMAT with keys being primary_category, secondary_category and sender
The message to be classified is delimited by triple backticks

message = ```{message}```
"""

ENTITY_PROMPT = PromptTemplate(input_variables=["message"], template=ENTITY_TEMPLATE)

# ======================================================================================================================================

KEYWORDS_TEMPLATE = """
I want you to act as a SMS service analyst, you classify the messages into categories and extract named entities from messages.
The classification task is a multi-label classification task(primary_category and secondary_category)
The primary_category focus on the functionality of the message, and the secondary_category focus on the content type(industry, business type, app type) of the message.

The Primary category can be one of the following:
[Advertisement, Notification, Verification, Subscription, Transaction, Reminder, Alert, Survey, Support, Invitation, Personal, Spam]

The Secondary category can be an array of the following classes:
[Entertainment, Banking and Finance, Retail, Telecom, Travel and Hospitality, Government and Public Services, Healthcare, Education, Social Networking, Utilities, News and Media, Non-Profit, Technology, Automotive, Food and Dining, Sports, Fashion and Beauty, Real Estate, Legal and Insurance, Job and Recruitment, Loan Service]

The sender name, such as a company name, a name of a mobile app, a product of a bank, loan product etc. 

keywords, a list of 5 keywords that are helpful to determined the categories.

You should format your answer in JSON FORMAT with keys being primary_category, secondary_category, sender and keywords
The message to be classified is delimited by triple backticks

message = ```{message}```
"""

KEYWORDS_PROMPT = PromptTemplate(input_variables=["message"], template=KEYWORDS_TEMPLATE)

# ======================================================================================================================================

FEWSHOT_PREFIX = """
I want you to act as a SMS service analyst, you classify the messages into categories and extract named entities from messages.
The classification task is a multi-label classification task(primary_category and secondary_category)
The primary_category focus on the functionality of the message, and the secondary_category focus on the content type(industry, business type, app type) of the message.

The Primary category can be one of the following:
[Advertisement, Notification, Verification, Subscription, Transaction, Reminder, Alert, Survey, Support, Invitation, Personal, Spam]

The Secondary category can be an array of the following classes:
[Entertainment, Banking and Finance, Retail, Telecom, Travel and Hospitality, Government and Public Services, Healthcare, Education, Social Networking, Utilities, News and Media, Non-Profit, Technology, Automotive, Food and Dining, Sports, Fashion and Beauty, Real Estate, Legal and Insurance, Job and Recruitment, Loan Service]

The sender name, such as a company name, a name of a mobile app, a product of a bank, loan product etc. 

keywords, a list of 5 keywords that are helpful to determined the categories.

You should format your answer in JSON FORMAT with keys being primary_category, secondary_category, sender and keywords
"""

EXAMPLE_LIST = json.loads(open("/Users/wanghuan/Projects/gpt_sms/example.json",'r').read())

EXAMPLE_PROMPT = PromptTemplate(
    input_variables=["message",'completion'], 
    template="message: ```{{message}}```\ncompletion: {{completion}}\n",template_format = 'jinja2')

FEWSHOT_SUFFIX = "message:{{message}}\ncompletion:"

FEWSHOT_PROMPT = FewShotPromptTemplate(
    examples=EXAMPLE_LIST,
    example_prompt=EXAMPLE_PROMPT,
    prefix=FEWSHOT_PREFIX,
    suffix=FEWSHOT_SUFFIX,
    input_variables=["message"],
    example_separator="\n\n",
    template_format = 'jinja2'
)

# ======================================================================================================================================
    
TEMPLATES = dict(
    detailed = DETAILED_PROMPT,
    concise = CONCISE_PROMPT,
    entity = ENTITY_PROMPT,
    keywords = KEYWORDS_PROMPT,
    fewshot = FEWSHOT_PROMPT
)

if __name__ == "__main__":
    # prompt = MessagePrompt(template_name="keywords")
    # print(prompt.format("Hello world"))
    
    
    prompt = MessagePrompt(template_name='fewshot')
    print(prompt.format("Hello world"))