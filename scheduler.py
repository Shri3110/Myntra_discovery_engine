import schedule
import time
import subprocess
import os

def run_pipeline():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting daily Myntra Discovery Engine pipeline (Target: ~255 reviews)...")
    
    # Run the pipeline script from phase 5 testing
    pipeline_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phase_5_testing')
    
    try:
        subprocess.run(["python", "run_pipeline.py"], cwd=pipeline_dir, check=True)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Daily pipeline completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error running daily pipeline: {e}")

if __name__ == "__main__":
    print("======================================================")
    print("  Myntra Discovery Engine - Daily Scheduler Daemon")
    print("======================================================")
    print(f"Scheduler started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("Configured to fetch ~255 live reviews every night at 00:00 (Midnight).")
    
    # Schedule to run every day at midnight
    schedule.every().day.at("00:00").do(run_pipeline)
    
    print("\nWaiting for the next scheduled run... (Press CTRL+C to quit)\n")
    
    # Keep the daemon alive
    while True:
        schedule.run_pending()
        time.sleep(60)
