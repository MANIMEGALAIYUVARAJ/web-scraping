import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

try:
    from driver_utils import install_configured_driver
    print("Successfully imported driver_utils")
    
    print("Attempting to install 'latest'...")
    path = install_configured_driver("latest")
    print(f"Latest installed at: {path}")
    
    # Test one of the specific high versions requested to see if it exists
    print("Attempting to install 'stable' (145.0.7632.26)...")
    path = install_configured_driver("stable")
    print(f"Stable installed at: {path}")

except Exception as e:
    print(f"Error: {e}")
    import helpers
    import traceback
    traceback.print_exc()
