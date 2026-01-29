from pathlib import Path
import os
from dotenv import load_dotenv

# Simulate settings.py logic (running from root, so 1 parent less?)
# settings.py is in paddy/settings.py (depth 2). Root is depth 0.
# If this script is in root:
BASE_DIR = Path(__file__).resolve().parent
print(f"Script Context: {BASE_DIR}")

env_path = BASE_DIR / '.env'
print(f"Target Env Path: {env_path}")
print(f"File Exists: {env_path.exists()}")

# Read raw content to check encoding/format
if env_path.exists():
    try:
        content = env_path.read_text(encoding='utf-8')
        print(f"Raw Content (first 50 chars): {content[:50]}")
    except Exception as e:
        print(f"Error reading file: {e}")

# Try loading
print("Loading dotenv...")
loaded = load_dotenv(env_path, override=True)
print(f"Load_dotenv returned: {loaded}")

print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"DEBUG: {os.getenv('DEBUG')}")
