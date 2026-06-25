from pydantic import BaseModel
from typing import List

class QuestionRequest(BaseModel):
    question :str
    top_k : int = 3
    thread_id : str = ""

class SourceChunk(BaseModel):
    content : str

class AnswerResponse(BaseModel):
    question : str
    answer : str
    sources : List[SourceChunk]
    thread_id:str