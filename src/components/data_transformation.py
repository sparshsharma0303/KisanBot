import sys
from src.logger import logging
from src.exceptions import KisanBotException
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_raw_data(path:str = "data/raw/kisanbot_corpus.csv"):
    try:
        logging.info("loading the data from raw csv file")
        dataset = pd.read_csv(path)
        return dataset

    except Exception as e:
        logging.error(f"failed: {e}")
        raise KisanBotException(e,sys)
    
def transform_data(csv_path: str = "data/raw/kisanbot_corpus.csv"):
    try:
        logging.info("starting data transformation")
        df = load_raw_data(csv_path)
        df.drop_duplicates(subset=["question", "answers"], inplace=True)
        df["combined"] = "Question: " + df["question"] + "\nAnswer: " + df["answers"]
        documents = [
            Document(
                page_content = row["combined"],
                metadata = {"row": idx}
            )
            for idx, row in df.iterrows()
        ]
        logging.info(f"created {len(documents)} documents")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size = 500,
            chunk_overlap = 50
        )
        chunks = splitter.split_documents(documents)
        logging.info(f"split into {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logging.error(f"failed: {e}")
        raise KisanBotException(e,sys)
    
if __name__ == "__main__":
    chunks = transform_data()
    print(f"total chunks : {len(chunks)}")
    print(chunks[0])
