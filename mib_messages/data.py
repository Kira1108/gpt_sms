from mib_messages.database import Base, engine, get_db
from mib_messages.crud import create_message_from_dataframe, delete_all

import pandas as pd
import logging
from typing import Optional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Data")


Base.metadata.create_all(bind=engine)


def create_database(path:str, fmt:Optional[str] = "csv", replace:Optional[bool] = False):
    """Read raw datafile into sqlite database, either csv or feather.
    fmt: file format, csv or feather
    path: path to the file
    """
    
    if fmt == "csv":
        logger.info(f"Reading csv file {path}.")
        df = pd.read_csv(path)
        
    elif fmt == 'feather':
        logger.info(f"Reading feather file {path}.")
        df = pd.read_feather(path)
        
    else:
        raise ValueError("fmt must be csv or feather.")
    
    logger.info("Writing to database.")
    
    if replace:
        answer = input("Are you sure you want to replace the database? (y/n)")
        if answer.lower() == 'y':
            logger.info("Replacing database.")
            delete_all(next(get_db()))
        else:
            logger.info("Aborting.")
            return 

    create_message_from_dataframe(df, if_exists = 'append')
    logger.info("Done~~!")

