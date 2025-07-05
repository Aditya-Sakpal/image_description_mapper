from pydantic import BaseModel

class ImageUrlRequest(BaseModel):
    image_url: str

class CandidateDescription(BaseModel):
    candidate_description_index: str
    candidate_description: str
    candidate_reasoning: str
    confidence_score: float

class ExpectedOutput(BaseModel):
    matched_description_index: str
    matched_description: str
    reasoning: str
    confidence_score: float
    candidate_descriptions: list[CandidateDescription]