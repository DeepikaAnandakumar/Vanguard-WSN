import os
import shutil
import glob

def cleanup():
    target_dirs = [
        'results', 'results_*', 'master_results', 'master_results_*', 
        'adaptive', 'demo_results', 'final_results', 'paper_results', 
        'num_results', 'current_exact_results'
    ]
    
    target_files = [
        '*stats*', '*log*', '*analysis*', 'REPORT.md', 'DEMO_RESULTS_SUMMARY.html'
    ]
    
    base_path = r'c:\Users\Lenovo\OneDrive\Desktop\6TH SEM\case study\case study\EBPT_CRA'
    
    print("Purging directories...")
    for pattern in target_dirs:
        for path in glob.glob(os.path.join(base_path, pattern)):
            if os.path.isdir(path):
                print(f"Deleting dir: {path}")
                shutil.rmtree(path, ignore_errors=True)
                
    print("Purging files...")
    for pattern in target_files:
        for path in glob.glob(os.path.join(base_path, pattern)):
            if os.path.isfile(path):
                print(f"Deleting file: {path}")
                os.remove(path)

    # Move .md files to archive (except key ones)
    keep_files = ['README_reproduce.md', 'PROJECT_PRD.md', 'PAPER_FINAL_HONEST.md', 'task.md', 'implementation_plan.md', 'walkthrough.md', 'brutal_evaluation.md']
    archive_dir = os.path.join(base_path, 'archive')
    os.makedirs(archive_dir, exist_ok=True)
    
    for path in glob.glob(os.path.join(base_path, '*.md')):
        filename = os.path.basename(path)
        if filename not in keep_files:
            print(f"Archiving: {filename}")
            try:
                shutil.move(path, os.path.join(archive_dir, filename))
            except Exception as e:
                print(f"Error moving {filename}: {e}")

if __name__ == "__main__":
    cleanup()
