import sqlite3
import pandas as pd
import numpy as np
import json
from copy import deepcopy

with sqlite3.connect("ng_message_ai_v2.db") as conn:
    raw_df = pd.read_sql_query("select * from messages", conn)
    
    
def create_json_data(df):
    jsons = []
    for msg in df['ai_message']:
        try:
            jsons.append(json.loads(msg))        
        except:
            jsons.append(None)
    df['json_data'] = jsons
    return df

def remove_invalid(df):
    return df[df['json_data'].notnull()].copy()

def correct_dtype(df):
    def _correct(x):
        tmp = deepcopy(x)
        
        if tmp['primary_category'] is None:
            tmp['primary_category'] = []
            
        if tmp['secondary_category'] is None:
            tmp['secondary_category'] = []
        
        if isinstance(tmp['primary_category'], str):
            tmp['primary_category'] = [tmp['primary_category']]
        if isinstance(tmp['secondary_category'], str):
            tmp['secondary_category'] = [tmp['secondary_category']]
        if isinstance(tmp['entities'], str):
            tmp['entities'] = [tmp['entities']]
            
        move_categories = ['Loan Service', 'Job and Recruitment', 'Entertainment']
        for c in move_categories:
            if c in tmp['primary_category']:
                tmp['primary_category'].remove(c)
                tmp['secondary_category'].append(c)

        tmp['primary_category'] = list(set(tmp['primary_category']))
        tmp['secondary_category'] = list(set(tmp['secondary_category']))
        tmp['entities'] = list(set(tmp['entities']))    
               
        return tmp
    df['json_data'] = df['json_data'].apply(_correct)
    return df

allowed_primaries = ['Advertisement',
 'Transaction',
 'Notification',
 'Reminder',
 'Invitation',
 'Personal',
 'Verification',
 'Subscription',
 'Alert',
 'Support',
 'Survey',
 'Spam']

def extract_primary(df):
    def _extract(x):
        # extract primary category out, loop over all categories
        cats = [c if c in allowed_primaries else 'Others' for c in x['primary_category']]
        return list(set(cats))
    df['primary_category'] = df['json_data'].apply(_extract)
    return df

merged_categories = {
    'Loan Service':['Loan Service'],
    'Banking and Finance': ['Investment','Banking and Finance', 'Business and Finance', 'Finance and Banking', 'Personal Finance', 'Financial Services', 'Finance'],
    'Education': ['Education'],
    'Telecom': ['Telecom'],
    'Government and Public Services': ['Politics','Government and Public Services'],
    'Retail': ['Retail'],
    'Healthcare': ['Healthcare'],
    'Social Networking': ['Social Networking'],
    'Religious': ['Religious', 'Religion', 'Religion and Spirituality', 'Religious Organization', 'Spiritual', 'Spiritual Services'],
    'Non-Profit': ['Non-Profit'],
    'Entertainment': ['Gaming','Photography','Entertainment', 'Media and Entertainment', 'Music', 'Broadcasting'],
    'Travel and Hospitality': ['Travel and Hospitality', 'Hospitality', 'Transport and Hospitality', 'Event and Hospitality'],
    'Job and Recruitment': ['Job and Recruitment', 'Employment'],
    'Utilities': ['Oil and Gas','Utilities', 'Energy and Utilities', 'Energy'],
    'Technology': ['Technology', 'Mobile App'],
    'Real Estate': ['Real Estate', 'Construction', 'Home Services', 'Construction and Real Estate', 'Construction and Building', 'Construction and Engineering'],
    'Food and Dining': ['Food and Dining'],
    'Fashion and Beauty': ['Fashion and Beauty', 'Beauty and Fashion', 'Beauty and Spa', 'Beauty and Skincare'],
    'Gambling': ['Gambling', 'Gambling and Betting', 'Gambling and Lottery', 'Lottery and Gaming'],
    'Automotive': ['Automotive'],
    'Sports': ['Sports'],
    'Insurance': ['Insurance', 'Legal and Insurance'],
    'Business': ['Entrepreneurship','Market Research','Business', 'Business and Networking', 'Business and Marketing', 'Business and Professional Services', 'Business and Entrepreneurship', 'Business and Consulting', 'Business Directory', 'Business and Management', 'Business and Professional'],
    'Logistics': ['Logistics', 'Logistics and Delivery', 'Logistics and Shipping', 'Delivery'],
    'News and Media': ['News and Media'],
    'Transportation': ['Transportation'],
    'Agriculture': ['Agriculture', 'Agriculture and Farming'],
    'Events': ['Event Management' ,'Networking and Events' ,'Event', 'Event Planning', 'Event and Wedding Planning', 'Event and Conference', 'Event Planning and Rentals', 'Event and Ticketing', 'Event Planning and Services'],
    'Others': ['Marketing and Advertising', 'Advertising and Marketing', 'Advertisement','Support','Survey','Cryptocurrency','Security', 'Unknown', 'None', 'N/A', 'Verification', 'Corporate', 'Alcohol and Beverages', 'Printing and Publishing', 'Pet Care', 'Personal Care', 'Transaction', 'Safety', 'Notification', 'Customer Service', 'Training', 'Printing and Press', 'Consulting', 'Research and Survey', 'Research', 'Crypto Trading', 'Greeting', 'Wedding Services', 'Alert', 'Art and Culture', 'Direct Selling', 'Event and Wedding Planning', 'Spam', 'Reminder', 'Wedding and Events', 'Event Planning and Rentals', 'Publishing', 'Fitness', 'Cleaning Services', 'Workspace Booking', 'Multi-Level Marketing', 'Holiday Greetings', 'Arts and Culture', 'Environment', 'Music', 'Ticket Sales', 'Mining', 'Household Products', 'Seasonal Greetings']
}

merge_rules = {cat:k for k,v in merged_categories.items() for cat in v}



def extract_secondary(df):
    def normalize_secondary_category(x):
        normalized = []
        for cat in x['secondary_category']:
            if cat in merge_rules.keys():
                normalized.append(merge_rules[cat])
            else:
                normalized.append(cat)
        return list(set(normalized))
    df['secondary_category'] = df['json_data'].apply(normalize_secondary_category)
    return df
    
df = raw_df.pipe(create_json_data).pipe(remove_invalid).pipe(correct_dtype)
df.pipe(extract_primary).pipe(extract_secondary)

category_df = df[['phone','primary_category','secondary_category']].copy()

from dataclasses import dataclass

@dataclass
class CategoryVectorizer:
    
    categories:list
    prefix :str= 'func_'
    
    def __post_init__(self):
        
        self.category2id = {c:i for i,c in enumerate(self.categories)}
        self.id2category = {v:k for k,v in self.category2id.items()}
        self.N = len(self.categories)
        
    def __call__(self, df, col) -> pd.DataFrame:
        
        columns = [self.prefix + self.id2category[i] for i in range(self.N)]
        
        vecs = []
        for c_list  in df[col].values:
            vec = np.zeros(self.N)
            ids = [self.category2id[c] for c in c_list]
            vec[ids] = 1
            vecs.append(vec)
        res = pd.DataFrame(np.array(vecs), columns = columns) 
        res.columns = [col.replace(" ","_")for col in res.columns]
        return res
    
primary_category_names = list({c for pl in category_df.primary_category.values for c in pl})
secondary_category_names = list({c for pl in category_df.secondary_category.values for c in pl})

primary_vectorizer = CategoryVectorizer(primary_category_names, prefix='func_')
secondary_vectorizer = CategoryVectorizer(secondary_category_names, prefix='content_')

primary_1hot_df = primary_vectorizer(category_df, 'primary_category')

primary_1hot_df['phone'] = category_df['phone'].tolist()
primary_1hot_df.set_index('phone', inplace=True)

secondary_1hot_df = secondary_vectorizer(category_df, 'secondary_category')

secondary_1hot_df['phone'] = category_df['phone'].tolist()
secondary_1hot_df.set_index('phone', inplace=True)


OUTPUT_DB = "ng_message_ai_v2.db"

with sqlite3.connect(OUTPUT_DB) as conn:
    primary_1hot_df.to_sql("message_primary", conn, if_exists = 'replace')
        
with sqlite3.connect(OUTPUT_DB) as conn:
    secondary_1hot_df.to_sql("message_secondary", conn, if_exists = 'replace')