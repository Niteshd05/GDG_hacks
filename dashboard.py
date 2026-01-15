"""
Simple progress logging - just percentages, errors, and success messages
"""

def log_event(message, icon="✓"):
    """Print a permanent log message"""
    print(f"{icon} {message}")

def update_progress(job_id, message, percent=0, icon="⚙️"):
    """Print progress update with percentage"""
    print(f"{icon} [{percent}%] {job_id}: {message}")

def complete_task(job_id, message):
    """Print completion message"""
    print(f"✅ {message}")

def error_task(job_id, message):
    """Print error message"""
    print(f"❌ {message}")
