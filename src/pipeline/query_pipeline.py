import sys
from src.logger import logging
from src.exceptions import KisanBotException
from src.components.agent import build_agent

def run_query_pipeline(question: str, thread_id: str = ""):
    try:
        logging.info(f"Query pipeline started for {question}")

        agent = build_agent()

        import uuid
        if not thread_id:
            thread_id = str(uuid.uuid4())

        result = agent.invoke(
            {
                "question": question,
                "chunks": [],
                "answer": "",
                "chat_history": []
            },
            config = {"configurable": {"thread_id": thread_id}}
        )
        logging.info("Query pipeline completed successfully")
        return{
            "question": question,
            "answer": result['answer'],
            "thread_id":thread_id
        }

    except Exception as e:
        logging.error(f'query pipeline failed: {e}')
        raise KisanBotException(e,sys)
    

if __name__ == "__main__":
    response = run_query_pipeline("how to increase wheat yield?")
    print(f"Answer: {response['answer']}")
    print(f"Thread ID: {response['thread_id']}")