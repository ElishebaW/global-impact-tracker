"""Core tracking logic for orchestration insights."""


import os
import csv
import time
from datetime import datetime
from pathlib import Path

class GlobalImpactTracker:
    def __init__(self):
        # Creates a hidden folder in your home directory to store the global log
        self.log_dir = Path.home() / ".impact_tracker"
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / "global_productivity.csv"
        self._ensure_log_exists()

    def _ensure_log_exists(self):
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Project", "Task", "Human_Baseline_Hrs", "AI_Sec", "Status"])

    def log_impact(self, project, task, baseline_hrs, status="Success"):
        # Logic to record the 'win'
        timestamp = datetime.now().strftime("%Y-%m-%d")
        # Record start time for AI execution
        start = time.time()
        # [Placeholder for your orchestration call]
        ai_duration = round(time.time() - start, 2)

        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, project, task, baseline_hrs, ai_duration, status])
            
    def get_total_savings(self):
        # A quick function to calculate your career-wide time saved
        total_hrs = 0
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_hrs += float(row['Human_Baseline_Hrs'])
        return total_hrs
