from parsing import parse_questions
from transcript_analysis import analyze_transcript_with_questions
import json
from transcript import process_interview_transcript

#import dotenv
from dotenv import load_dotenv
load_dotenv()



if __name__ == "__main__":
    
    
    
    question_file = "questions.txt"
    questions = parse_questions(question_file)
  
    audio_path = "fauxinterview.m4a"
    transcript_file = "transcript.txt"
    result_file = "results.json"
    
    if(False):
        transcript = process_interview_transcript(audio_path)
        #store transcript in a file
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
    
    if(True):
        results = analyze_transcript_with_questions(
            transcript_path=transcript_file,
            questions=questions,
            output_path=result_file
        )
    
  
    
    