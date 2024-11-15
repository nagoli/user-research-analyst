import pandas as pd
from typing import Tuple
from data import InterviewDataset, Question, Interview
from segments import normalize_segments_in_interviewdataset, create_segment_dataset


def parse_excel_file(file_path: str) -> InterviewDataset:
    """
    Charge les données d'un fichier Excel dans la structure InterviewDataset
    
    Args:
        file_path: Chemin vers le fichier Excel
        
    Returns:
        InterviewDataset: Données structurées de l'interview
    """
    # Charger le fichier Excel
    df = pd.read_excel(file_path)
    
    # Extraire les questions depuis les en-têtes (toutes les colonnes sauf les 2 premières)
    questions = [
        Question(
            id=str(i+3),  # Numéro de colonne comme ID (commence à 3 car col1=nom, col2=segments)
            text=str(col_name),
            column_index=i+2
        )
        for i, col_name in enumerate(df.columns[2:])
    ]
    
    # Extraire les interviews (toutes les lignes car les interviews commencent à la ligne 0)
    interviews = []
    for _, row in df.iterrows():  # Supprimé le iloc[1:] pour commencer à la ligne 0
        # Extraire et nettoyer les segments
        segments_str = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
        segments = [s.strip() for s in segments_str.split(',') if s.strip()]
        
        # Créer le dictionnaire des réponses
        answers = {
            q.id: str(row.iloc[q.column_index]) 
            for q in questions
            if pd.notna(row.iloc[q.column_index])
        }
        
        interview = Interview(
            name=str(row.iloc[0]),
            segments=segments,
            answers=answers
        )
        interviews.append(interview)
    

    dataset = InterviewDataset(
        questions=questions,
        interviews=interviews
    )
    
    # Normalize segments if needed
    #dataset = normalize_segments_in_interviewdataset(dataset)   
    
    return dataset


# Exemple d'utilisation:
def test_excel_parsing():
    # Charger les données
    dataset = parse_excel_file("data/analysis_report_test.xlsx")
    
    # Exemple d'accès aux données
    print(f"Nombre d'interviews: {len(dataset.interviews)}")
    print(f"Nombre de questions: {len(dataset.questions)}")
    print(f"Nombre de segments: {len(dataset.segment_set)}")
    print(f"Segments: {dataset.segment_set}")
    
    # exemple de transformation de l’interviewdataset en segmentdataset
    segment_dataset = create_segment_dataset(dataset)
    print("\nTransformed into SegmentDataset:")
    print(f"Number of segments: {len(segment_dataset.segments)}")
    
    # Print example of answers for each segment
    for segment_name, questions in segment_dataset.segments.items():
        print(f"\nSegment: {segment_name}")
        for question_id, answer in questions.items():
            print(f"  Question {question_id}:")
            print(f"  Summary: {answer.answer_summary}")
            print(f"  Quote: {answer.quote}")
            print(f"  Number of answers: {len(answer.rough_answers)}")
        
if __name__ == "__main__":
    test_excel_parsing()    