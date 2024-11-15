from openai import OpenAI
from typing import Dict, List
from data import SegmentDataset
import asyncio

async def generate_segment_synthesis(
    segment_name: str,
    answers: Dict[str, List[str]],
    questions: Dict[str, str]
) -> str:
    """
    Generates a synthesis of answers for a specific question and segment.
    
    Args:
        segment_name: The name of the segment
        answers: Dictionary mapping question IDs to their answers
        questions: Dictionary mapping question IDs to their text
        
    Returns:
        str: A synthesis of the answers
    """
    client = OpenAI()
    
    # Format the answers for the prompt
    answers_text = ""
    for question_id, answer_list in answers.items():
        question_text = questions.get(question_id, question_id)
        answers_text += f"\nQuestion: {question_text}\n"
        for i, answer in enumerate(answer_list, 1):
            answers_text += f"Answer {i}: {answer}\n"
    
    prompt = f"""
    Here are answers from users in the "{segment_name}" segment:
    {answers_text}
    
    Please provide a concise synthesis of these answers, highlighting:
    1. Common themes and patterns
    2. Notable unique perspectives
    3. Key insights specific to this segment
    
    Synthesis:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating synthesis: {str(e)}"

if __name__ == "__main__":
    # Example usage
    synthesis = asyncio.run(generate_segment_synthesis(
        segment_name="visually_impaired",
        answers={
            "Q1": ["Very positive overall", "Some navigation issues"],
            "Q2": ["Screen reader works well", "Contrast could be better"]
        },
        questions={
            "Q1": "What is your overall experience?",
            "Q2": "What specific accessibility features did you use?"
        }
    ))
    print(synthesis)