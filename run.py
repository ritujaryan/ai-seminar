import uvicorn
import os
import sys

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting AI Seminar System server on http://localhost:{port}...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
