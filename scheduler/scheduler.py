import schedule
import time
import subprocess

def scheduled_task():
    subprocess.run(["python", "runner.py"])  # Call runner.py to invoke the check_prices function

schedule.every().day.at("09:00").do(scheduled_task)  # Schedule the task to run every day at 09:00 AM

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)
