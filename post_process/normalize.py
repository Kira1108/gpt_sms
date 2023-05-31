import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)


UNCLEAR_CATEGORY = 'Other'

class StrategyClean(ABC):
    
    """
        IF      [match_fn] then SELECT [match_df]   APPLY [match_apply_fn]
        IF NOT  [match_fn] then SELECT [unmatch_df] APPLY [unmatch_apply_fn(default do nothing)]
    """
    
    @abstractmethod
    def match_fn(self,df) -> pd.Series:
        ...
        
    @abstractmethod
    def match_apply_fn(self, df) -> pd.DataFrame:
        ...
        
    def unmatch_apply_fn(self, df) -> pd.DataFrame:
        return df
    
    def __call__(self, df):
        match = self.match_fn(df)
        unmatch = ~match
        match_df = self.match_apply_fn(df[match].copy())
        unmatch_df = self.unmatch_apply_fn(df[unmatch].copy())
        return pd.concat([match_df, unmatch_df])
    
    
class CleanLoanService(StrategyClean):
    
    """
    If Loan Service appears in primary category, move it to the secondary category.
    And handle exceptions caused by the movement.
    """
    
    def __init__(self, field = "Loan Service"):
        self.field= field
        
        
    def _remove(self,arr):
        arr.remove(self.field)
        
        if len(arr) == 0:
            arr.append(UNCLEAR_CATEGORY)
            
        return arr
    
    def match_fn(self,df):
        return df.primary_category.apply(lambda x:self.field in x)
    
    def match_apply_fn(self, df):
        df.secondary_category = self.field
        df.primary_category = df.primary_category.apply(self._remove)
        return df
    

class CleanNoisyPrimary(StrategyClean):
    
    """Noisy primary categoires should be removed from primary category list.
    IF the list is empty, add a default category for that.
    """
    
    NOISY_PRIMARY = {'Entertainment',
                     'Job and Recruitment',
                     'Education',
                     'Retail',
                     'Blessing',
                     'Healthcare',
                     'Banking and Finance',
                     'App Download',
                     'News',
                     'Social Networking',
                     'Holiday Greetings',
                     'Insurance',
                     'Finance',
                     'Business',
                     'Greeting',
                     'App Promotion',
                     'Government and Public Services',
                     'Donation',
                     'Religious',
                     'Threat'}
    
    def match_fn(self,df):
        return df.primary_category.apply(lambda x:len(set(x).intersection(self.NOISY_PRIMARY)) > 0)
    
    def match_apply_fn(self, df):
        df.primary_category = df.primary_category.apply(lambda x: list(set(x).difference(self.NOISY_PRIMARY)))
        df.primary_category = df.primary_category.apply(lambda x: x if len(x) > 0  else [UNCLEAR_CATEGORY])
        return df
    
SECONDARY_TYPE_REPLACE_DICT = {
 'Religious': 'Religion',
 'Religion and Spirituality': 'Religion',
 'Religious Organization': 'Religion',
 'Religious Services': 'Religion',
 'Religious Organizations': 'Religion',
 'Business and Recruitment': 'Job and Recruitment',
 'Business and Job Recruitment': 'Job and Recruitment',
 'Construction and Real Estate': 'Real Estate',
 'Beauty and Fashion': 'Fashion and Beauty',
 'Gambling and Betting': 'Gambling',
 'Gambling and Lottery': 'Gambling',
 'Gambling and Gaming': 'Gambling',
 'Gambling and Casino': 'Gambling',
 'Business and Finance': 'Banking and Finance',
 'Finance and Banking': 'Banking and Finance',
 'Legal and Insurance': 'Insurance',
 '': UNCLEAR_CATEGORY,
 'News and Media': 'Entertainment',
 'Logistics and Delivery': 'Logistics',
 'Shipping and Logistics': 'Logistics',
 'Business and Networking': 'Business and Industry',
 'Business and Marketing': 'Business and Industry',
 'Business and Entrepreneurship': 'Business and Industry',
 'Business and Professional Services': 'Business and Industry',
 'Business and Partnership': 'Business and Industry',
 'Business and Career': 'Business and Industry',
 'Business and Consulting': 'Business and Industry',
 'Business and Retail': 'Retail',
 'Business and Sales Training': 'Marketing',
 'Business and Launch Events': 'Business and Industry',
 'Business and Event': 'Event',
 'Business and Services': 'Business and Industry',
 'Business and Conference': 'Business and Industry',
 'Business and Sales Promotion': 'Business and Industry',
 'Business and App Type': 'Business and Industry',
 'Business Type: Unknown': 'Business and Industry',
 'Business and Trade Show': 'Business and Industry',
 'Business and Trade': 'Business and Industry',
 'Business and Management': 'Business and Industry',
 'Business and Productivity': 'Business and Industry',
 'Business and Exhibition': 'Business and Industry',
 'Business and Corporate': 'Business and Industry',
 'Business Type': 'Business and Industry',
 'Gaming and Entertainment': 'Gaming',
 'Agriculture and Farming': 'Agriculture',
 'Event Planning': 'Event',
 'Event and Conference': 'Event',
 'Event and Hospitality': 'Event',
 'Event Services': 'Event',
 'Event Planning and Services': 'Event',
 'Corporate Events': 'Event',
 'Exhibition': 'Event',
 'Mobile App': 'Technology',
 'Construction and Manufacturing': 'Manufacturing',
 'Media and Entertainment': 'Entertainment',
 'Marketing and Advertising': 'Marketing',
 'Greeting': 'Personal',
 'Oil and Gas': 'Energy',
 'Survey': 'Research',
 'Market Research': 'Research',
 'Home Security': 'Security',
 'Security Services': 'Security',
 'Security Industry': 'Security',
 'Investment': 'Banking and Finance',
 'Construction and Home Services': 'Construction',
 'Construction and Home Improvement': 'Construction',
 'Nightlife': 'Entertainment',
 'Music': 'Entertainment',
 'Pet Care': 'Pet Services',
 'Fitness and Gym': 'Fitness',
 'Lottery Service': 'Gambling',
 'Lottery': 'Gambling',
 'Cryptocurrency': 'Banking and Finance',
 'Publishing': 'Media and Entertainment',
 'Home Decor': 'Retail',
 'Photography and Printing': 'Entertainment',
 'Printing Services': 'Entertainment',
 'Photography': 'Entertainment',
 'Mining and Metals': 'Mining and Resources',
 'Community': 'Social Networking',
 'Classifieds': 'Retail',
 'Engineering': 'Professional Services',
 'Political Campaign': 'Government and Public Services',
 'Delivery': 'Logistics',
 'Transportation': 'Logistics',
 'Unknown': UNCLEAR_CATEGORY,
 'Marketing': 'Business and Industry',
 'App Type': 'Technology',
 'Manufacturing': 'Business and Industry',
 'Construction': 'Real Estate',
 'Pet Services': 'Retail',
 'Fitness': 'Healthcare',
 'Professional Services': 'Business and Industry',
 'Hospitality': 'Travel and Hospitality',
 'Mining and Resources': 'Industry',
 'Spiritual': 'Religion',
 'Customer Service': 'Services',
 'Media and Entertainment': 'Entertainment',
 'Home Services': 'Retail',
}

@dataclass
class CleanNoisySecondary:
    
    count_thresh:int = 20
    
    
    def call(self, df):
        df.secondary_category = df.secondary_category.replace(SECONDARY_TYPE_REPLACE_DICT)
        cnts = df.secondary_category.value_counts()
        small_categories = {k:UNCLEAR_CATEGORY for k in cnts[cnts < self.count_thresh].index.tolist()}
        df.secondary_category = df.secondary_category.replace(small_categories)
        return df
    
    def __call__(self, df):
        return self.call(df)
        