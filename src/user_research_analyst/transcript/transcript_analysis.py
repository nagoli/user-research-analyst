from pydantic import BaseModel, Field
from typing import List, Tuple
from enum import Enum
import json
import os
from openai import OpenAI

class Confidence(str, Enum):
    low = "low"
    medium = "medium" 
    high = "high"

class AnalysisResult(BaseModel):
    question_id: str = Field(..., description="L'identifiant unique de la question")
    found: bool = Field(..., description="Indique si une réponse pertinente a été trouvée")
    answer: str = Field(..., description="La réponse extraite/résumée dans la langue de la question")
    confidence: Confidence = Field(..., description="Niveau de confiance dans la réponse")

class TranscriptAnalyzer:
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI()

    def analyze_question(self, transcript: str, question_text: str, context_instructions: str = "") -> AnalysisResult:
        
        prompt = f"""You must respond with a valid JSON object and nothing else.

        Analyze the following interview transcript to find from the person who is interviewed the answer he gave to this specific question:
        Question: {question_text}

        Transcript:
        {transcript}

        Extract literally the relevant information that answers this question. Do not invent anything. Take into account the following context instructions:
        {context_instructions}
        
        You must respond with this exact JSON structure:
        {{
            "found": boolean,
            "answer": "string with the extracted answer or explanation if not found",
            "confidence": "low" or "medium" or "high"
        }}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            response_text = response.choices[0].message.content
            
            # Debug logging
            print(f"Raw response: {response_text}")
            
            try:
                result = json.loads(response_text)
                return AnalysisResult(**result)
            except json.JSONDecodeError as je:
                return AnalysisResult(
                    question_id=question_id,
                    found=False,
                    answer=f"Error parsing JSON response: {str(je)}",
                    confidence=Confidence.low
                )
                
        except Exception as e:
            return AnalysisResult(
                question_id=question_id,
                found=False,
                answer=f"API Error: {str(e)}",
                confidence=Confidence.low
            )

def analyze_transcript_with_questions(
    transcript_path: str,
    questions: List[Tuple[str, str]],
    output_path: str = "analysis_results.json"
) -> dict:
    """Process transcript and analyze with questions"""
    analyzer = TranscriptAnalyzer()
    
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    results = {}
    for question_tuple in questions:
        result = analyzer.analyze_question(transcript, question_tuple)
        results[result.question_id] = result.model_dump()
        
        # Save intermediate results
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    return results
