from user_research_analyst.campaign.question_parsing import parse_questions
from user_research_analyst.transcript.transcript_analysis import analyze_transcript_with_questions
import json
from user_research_analyst.transcript.transcript_builder import process_interview_transcript

#import dotenv
from dotenv import load_dotenv
load_dotenv()



if __name__ == "__main__":
    
    
    
    question_file = "data/questions.txt"
    questions = parse_questions(question_file)
    if (True): 
        print(questions
                     )
    audio_path = "data/fauxinterview.m4a"
    transcript_file = "data/transcript.txt"
    result_file = "data/results.json"
    
    if(False):
        transcript = process_interview_transcript(audio_path)
        #store transcript in a file
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
    
    if(False):
        results = analyze_transcript_with_questions(
            transcript_path=transcript_file,
            questions=questions,
            output_path=result_file
        )
    
  
    
    