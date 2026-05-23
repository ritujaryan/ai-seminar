import os
import google.generativeai as genai

# Load env
_root_dir = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_root_dir, ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                k_str = key.strip()
                if k_str not in os.environ:
                    os.environ[k_str] = val.strip().strip('"').strip("'")

key = os.getenv("GEMINI_API_KEY")
print(f"API Key: {key[:8]}...")
genai.configure(api_key=key)
try:
    print("Listing models...")
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print("Error listing models:", e)
