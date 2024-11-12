import assemblyai as aai
import os
from typing import List, Optional

# get keys from .env


# Initialize AssemblyAI with your API key
aai.settings.api_key = os.environ.get("ASSEMBLYAI_API_KEY")

def process_interview_transcript(
    audio_file_path: str
) -> str:
    """
    Process the interview audio using AssemblyAI with speaker diarization
    
    Args:
        audio_file_path: Path to the audio file
        question_context: Optional list of expected questions
    """
    # Configure transcription with speaker diarization
    # define speaker numbers
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        speakers_expected=2,
        language_code="fr",
        word_boost=["Chatbot", "technologie d’assistance", "technos d’assistance", "JAWS", "NVDA", "VoiceOver", "TalkBack", "Dragon", "BRLTTY", "System Access", "ZoomText", "Windows Magnifier", "MacOS Zoom", "Mac", "PC", "Windows", "Tobii Eye Tracker", "Tobii", "Speechify", "TextAloud", "SIRI", "Alexa", "Google Assistant", "Text-to-Speech", "Google", "OrCam", "MyEye", "eSight", "Zoom", "Google Meet", "Teams", "Skype", "Proloquo2Go", "Cortana", "Bixby", "Celia", "Robin", 
        ]
    )
    
    # Create transcriber and process file
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(
        audio_file_path,
        config=config
    )
    
    # Format the transcript with speaker labels
    formatted_transcript = []
    current_speaker = None
    
    for utterance in transcript.utterances:
        speaker = f"Speaker {utterance.speaker}"  # ou utilisez utterance.speaker_name si défini
        timestamp = f"[{utterance.start:.2f} - {utterance.end:.2f}]"
        
        if current_speaker != speaker:
            formatted_transcript.append(f"\n{speaker} {timestamp}:")
            current_speaker = speaker
            
        formatted_transcript.append(f"    {utterance.text}")
    
    return "\n".join(formatted_transcript)








