import sys
import os
from src.logger import logging
from src.exceptions import KisanBotException
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

def build_vectorstore(chunks, save_path: str = "vectorstore/"):
    try:
        logging.info("loading embedding model")
        embeddings = HuggingFaceEmbeddings(
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
        )
        logging.info("building FAISS index from chunks")
        vectorstore = FAISS.from_documents(chunks,embeddings)
        os.makedirs(save_path,exist_ok=True)
        vectorstore.save_local(save_path)
        logging.info(f"FAISS index saved to {save_path}")
        return vectorstore
    except Exception as e :
        logging.error(f"vector store build failed : {e}")
        raise KisanBotException(e,sys)
    
def load_vectorstore(save_path: str = "vectorstore/"):
    try:
        logging.info("loading embedding model")
        embeddings = HuggingFaceEmbeddings(
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
        )
        logging.info(f'loading FAISS index from {save_path}')
        vectorstore = FAISS.load_local(
            save_path,
            embeddings,
            allow_dangerous_deserialization=True # FAISS uses Python's pickle format to save index.pkl, LangChain forces you to explicitly allow this as a safety acknowledgement
        )
        logging.info("FAISS index loaded succesfully")
        return vectorstore
    except Exception as e:
        logging.error("vectorstore loading failed : {e}")
        raise KisanBotException(e,sys)
    

if __name__ == "__main__":
    from src.components.data_transformation import transform_data
    chunks = transform_data()
    vectorstore = build_vectorstore(chunks=chunks)
    print("vectorstore built and saved")
    print("testing load...")
    vs = load_vectorstore()
    result = vs.similarity_search("how to prevent soil erosion", k = 3)
    for r in result:
        print(r.page_content)
        print("----")
