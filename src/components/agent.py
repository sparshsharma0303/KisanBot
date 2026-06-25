import sys
from typing import TypedDict, List,Annotated
import operator
import os
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document
from src.logger import logging
from src.exceptions import KisanBotException
from src.components.vectorstore_builder import load_vectorstore
from src.components.rag_pipeline import retrieve_chunks,generate_answer
import uuid
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

class AgentState(TypedDict):
    question : str
    chunks : List[Document]
    answer: str
    chat_history: Annotated[List[dict], operator.add]

def retrive_node(state: AgentState) -> dict:
    try:
        logging.info("Agent node : retrieving chuks")
        question = state['question']
        vectorstore = load_vectorstore()
        chunks = retrieve_chunks(vectorestore= vectorstore, question= question)
        return {"chunks": chunks}
    except Exception as e:
        raise KisanBotException(e,sys)
    
def generate_node(state: AgentState) -> dict:
    try:
        logging.info("agent node : generating answer")
        question = state["question"]
        chunks = state["chunks"]
        chat_history = state.get("chat_history",[])
        answer = generate_answer(question,chunks,chat_history)
        new_history = [
            {"role":"user","content":question},
            {"role": "assistant","content":answer}
        ]
        return {"answer": answer,"chat_history":new_history}
    except Exception as e :
        raise KisanBotException(e,sys)
    
def build_agent():
    try:
        logging.info("building the langraph agent")
        graph = StateGraph(AgentState)

        graph.add_node("retrive", retrive_node)
        graph.add_node("generate", generate_node)

        graph.set_entry_point("retrive")
        graph.add_edge("retrive","generate")
        graph.add_edge("generate",END)
        
        db_path = "artifacts/chat_history.db"
        os.makedirs("artifacts",exist_ok=True)
        conn = sqlite3.connect(db_path, check_same_thread = False)
        memory = SqliteSaver(conn)
        app = graph.compile(checkpointer = memory)

        logging.info("agent compiled succesfully")
        return app
    
    except Exception as e:
        raise KisanBotException(e,sys)
    

if __name__ == "__main__":
    agent = build_agent()
    result = agent.invoke({
        "question": "how to protect wheat crop from pests?",
        "chunks": [],
        "answer": ""
    })
    print(f"question: {result['question']}")
    print(f"Answer: {result['answer']}")