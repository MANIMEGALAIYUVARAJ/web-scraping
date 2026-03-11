import os
import psutil

def kill_chrome():
    print("Force closing all Chrome instances...")
    count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'chrome' in proc.info['name'].lower():
                proc.kill()
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    print(f"Terminated {count} Chrome processes.")

if __name__ == "__main__":
    kill_chrome()
