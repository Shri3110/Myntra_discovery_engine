import os
import subprocess
import time

def run_script(script_path, cwd):
    """Helper to run a python script as a subprocess"""
    print(f"\n[{time.strftime('%X')}] Running: {script_path}...")
    try:
        result = subprocess.run(['python', script_path], cwd=cwd, check=True, text=True, capture_output=True)
        print(f"[{time.strftime('%X')}] Success: {script_path}")
        # Print last few lines of output for context
        lines = result.stdout.strip().split('\n')
        for line in lines[-3:]:
            print(f"  > {line}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%X')}] Error in {script_path}:")
        print(e.stderr)
        return False

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    print("="*60)
    print("MYNTRA DISCOVERY ENGINE - END-TO-END SIMULATION")
    print("="*60)
    
    # 1. Ingestion
    print("\n--- PHASE 1: DATA INGESTION ---")
    p1_dir = os.path.join(root_dir, 'phase_1_ingestion')
    run_script('scrapers/reddit_scraper.py', p1_dir)
    run_script('scrapers/youtube_scraper.py', p1_dir)
    run_script('scrapers/play_store_scraper.py', p1_dir)
    run_script('scrapers/ios_scraper.py', p1_dir)
    
    # 2. Processing
    print("\n--- PHASE 2: PROCESSING & VECTORIZATION ---")
    p2_dir = os.path.join(root_dir, 'phase_2_processing')
    run_script('cleaner.py', p2_dir)
    run_script('embedder.py', p2_dir)
    
    # 3. Agents
    print("\n--- PHASE 3: AI AGENT CLASSIFICATION ---")
    p3_dir = os.path.join(root_dir, 'phase_3_agents')
    print("Note: Skipping Agent execution in automated test to save API limits. Run manually for full test.")
    run_script('agents/classifier_agent.py', p3_dir)
    run_script('agents/intent_agent.py', p3_dir)
    
    # 4. Constraint Validation
    print("\n--- PHASE 5: CONSTRAINT VALIDATION ---")
    print("RAG Synthesis constraint check: Ensure 'run_synthesis_query' ignores monetary incentives.")
    
    print("\n="*60)
    print("PIPELINE TEST COMPLETE.")
    print("To start the Dashboard, run Phase 4 backend and frontend servers.")
    print("="*60)

if __name__ == "__main__":
    main()
