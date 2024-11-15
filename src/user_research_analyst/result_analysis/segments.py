from typing import Set, Dict, List, Optional
import json
import openai
from data import InterviewDataset, Interview, SegmentAnswer, SegmentDataset, Question

class SegmentNormalizer:
    """Normalizes segment names using OpenAI's API"""
    def __init__(self, language: str="french"):
        self.client = openai
        self.language = language
        
    def normalize_segment_set(self, segment_set: Set[str]) -> Set[str]:
        """
        Takes all segment lists and creates a normalized set of unique segments
        
        Args:
            segment_set: Set of segments to normalize
            
        Returns:
            Set[str]: Normalized set of unique segments
        """
        prompt = f"""
        Here is a list of segments describing different types of users or conditions:
        {list(segment_set)}

        Create a normalized set of unique segments by:
        1. Correcting spelling mistakes
        2. Standardizing similar terms (e.g., "kid" and "child" should be one term)
        3. Use the {self.language} language
        4. Using singular form
        5. Using lowercase
        6. Removing semantical duplicates and keeping only one instance of each segment
        7. You evaluate the confidence of your answer, it can be low if you are not sure

        You must respond with this exact JSON structure: 
        {{
            "segment_set": list of unique segments
            "confidence": "low" or "medium" or "high"
        }}
        
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            normalized_segments = json.loads(response.choices[0].message.content)
            print (f"Original segments: {segment_set}")
            print (f"Normalized segments: {normalized_segments}")
            if normalized_segments['confidence'] != "high":
                print (f"Low confidence for segment list: {normalized_segments}")
            return set(normalized_segments['segment_set'])
        except Exception as e:
            print(f"Error normalizing segment set: {e}")
            return set()

    def normalize_segment_list(self, segments: List[str], normalized_set: Set[str]) -> List[str]:
        """
        Takes a list of segments and matches them to the normalized set
        using GPT to handle the matching
        """
        prompt = f"""
        Given this list of normalized segments:
        {sorted(list(normalized_set))}

         Match these input segments to the normalized list:
        {segments}

        Use the {self.language} language
        
        For each input segment, you evaluate the semantical proximity with each normalized segment. 
        You must respond with this exact JSON structure: 
        {{
            "matched_segments": list of normalized segments that best match with the input segments
            "unmatched_segments": list of input segments that did not properly match any normalized segment
            "confidence": "low" or "medium" or "high"
        }}
        
       
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            matched_segments = json.loads(response.choices[0].message.content)
            if matched_segments['confidence'] != "high":
                print (f"Low confidence for segment list: {segments} \n Found : {matched_segments}")
            return matched_segments['matched_segments']+matched_segments['unmatched_segments']
        except Exception as e:
            print(f"Error: {str(e)}")
            return segment


def normalize_segments_in_interviewdataset(dataset: InterviewDataset) -> InterviewDataset:
    """
    Normalizes all segments in an InterviewDataset
    
    Args:
        dataset: The dataset to normalize
        
    Returns:
        InterviewDataset: A new dataset with normalized segments
    """
    normalizer = SegmentNormalizer(language="french")
    
    # Normalize the segment set
    normalized_segment_set = normalizer.normalize_segment_set(dataset.segment_set)
    
    # # Create a mapping from old to new segment names
    # segment_mapping = {}
    # for old_segment in dataset.segment_set:
    #     # Find the closest match in the normalized set
    #     # For now, just lowercase and replace spaces with underscores
    #     normalized = old_segment.lower().replace(' ', '_')
    #     if normalized in normalized_segment_set:
    #         segment_mapping[old_segment] = normalized
    
    # Create new interviews with normalized segments
    normalized_interviews = []
    for interview in dataset.interviews:
        normalized_segments = normalizer.normalize_segment_set(interview.segments)  
        
        normalized_interview = Interview(
            name=interview.name,
            segments=normalized_segments,
            answers=interview.answers
        )
        normalized_interviews.append(normalized_interview)
    
    # Create and return the normalized dataset
    normalized_dataset = InterviewDataset(
        questions=dataset.questions,
        interviews=normalized_interviews
    )
    return normalized_dataset   

def create_segment_dataset(interview_dataset: InterviewDataset) -> SegmentDataset:
    """
    Creates a SegmentDataset from an InterviewDataset by grouping answers by segment.
    Uses the normalized segment_set of the InterviewDataset as the source of truth for segments.
    
    Args:
        interview_dataset: The source dataset organized by interview
        
    Returns:
        SegmentDataset: A new dataset organized by segment
    """
    # Initialize the segments dictionary with nested structure
    segments: Dict[str, Dict[str, SegmentAnswer]] = {}
    
    # For each segment in the segment set
    for segment_name in interview_dataset.segment_set:
        segments[segment_name] = {}
        # For each question
        for question in interview_dataset.questions:
            # Collect all answers for this segment and question
            answers = []
            for interview in interview_dataset.interviews:
                if segment_name in interview.segments and question.id in interview.answers:
                    answer = interview.answers[question.id]
                    if answer:
                        answers.append(answer)
            
            # If we have answers, create a SegmentAnswer
            if answers:
                # For now, we use the first answer as the main quote and create a simple summary
                quote = answers[0] if answers else None
                summary = f"Found {len(answers)} relevant answer(s)"
                
                segments[segment_name][question.id] = SegmentAnswer(
                    segment_name=segment_name,
                    question_id=question.id,
                    answer_summary=summary,
                    quote=quote,
                    rough_answers=answers
                )
    
    # Create and return the new SegmentDataset
    return SegmentDataset(
        questions=interview_dataset.questions,
        segments=segments
    )

if __name__ == "__main__":
    
    dataset = InterviewDataset(
        questions=[
            Question(id="Q1", text="Comment avez-vous trouvé l'application ?", column_index=0),
            Question(id="Q2", text="Quelles difficultés avez-vous rencontrées ?", column_index=1),
            Question(id="Q3", text="Comment avez-vous trouvé l'interface utilisateur ?", column_index=2)
        ],  # Add your questions here if needed
        interviews=[
            Interview(
                name="Interview_001",
                segments=["adulte", "aveugle", "mal-voyant"],
                answers={"Q1": "Très positive dans l'ensemble", "Q2": "Quelques problèmes de navigation", "Q3": "Difficulté avec le contraste"}
            ),
            Interview(
                name="Interview_002",
                segments=["enfant", "handicap moteur"],
                answers={"Q1": "Bof pas top ", "Q2": "ca va", "Q3": "joli"}
            ),
            Interview(
                name="Interview_003",
                segments=["jeune", "aveugle", "handicap moteur"],
                answers={"Q1": "cool", "Q2": "aucune", "Q3": "moche"}
            )
        ]
    )
    normalized_dataset = normalize_segments_in_interviewdataset(dataset) if(False) else dataset
    if (False):
        print("Original segments:")
        for interview in dataset.interviews:
            print(f"{interview.name}: {interview.segments}")
        
        print("\nNormalized segments:")
        for interview in normalized_dataset.interviews:
            print(f"{interview.name}: {interview.segments}")


    segment_dataset = create_segment_dataset(normalized_dataset)  
    
    print ("Reponse par segment :   ")  
    for segment in segment_dataset.segments.values():
        for question_id, segment_answer in segment.items():
            print(f"{segment_answer.segment_name} - {question_id}: {segment_answer.rough_answers}")