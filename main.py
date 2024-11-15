from user_research_analyst.campaign.question_parsing import parse_questions
from user_research_analyst.transcript.transcript_builder import process_interview_transcript
from user_research_analyst.transcript.transcript_analysis import analyze_transcript_with_questions
from user_research_analyst.campaign.config import config
from typing import List, Tuple

from dotenv import load_dotenv
load_dotenv()

def process_interview(
    audio_file: str,
    questions: List[Tuple[str, str]],
    do_transcribe_audio: bool = False,
    do_analyze_audio_transcript: bool = False
) -> None:
    """
    Process a single interview from audio file to analysis
    
    Args:
        audio_file: Path to the audio file
        questions: List of (question_id, question_text) tuples
        do_transcribe_audio: Whether to perform transcription step
        do_analyze_audio_transcript: Whether to perform analysis step
    """
    # Create directories if they don't exist
    raw_transcript_dir = config.get_path('raw_transcript_dir')
    structured_transcript_dir = config.get_path('structured_transcript_dir')
    os.makedirs(raw_transcript_dir, exist_ok=True)
    os.makedirs(structured_transcript_dir, exist_ok=True)
    
    # Extract interview name from audio file
    interview_name = os.path.splitext(os.path.basename(audio_file))[0]
    
    # Define output files
    raw_transcript_file = os.path.join(raw_transcript_dir, f"{interview_name}_raw.txt")
    structured_transcript_file = os.path.join(structured_transcript_dir, f"{interview_name}_structured.json")
    
    # Step 1: Generate transcript if requested
    if do_transcribe_audio:
        #do not generate transcript if it already exists
        if os.path.exists(raw_transcript_file):
            if config.should_debug('verbose'):
                print(f"Transcript for {interview_name} already exists at {raw_transcript_file}")
        else : 
            if config.should_debug('verbose'):
                print(f"Transcribing {interview_name}...")
            transcript = process_interview_transcript(
                audio_file,
                language_code=config.get_config('language_id'),
                word_boost=config.word_boost
            )
            with open(raw_transcript_file, "w", encoding="utf-8") as f:
                f.write(transcript)
                
            if config.should_debug('print_transcripts'):
                print(f"\nTranscript for {interview_name}:")
                print(transcript)
    
    # Step 2: Analyze transcript if requested
    if do_analyze_audio_transcript:
        if not os.path.exists(raw_transcript_file):
            print(f"Error: Cannot analyze {interview_name} - raw transcript not found at {raw_transcript_file}")
            return
            
        print(f"Analyzing {interview_name}...")
        results = analyze_transcript_with_questions(
            transcript_path=raw_transcript_file,
            questions=questions,
            output_path=structured_transcript_file,
            llm_context=config.get_config('llm_context_instructions', {})
        )
        
        if config.should_debug('print_analysis'):
            print(f"\nAnalysis results for {interview_name}:")
            print(results)

def process_interview_directory(
    questions: List[Tuple[str, str]],
    do_transcribe_audio: bool = False,
    do_analyze_audio_transcript: bool = False
) -> None:
    """
    Process all audio interviews in a directory
    
    Args:
        questions: List of (question_id, question_text) tuples
        do_transcribe_audio: Whether to perform transcription step
        do_analyze_audio_transcript: Whether to perform analysis step
    """
    # Get audio directory
    audio_dir = config.get_path('audio_dir')
    
    # Get all audio files
    audio_extensions = {'.m4a', '.mp3', '.wav', '.aac'}
    audio_files = [
        os.path.join(audio_dir, f) 
        for f in os.listdir(audio_dir) 
        if os.path.splitext(f)[1].lower() in audio_extensions
    ]
    
    if config.should_debug('verbose'):
        print(f"\nFound {len(audio_files)} audio files in {audio_dir}:")
        for f in audio_files:
            print(f"  - {os.path.basename(f)}")
    else:
        print(f"Found {len(audio_files)} audio files to process")
    
    # Process each audio file
    for audio_file in audio_files:
        try:
            process_interview(
                audio_file=audio_file,
                questions=questions,
                do_transcribe_audio=do_transcribe_audio,
                do_analyze_audio_transcript=do_analyze_audio_transcript
            )
        except Exception as e:
            print(f"Error processing {audio_file}: {str(e)}")
            if config.should_debug('verbose'):
                import traceback
                print(traceback.format_exc())

def main(
    root_dir: str = "data",
    do_transcribe_audio: bool = False,
    do_analyze_audio_transcript: bool = False,
    do_make_transcript_report: bool = False,
    do_make_reviewed_transcript_analysis: bool = False
) -> None:
    """
    Main function to process interviews
    
    Args:
        root_dir: Root directory containing all project files
        do_transcribe_audio: Whether to perform transcription step
        do_analyze_audio_transcript: Whether to perform analysis step
        do_make_transcript_report: Whether to perform transcript report generation step
        do_make_reviewed_transcript_analysis: Whether to perform reviewed transcript analysis step
    """
    try:
        # Initialize configuration
        config.initialize(root_dir)
        if config.should_debug('verbose'):
            print(f"Initialized configuration:")
            print(f"  Root directory: {config.root_dir}")
            print(f"  Language: {config.language}")
            print(f"  Word boost terms: {len(config.word_boost)}")
        
        
        # Parse questions (only needed for analysis)
        questions = parse_questions(config.get_path('question_file'))
        if config.should_debug('verbose'):
            print(f"\n{len(questions)} questions parsed")
            if config.should_debug('print_questions'):
                for qid, text in questions:
                    print(f"{qid}: {text}")
    
        # Process all interviews in the audio directory
        if do_transcribe_audio or do_analyze_audio_transcript:  
            process_interview_directory(
                questions=questions,
                do_transcribe_audio=do_transcribe_audio,
                do_analyze_audio_transcript=do_analyze_audio_transcript
        )
            
    except (ValueError, FileNotFoundError, RuntimeError) as e:
        print(f"Error: {str(e)}")
        if config.should_debug('verbose'):
            import traceback
            print(traceback.format_exc())
        return

if __name__ == "__main__":
    import argparse
    import os
    from typing import List, Tuple
    
    parser = argparse.ArgumentParser(description='Process interview audio files')
    parser.add_argument('--root-dir', default="data/etude_chatbot",
                      help='Root directory containing all project files')
    parser.add_argument('--transcribe-audio', action='store_true',
                      help='Perform audio transcription step')
    parser.add_argument('--analyze-audio-transcript', action='store_true',
                      help='Perform audio transcript analysis step'),
    parser.add_argument('--make-transcript-report', action='store_true',
                      help='Perform audio transcript report generation step'),
    parser.add_argument('--make-reviewed-transcript-analysis', action='store_true',
                      help='Perform audio transcript review and analysis step'),
    
    args = parser.parse_args()
    
    main(
        root_dir=args.root_dir,
        do_transcribe_audio=args.transcribe_audio,
        do_analyze_audio_transcript=args.analyze_audio_transcript,
        do_make_transcript_report=args.make_transcript_report,
        do_make_reviewed_transcript_analysis=args.make_reviewed_transcript_analysis
    )
