"""
Script to verify content preservation in formatted documents
Compares original text content against generated Word and LaTeX files
"""

import re
from docx import Document

def normalize_text(text):
    """Normalize text for comparison (remove extra whitespace, case insensitive)"""
    # Remove LaTeX commands for comparison
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'[{}]', '', text)
    # Remove common LaTeX junk
    text = text.replace('$', '').replace('\\', '')
    # Normalize whitespace
    return ' '.join(text.lower().split())

def read_docx(path):
    """Read text from docx file"""
    doc = Document(path)
    return '\n'.join([p.text for p in doc.paragraphs])

def read_file(path):
    """Read text from plain text or tex file"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def verify_documents():
    print("Starting verification...")
    
    # Read original content
    try:
        original_text = read_file('vanguard_content.txt')
        normalized_original = normalize_text(original_text)
        print(f"Original content length: {len(normalized_original)} chars")
    except Exception as e:
        print(f"Error reading original content: {e}")
        return

    # Verify Word Document
    try:
        word_text = read_docx('Vanguard_IEEE_Formatted.docx')
        normalized_word = normalize_text(word_text)
        print(f"Word doc content length: {len(normalized_word)} chars")
        
        # Simple containment check (approximate due to formatting chars)
        # We check if key phrases from original exist in new
        key_phrases = [
            "Vanguard-WSN: A Utility-Driven Energy-Balanced Path Tree Framework",
            "Deepika A, Aishvarya G, Gayatri K, Anjana A",
            "First Node Death (FND) occurs at Round 993.1",
            "Algorithm 1: Utility-Based CH Selection",
            "94% with the best LP-bound"
        ]
        
        failed = False
        for phrase in key_phrases:
            if normalize_text(phrase) not in normalized_word:
                print(f"❌ Missing in Word doc: {phrase}")
                failed = True
        
        if not failed:
            print("✓ Word document content verification passed (Key phrases check)")
            
    except Exception as e:
        print(f"Error verifying Word doc: {e}")

    # Verify LaTeX Document
    try:
        latex_text = read_file('Vanguard_IEEE_Formatted.tex')
        # Remove preamble to check body content
        body_start = latex_text.find(r'\begin{document}')
        if body_start != -1:
            latex_text = latex_text[body_start:]
            
        normalized_latex = normalize_text(latex_text)
        print(f"LaTeX doc content length: {len(normalized_latex)} chars")
        
        failed = False
        for phrase in key_phrases:
            if normalize_text(phrase) not in normalized_latex:
                print(f"❌ Missing in LaTeX doc: {phrase}")
                failed = True
                
        if not failed:
            print("✓ LaTeX document content verification passed (Key phrases check)")

    except Exception as e:
        print(f"Error verifying LaTeX doc: {e}")

if __name__ == "__main__":
    verify_documents()
