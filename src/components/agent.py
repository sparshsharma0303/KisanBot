import sys
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document
from src.logger import logging
from src.exceptions import KisanBotException
from src.components.vectorstore_builder import load_vectorstore
from src.components.rag_pipeline import retrieve_chunks,generate_answer


class AgentState(TypedDict):
    question : str
    chunks : List[Document]
    answer: str

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
        answer = generate_answer(question,chunks)
        return {"answer": answer}
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

        app = graph.compile()
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