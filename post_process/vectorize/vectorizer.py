import pandas as pd
import numpy as np
from dataclasses import dataclass
import random
import sqlite3

INPUT_FILE = "normalized.feather"
OUTPUT_DB = "ng_message_ai.db"


@dataclass
class PrimaryCategoryVectorizer:
    
    prefix :str= 'func_'
    
    def __post_init__(self):

        self.primary_category = {'Advertisement','Alert','Invitation','Notification',
                                 'Other','Personal','Reminder','Spam','Subscription',
                                 'Support','Survey','Transaction','Verification'}
        
        self.category2id = {c:i for i,c in enumerate(list(self.primary_category))}
        self.id2category = {v:k for k,v in self.category2id.items()}
        self.N = len(self.primary_category)
        
    def __call__(self, df) -> pd.DataFrame:
        
        columns = [self.prefix + self.id2category[i] for i in range(self.N)]
        
        vecs = []
        for c_list  in df.primary_category.values:
            vec = np.zeros(self.N)
            ids = [self.category2id[c] for c in c_list]
            vec[ids] = 1
            vecs.append(vec)
        return pd.DataFrame(np.array(vecs), columns = columns)     


@dataclass
class SecondaryCategoryVectorizer:
    
    prefix: str = 'content_'


    def __post_init__(self):
        self.secondary_categories = {
             'Agriculture',
             'Automotive',
             'Banking and Finance',
             'Business and Industry',
             'Education',
             'Entertainment',
             'Event',
             'Fashion and Beauty',
             'Food and Dining',
             'Gambling',
             'Gaming',
             'Government and Public Services',
             'Healthcare',
             'Insurance',
             'Job and Recruitment',
             'Loan Service',
             'Logistics',
             'Non-Profit',
             'Other',
             'Personal',
             'Real Estate',
             'Religion',
             'Retail',
             'Social Networking',
             'Sports',
             'Technology',
             'Telecom',
             'Travel and Hospitality',
             'Utilities'
        }
        
        self.category2id = {c:i for i,c in enumerate(list(self.secondary_categories))}
        self.id2category = {v:k for k,v in self.category2id.items()}
        self.N = len(self.category2id)
        
        
    def __call__(self,df) -> pd.DataFrame:
        
        columns = [self.prefix + self.id2category[i] for i in range(self.N)]
        
        categories = df.secondary_category.apply(lambda x:self.category2id[x]).values
        return pd.DataFrame(np.eye(self.N)[categories], columns = columns)     

def vectorize_and_validate():
    phone_stats = pd.read_feather(INPUT_FILE)

    print("Creating primary category one hot matrix")
    pc = PrimaryCategoryVectorizer()
    pc_1hot = pc(phone_stats)

    print("Performing sanity check")
    revert_categories = pc_1hot.apply(lambda x: [pc.id2category[ix] for ix in np.where(x == 1)[0]], axis = 1).values
    actually_categories = phone_stats['primary_category']
    assert all([set(r) == set(a) for r,a in zip(revert_categories, actually_categories)])


    print("Primary Category Check Samples")
    for _ in range(50):
        idx = random.randint(0, len(phone_stats))
        print(revert_categories[idx], "----" ,actually_categories[idx])

    print("\n\nCreating secondary category one hot matrix")
    sc = SecondaryCategoryVectorizer()
    sc_1hot = sc(phone_stats)

    print("Performing sanity check")
    revert_categories = sc_1hot.apply(lambda x: sc.id2category[np.where(x==1)[0][0]], axis = 1)
    actually_categories = phone_stats['secondary_category']
    assert all( revert_categories== actually_categories)


    print("Secondary Category Check Samples")
    for _ in range(50):
        idx = random.randint(0, len(phone_stats))
        print(revert_categories[idx], "----" ,actually_categories[idx])
        
    return phone_stats, pc_1hot, sc_1hot


def to_database():
    phone_stats, pc_1hot, sc_1hot = vectorize_and_validate()
    
    with sqlite3.connect(OUTPUT_DB) as conn:
        primary = pd.concat([phone_stats[['phone']], pc_1hot], axis= 1)
        primary.columns = [col.replace(" ","_").replace("-","_") for col in primary.columns]
        primary.to_sql("message_primary", conn, if_exists = 'replace', index = False)
        
    with sqlite3.connect(OUTPUT_DB) as conn:
        secondary = pd.concat([phone_stats[['phone']], sc_1hot], axis= 1)
        secondary.columns = [col.replace(" ","_").replace("-","_")  for col in secondary.columns]
        secondary.to_sql("message_secondary", conn, if_exists = 'replace', index = False)
    
    
if __name__ == "__main__":
    
    to_database()