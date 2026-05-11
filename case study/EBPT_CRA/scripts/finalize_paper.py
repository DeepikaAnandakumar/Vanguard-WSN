
import os

BASE_DIR = r"C:\Users\Lenovo\.gemini\antigravity\brain\697f895a-a081-4974-9806-42bcd0398685"
PAPER_DIR = os.path.join(BASE_DIR, "submission_paper")
PART1 = os.path.join(PAPER_DIR, "Vanguard_WSN_part1.md")
PART2 = os.path.join(PAPER_DIR, "Vanguard_WSN_part2.md")
FINAL = os.path.join(PAPER_DIR, "Vanguard_WSN_IEEE_Paper.md")

def finalize():
    print("Reading Part 1...")
    with open(PART1, 'r', encoding='utf-8') as f:
        p1 = f.read()
        
    print("Reading Part 2...")
    with open(PART2, 'r', encoding='utf-8') as f:
        p2 = f.read()
        
    full_text = p1 + "\n" + p2
    
    # Fix links
    # Old: ![System Model](/system_model.mermaid)
    # New: ![System Model](paper_assets/system_model.png)
    # Note: Regex or simple replace if exact match
    full_text = full_text.replace("![System Model](/system_model.mermaid)", "![System Model](paper_assets/system_model.png)")
    
    print(f"Writing to {FINAL}...")
    with open(FINAL, 'w', encoding='utf-8') as f:
        f.write(full_text)
        
    print("Done.")

if __name__ == "__main__":
    finalize()
