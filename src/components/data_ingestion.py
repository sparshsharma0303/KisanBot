import pandas as pd
import sys
from datasets import load_dataset
# from langchain.schema import Document
from src.logger import logging
from src.exceptions import KisanBotException

def ingest_data(save_path:str =  "data/raw/kisanbot_corpus.csv"):
    try:
        logging.info('starting data ingestion from Hugging face')
        ds = load_dataset("KisanVaani/agriculture-qa-english-only")
        df = ds["train"].to_pandas()
        df.dropna(inplace = True)
        df.to_csv(save_path, index = False)
        logging.info(f"data saved to {save_path} - {len(df)} rows")
        return df
        
    except Exception as e:
        logging.error(f"ingestion failed: {e}")
        raise KisanBotException(e,sys)

# print(ingest_data())