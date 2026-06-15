from datasets import load_dataset
import pandas as pd

def ingest_data(save_path:str =  "data/raw/kisanbot_corpus.csv"):
    ds = load_dataset