from datasets import load_dataset
import pandas as pd

def ingest_data(save_path:str =  "data/raw/kisanbot_corpus.csv"):
    ds = load_dataset("KisanVaani/agriculture-qa-english-only")
    df = ds["train"].to_pandas()
    df.dropna(inplace = True)
    df.to_csv(save_path,index = False)
    