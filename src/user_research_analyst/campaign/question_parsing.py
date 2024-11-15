import re
from typing import List, Tuple

def parse_questions(file_path: str) -> List[Tuple[str, str]]:
    """
    Parse le fichier de questions et retourne une liste de tuples (id, question)
    
    Args:
        file_path: Chemin vers le fichier questions.txt
    
    Returns:
        List[Tuple[str, str]]: Liste de tuples (id, question)
    """
    questions = []
    current_id = ""
    current_question = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Check if line starts with question ID (e.g., "A10-", "B20-", etc.)
            id_match = re.match(r'^([A-Z]\d{2})-\s*(.*)', line)
            
            if id_match:
                # If we have a previous question stored, add it to the list
                if current_id and current_question:
                    questions.append((current_id, ' '.join(current_question)))
                
                # Start new question
                current_id = id_match.group(1)
                current_question = [id_match.group(2)]
            
            # If line starts with bullet point or is continuation of question
            elif line.startswith('•'):
                if current_question:
                    current_question.append(line.strip('•').strip())
            elif current_question:
                current_question.append(line)
    
    # Add the last question
    if current_id and current_question:
        questions.append((current_id, ' '.join(current_question)))
    
    return questions


