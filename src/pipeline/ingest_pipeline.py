import sys
from src.logger import logging
from src.exceptions import KisanBotException
from src.components.data_ingestion import ingest_data
from src.components.data_transformation import transform_data
from src.components.vectorstore_builder import build_vectorstore


def run_ingestion_pipeline():
    try: 
        logging.info("="*50)
        logging.info("starting KisanBot ingestion pipeline")

        logging.info("step 1/3 data ingestion")
        ingest_data()

        logging.info("step 2/3 data transformation")
        chunks = transform_data()

        logging.info("step 3/3 building vectorstore")
        build_vectorstore(chunks)

        logging.info("Ingestion pipeline completed successfully")
        logging.info("=" * 50)

    except Exception as e:
        logging.error(f"pipeline failed : {e}")
        raise KisanBotException(e,sys)
    
if __name__ == "__main__":
    run_ingestion_pipeline()