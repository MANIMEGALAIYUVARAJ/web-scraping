import shutil
import os
import glob

def check_space(path="C:\\"):
    total, used, free = shutil.disk_usage(path)
    print(f"Path: {path}")
    print(f"Total: {total // (2**30)} GB")
    print(f"Used: {used // (2**30)} GB")
    print(f"Free: {free // (2**30)} GB")
    return free

def clean_wdm_cache():
    cache_root = os.path.expanduser("~/.wdm")
    print(f"Cleaning cache at: {cache_root}")
    
    if not os.path.exists(cache_root):
        print("Cache directory does not exist.")
        return

    # Delete all files in drivers folder
    drivers_path = os.path.join(cache_root, "drivers")
    if os.path.exists(drivers_path):
        try:
             # Just listing sizes
             size = sum(os.path.getsize(f) for f in glob.glob(drivers_path + '/**/*', recursive=True) if os.path.isfile(f))
             print(f"Current Cache Size: {size / (1024*1024):.2f} MB")
             
             # Removal
             shutil.rmtree(drivers_path)
             print("Deleted .wdm/drivers directory.")
        except Exception as e:
            print(f"Error cleaning cache: {e}")
            
    # Re-create empty
    os.makedirs(drivers_path, exist_ok=True)

if __name__ == "__main__":
    print("--- Disk Check Before ---")
    check_space()
    
    print("\n--- Cleaning ---")
    clean_wdm_cache()
    
    print("\n--- Disk Check After ---")
    check_space()
