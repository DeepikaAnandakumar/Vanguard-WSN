
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Path to the paper
PAPER_PATH = r"C:\Users\Lenovo\.gemini\antigravity\brain\697f895a-a081-4974-9806-42bcd0398685\submission_paper\Vanguard_WSN_IEEE_Paper.md"
OUTPUT_PDF = r"C:\Users\Lenovo\.gemini\antigravity\brain\697f895a-a081-4974-9806-42bcd0398685\submission_paper\Vanguard_WSN_IEEE_Paper.pdf"
ASSETS_DIR = r"c:\Users\Lenovo\OneDrive\Desktop\6TH SEM\case study\case study\EBPT_CRA\submission_paper\paper_assets" 
# Note: The assets were saved in C:/Users/Lenovo/OneDrive/Desktop/6TH SEM/case study/case study/EBPT_CRA/submission_paper/paper_assets by plot script
# But the paper markdown refers to `paper_assets/system_model.png`.
# I will resolve paths relative to the EBPT_CRA folder or absolute.

def generate_pdf():
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    if 'Title' not in styles:
        styles.add(ParagraphStyle(name='Title', parent=styles['Heading1'], fontSize=18, spaceAfter=12, alignment=1))
    else:
        styles['Title'].fontSize = 18
        styles['Title'].alignment = 1
        styles['Title'].spaceAfter = 12
    if 'Abstract' not in styles:
        styles.add(ParagraphStyle(name='Abstract', parent=styles['Normal'], fontSize=10, leftIndent=20, rightIndent=20, spaceAfter=20, fontName='Times-Italic'))
    
    if 'SectionHeader' not in styles:
        styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading2'], fontSize=12, spaceBefore=12, spaceAfter=6, fontName='Times-Bold'))
        
    if 'BodyText' not in styles:
        styles.add(ParagraphStyle(name='BodyText', parent=styles['Normal'], fontSize=10, spaceAfter=6, fontName='Times-Roman', leading=12))
    else:
        # Update existing BodyText if needed
        styles['BodyText'].fontSize = 10
        styles['BodyText'].spaceAfter = 6
        styles['BodyText'].fontName = 'Times-Roman'
        styles['BodyText'].leading = 12
    
    story = []
    
    with open(PAPER_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    in_code_block = False
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
            
        # Headers
        if line.startswith('# '):
            story.append(Paragraph(line[2:], styles['Title']))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['SectionHeader']))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], styles['Heading3']))
            
        # Images
        elif line.startswith('![') and '](' in line:
            # Format: ![Alt](path)
            match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if match:
                alt = match.group(1)
                img_path = match.group(2)
                # Resolve path
                # If relative "paper_assets/...", prepend the real dir
                if "paper_assets" in img_path:
                    base_name = os.path.basename(img_path)
                    real_path = os.path.join(ASSETS_DIR, base_name)
                else:
                    real_path = img_path
                
                if os.path.exists(real_path):
                    try:
                        img = Image(real_path)
                        # Resize if too big
                        aspect = img.imageHeight / float(img.imageWidth)
                        img.drawWidth = 5 * inch
                        img.drawHeight = 5 * inch * aspect
                        story.append(img)
                        story.append(Paragraph(f"Fig: {alt}", styles['BodyText']))
                    except Exception as e:
                        print(f"Could not load image {real_path}: {e}")
                else:
                    print(f"Image not found: {real_path}")
        
        # Tables (Simple detection)
        elif line.startswith('|'):
            # Convert markdown table to ReportLine table is complex, 
            # for now we render as monospace text or skip.
            # Simplified: Just render as code or text
            story.append(Paragraph(line, styles['BodyText'])) # Placeholder
            
        # Bold/Italic (Basic regex substitution for PDF tags)
        else:
            # Replace **text** with <b>text</b>
            # Replace *text* with <i>text</i>
            # Note: simplistic approach
            text = line
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            
            style = styles['BodyText']
            if line.startswith('**Abstract**'):
                style = styles['Abstract']
            
            story.append(Paragraph(text, style))
            
    try:
        doc.build(story)
        print(f"PDF generated: {OUTPUT_PDF}")
    except Exception as e:
        print(f"PDF Generation Error: {e}")

if __name__ == "__main__":
    generate_pdf()
