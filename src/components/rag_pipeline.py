import sys
import os
import requests
from dotenv import load_dotenv
from src.logger import logging
from src.exceptions import KisanBotException
from src.components.vectorstore_builder import load_vectorstore
import socket
from groq import Groq
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
client = Groq(api_key = GROQ_API_KEY)


def retrieve_chunks(vectorestore, question:str , k :int = 3):
    try:
        logging.info(f"retriving to {k} chunks for query : {question}")
        chunks = vectorestore.similarity_search(question,k= k )
        logging.info(f"retrived {len(chunks)} chunks")
        return chunks
    except Exception as e:
        logging.error(f"retrival failed {e}")
        raise KisanBotException(e,sys)
    
def generate_answer(question:str, chunks:list):
    try:
        logging.info("building context from the retrived chunks")
        context = "\n\n".join([chunk.page_content for chunk in chunks])
        prompt = f"""You are KisanBot, a helpful agricultural assistant for Indian farmers.
        Use the context below to answer the question. If the answer is not in the context, say "I don't have enough information on this."
        Context:
        {context}

        Question: {question}"""
        logging.info("Calling Groq")
        response = client.chat.completions.create(
            model = "llama-3.1-8b-instant",
            messages = [{"role":"user","content":prompt}],
            temperature = 0.3,
            max_tokens = 300
        )
        answer = response.choices[0].message.content.strip()
        logging.info("answer generated succesfully")
        return answer

    except Exception as e:
        logging.error(f"answer generation failed {e}")
        raise KisanBotException(e,sys)
    

if __name__ == "__main__":
    vs = load_vectorstore()
    question = "how to protect wheat crop from pests?"
    chunks = retrieve_chunks(vs, question)
    answer = generate_answer(question, chunks)
    print(f"Question: {question}")
    print(f"Answer: {answer}")
    