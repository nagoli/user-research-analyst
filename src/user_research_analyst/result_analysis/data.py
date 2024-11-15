from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Set, Any

class Interview(BaseModel):
    """Represents a single interview with its answers and segments"""
    name: str = Field(..., description="Name of the interviewee")
    segments: List[str] = Field(default_factory=list, description="List of normalized segments")
    answers: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Dictionary mapping question IDs to their answers"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "segments": ["adult", "visually_impaired"],
                "answers": {
                    "Q1": "Very positive experience",
                    "Q2": "Some navigation issues"
                }
            }
        }

class Question(BaseModel):
    """Represents a question of the interview"""
    id: str = Field(..., description="Unique identifier of the question")
    text: str = Field(..., description="Text of the question")
    column_index: int = Field(..., description="Index of the column in the Excel file (0-based)")

class InterviewDataset(BaseModel):
    """Represents a collection of interviews with their questions"""
    questions: List[Question] = Field(..., description="List of questions in column order")
    interviews: List[Interview] = Field(..., description="List of interviews")
    segment_set: Set[str] = Field(
        default_factory=set,
        description="Set of all possible segments in the dataset"
    )

    def __init__(self, **data):
        super().__init__(**data)
        self.calculate_segment_set()

    def calculate_segment_set(self):
        """Initialize segment_set from interviews"""
        self.segment_set = set()
        for interview in self.interviews:
            self.segment_set.update(interview.segments)

    @field_validator('segment_set', mode='before')
    def ensure_set(cls, v):
        return set(v) if v is not None else set()

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "id": "Q1",
                        "text": "What is your experience with the product?",
                        "column_index": 2
                    }
                ],
                "interviews": [
                    {
                        "name": "John Doe",
                        "segments": ["adult", "visually_impaired"],
                        "answers": {
                            "Q1": "Very positive experience",
                            "Q2": "Some navigation issues"
                        }
                    }
                ],
                "segment_set": ["adult", "child", "visually_impaired", "mobility_impaired"]
            }
        }

class SegmentAnswer(BaseModel):
    """Represents an answer for a specific question with summary, quote, and original rough answers"""
    # segment_id: str = Field(..., description="stemmed version of the segment name")
    segment_name: str = Field(..., description="Name of the segment this answer relates to")
    question_id: str = Field(..., description="ID of the question this answer relates to")
    answer_summary: str = Field(..., description="Summary or main point of the answer")
    quote: Optional[str] = Field(None, description="Supporting quote from the raw data")
    rough_answers: List[Optional[str]] = Field(
        default_factory=list,
        description="List of all raw answers for this segment and question"
    )

class SegmentDataset(BaseModel):
    """Represents all segment-related answers organized by question"""
    questions: List[Question] = Field(..., description="List of questions in column order")
    segments: Dict[str, Dict[str, SegmentAnswer]] = Field(
        default_factory=dict,
        description="Dictionary mapping segment names to their answers, organized by question ID"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "id": "Q1",
                        "text": "What is your experience with the product?",
                        "column_index": 2
                    }
                ],
                "segments": {
                    "accessibility": {
                        "Q1": {
                            "segment_name": "accessibility",
                            "question_id": "Q1",
                            "answer_summary": "Generally positive experience",
                            "quote": "Very positive overall, easy to navigate"
                        }
                    }
                }
            }
        }