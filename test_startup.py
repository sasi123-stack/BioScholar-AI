
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.api.dependencies import initialize_services
from src.utils.logger import logger

print("Starting service initialization test...")
try:
    initialize_services()
    print("Service initialization successful!")
except Exception as e:
    print(f"Service initialization failed: {e}")
    import traceback
    traceback.print_exc()
