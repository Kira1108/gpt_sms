from typing import Protocol, List
import sqlite3
import pandas as pd
import json
from dataclasses import dataclass

class DataFrameTransform(Protocol):
    
    def __call__(self, df:pd.DataFrame) -> pd.DataFrame:
        ...

# =========== Extract Data =============
def load_raw_data(db_name:str):
    """Load data from database"""
    with sqlite3.connect(db_name) as conn:
        return pd.read_sql_query("SELECT * FROM messages where ai_message is not null", conn)

    
# =========== Transform Data =============
def filter_validate(df):  
    """Filter out non-json compatible records"""
    jsons = []
    for x in df['ai_message']:
        try:
            jsons.append(json.loads(x))
        except:
            jsons.append(None)
            
    df['result'] = jsons
    df = df[df['result'].notnull()].copy()
    return df


class DataChecker:
    
    @staticmethod
    def check_key(x, key, type_):
        """Check json field type"""
        if isinstance(x, dict) and key in x.keys() and isinstance(x[key], type_):
            return 1
        return 0
    
    def __call__(self, df):
        df['correct_primary'] = df['result'].apply(lambda x: self.check_key(x, 'primary_category',list))
        df['correct_secondary'] = df['result'].apply(lambda x: self.check_key(x, 'secondary_category',str))
        df['correct_keywords'] = df['result'].apply(lambda x: self.check_key(x, 'keywords',list))
        df['correct_sender'] = df['result'].apply(lambda x: self.check_key(x, 'sender',str))
        return df


def filter_data(df):
    """Filter data records"""
    return df[
        (df.correct_primary == 1) &
        (df.correct_secondary == 1) &
        (df.correct_keywords == 1) &
        (df.correct_sender == 1)].copy()
    
def extract_features(df):
    
    """Extract features"""
    df['primary_category'] = df['result'].apply(lambda x: x['primary_category'])
    df['secondary_category'] = df['result'].apply(lambda x: x['secondary_category'])
    df['keywords'] = df['result'].apply(lambda x: x['keywords'])
    df['sender'] = df['result'].apply(lambda x: x['sender'])
    
    return df

def column_selection(df):
    columns = ['phone','message','primary_category','secondary_category','keywords','sender']
    return df[columns].copy()


@dataclass
class TransformPipeline:
    
    transforms:List[DataFrameTransform]
    
    def __call__(self, df):
        for t in self.transforms:
            df = df.pipe(t).copy()
        return df

    
preprocess_pipeline = TransformPipeline([
        filter_validate,
        DataChecker(),
        filter_data,
        extract_features,
        column_selection]
)