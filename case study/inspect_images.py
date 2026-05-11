from docx import Document

doc = Document('Vanguard.final (1).docx')

print("--- Document Structure Scan ---")
img_count = 0
for i, p in enumerate(doc.paragraphs):
    # Check for images (runs with drawings)
    has_image = False
    for r in p.runs:
        if 'drawing' in r._element.xml:
            img_count += 1
            has_image = True
    
    if has_image:
        print(f"Paragraph {i}: [IMAGE {img_count}]")
    
    if p.text.strip():
        # Print surrounding text to identify context
        text = p.text.strip()
        if len(text) > 50:
            text = text[:50] + "..."
        print(f"Paragraph {i}: {text}")
