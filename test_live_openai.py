import os
import sys
from langchain_openai import ChatOpenAI

def test_key():
    print("=" * 60)
    print("TESTING OPENAI API KEY CONNECTION")
    print("=" * 60)
    
    # Load .env manually if present
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

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)
        
    print(f"Found API key: {api_key[:8]}...{api_key[-8:] if len(api_key) > 16 else ''}")
    
    try:
        print("Initializing ChatOpenAI and sending test prompt...")
        # Use a lightweight model for cost/speed
        llm = ChatOpenAI(api_key=api_key, model="gpt-4o-mini", temperature=0)
        response = llm.invoke("Confirm connection by responding with the single word: Success!")
        print(f"Response from OpenAI: '{response.content.strip()}'")
        print("\n[+] VERIFICATION RESULT: The OpenAI API Key is valid and working!")
    except Exception as e:
        print(f"\n[-] VERIFICATION RESULT: Connection failed!")
        print(f"Error Details: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_key()
